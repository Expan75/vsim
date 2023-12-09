"""
This module contains strategy classes that implement different voting systems

To add a new voting system, subclass the VotingSystem abstract base calss and be sure to implement the 'elect' method. Have a look at one of the current implementations for help!
"""
import random
import operator
import numpy as np
from abc import ABC, abstractmethod
from typing import List, Set, Dict
from dataclasses import dataclass
from scipy.spatial import KDTree


@dataclass
class ElectionResult:
    winners: Set[int]
    cast_votes: dict


def allocate_votes(
    electorate: np.ndarray,
    candidates: np.ndarray,
    votes: int = 1,
    apathy_prob: float = 0.0,
) -> Dict[int, int]:
    """Allocates votes from electorate to candidates nearest neighbour(s)"""
    n_voters, _ = electorate.shape
    n_candidates, _ = candidates.shape
    counted_votes = np.zeros(n_candidates)

    # build tree for efficient NN lookup
    kd_tree = KDTree(candidates)
    _, closest_candidates = kd_tree.query(electorate, k=votes)

    for i in range(n_voters):
        voter_apathetic = np.random.rand() < apathy_prob
        if voter_apathetic:
            continue
        else:
            counted_votes[closest_candidates[i]] += 1

    return dict(enumerate(counted_votes))


class VotingSystem(ABC):
    """Strategy for running simulator, akin to given system of voting"""

    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def elect(self, electorate: np.ndarray, candidates: np.ndarray) -> ElectionResult:
        pass


class Plurality(VotingSystem):
    def __init__(self, apathy_prob: float = 0.0, *args, **kwargs):
        self.apathy_prob = apathy_prob

    def elect(self, electorate: np.ndarray, candidates: np.ndarray) -> ElectionResult:
        """Elect a single winner by plurality (whoever gets the most votes)"""
        electoral_vote_count = allocate_votes(
            electorate, candidates, votes=1, apathy_prob=self.apathy_prob
        )
        winner_idx, _ = max(electoral_vote_count.items(), key=operator.itemgetter(1))
        winners: Set[int] = {winner_idx}
        result = ElectionResult(cast_votes=electoral_vote_count, winners=winners)

        return result


class Majority(VotingSystem):
    def __init__(
        self,
        apathy_prob: float = 0.0,
        share_threshold: float = 0.5,
        round_knockouts: int = 1,
        *args,
        **kwargs,
    ):
        self.apathy_prob = apathy_prob
        self.threshold = share_threshold
        self.knockouts = round_knockouts

    def elect_rec(
        self, electorate: np.ndarray, candidates: np.ndarray, prior_results=[]
    ) -> List[ElectionResult]:
        """Keeps knocking out candidates until one passes share threshold"""

        voters, _ = electorate.shape
        electoral_vote_count = allocate_votes(electorate, candidates, votes=1)

        # check winner share and terminate if above threshold
        winner_idx, _ = max(electoral_vote_count.items(), key=operator.itemgetter(1))
        winner_share = electoral_vote_count[winner_idx] / voters
        above_threshold = winner_share > self.threshold

        result = ElectionResult({winner_idx}, cast_votes=electoral_vote_count)
        results = [*prior_results, result]

        if above_threshold:
            return results
        else:
            # cull k worst, TODO: fix so we don't throw away original indices here!
            worst_performers = [
                i
                for i, _ in sorted(
                    [(c, v) for c, v in electoral_vote_count.items()],
                    key=operator.itemgetter(1),
                    reverse=True,
                )
            ]

            # catch situation where we knock out more than remains
            knockouts_to_apply = self.knockouts
            candidates_remaining = len(electoral_vote_count.keys()) - knockouts_to_apply
            while candidates_remaining < 2:
                candidates_remaining = (
                    len(electoral_vote_count.keys()) - knockouts_to_apply
                )
                knockouts_to_apply -= 1

            knocked_out = worst_performers[:knockouts_to_apply]
            next_round_candidates = np.delete(candidates, knocked_out, axis=0)

            return self.elect_rec(electorate, next_round_candidates, results)

    def elect(self, electorate: np.ndarray, candidates: np.ndarray) -> ElectionResult:
        results: List[ElectionResult] = self.elect_rec(electorate, candidates)
        return results[-1]


class ApprovalVoting(VotingSystem):
    def __init__(
        self, apathy_prob: float = 0.0, n_approvals_per_voter: int = 2, *args, **kwargs
    ):
        self.apathy_prob = apathy_prob
        self.n_approvals_per_voter = n_approvals_per_voter

    def elect(self, electorate: np.ndarray, candidates: np.ndarray) -> ElectionResult:
        n_candidates, _ = candidates.shape
        assert self.n_approvals_per_voter <= n_candidates, "more votes than candidates"
        electoral_vote_count = allocate_votes(
            electorate,
            candidates,
            votes=self.n_approvals_per_voter,
            apathy_prob=self.apathy_prob,
        )

        winner_idx, _ = max(electoral_vote_count.items(), key=operator.itemgetter(1))
        winners: Set[int] = {winner_idx}
        result = ElectionResult(cast_votes=electoral_vote_count, winners=winners)

        return result


class ProportionalRepresentation(VotingSystem):
    """
    Implements a proportional representation system, which is typically found in
    most parliament elections (Sweden etc.).
    """

    def __init__(
        self,
        apathy_prob: float = 0.0,
        seats_to_allocate: int = 349,
        min_share_threshold: float = 0.04,
        *args,
        **kwargs,
    ):
        self.seats: int = seats_to_allocate
        self.threshold: float = min_share_threshold
        self.apathy_prob: float = apathy_prob

    def elect(self, electorate: np.ndarray, candidates: np.ndarray) -> ElectionResult:
        voters, _ = electorate.shape
        electoral_vote_count = allocate_votes(electorate, candidates)
        candidate_votes_under_threshold = {
            c: v
            for c, v in electoral_vote_count.items()
            if (v / voters) < self.threshold
        }

        remaining_votes = voters - sum(candidate_votes_under_threshold.values())
        allocated_seats = {
            c: round((v / remaining_votes) * self.seats)
            for c, v in electoral_vote_count.items()
            if c not in candidate_votes_under_threshold
        }

        # handle off by one, or further underallocation
        seats_allocated = sum(allocated_seats.values())

        while seats_allocated < self.seats:
            cand = random.choice(list(allocated_seats.keys()))
            allocated_seats[cand] += 1
            seats_allocated += 1

        # loosely defined here, but just seen as candidate with highest seat count
        winner = max(allocated_seats, key=lambda c: allocated_seats[c])
        return ElectionResult(winners={winner}, cast_votes=allocated_seats)


# constant of what systems are supported currently
SUPPORTED_VOTING_SYSTEMS = {
    "plurality": Plurality,
    "majority": Majority,
    "approval": ApprovalVoting,
    "proportional": ProportionalRepresentation,
}


def setup_voting_system(name: str, *args, **kwargs) -> VotingSystem:
    """Helper for setting up the correct voting system"""
    return SUPPORTED_VOTING_SYSTEMS[name](*args, **kwargs)


if __name__ == "__main__":
    pass
