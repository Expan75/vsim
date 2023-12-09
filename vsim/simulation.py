import logging
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Optional
from vsim import common
from vsim.voting_system import VotingSystem, ElectionResult


@dataclass
class SimulationResult:
    weighted_fairness: float
    unweighted_fairness: float
    election_result: ElectionResult
    parameters: Optional[dict] = None


class VotingSimulator:
    """
    Represents a running simulation. Runs an election given
    the injected voting system strategy and population.
    """

    def __init__(
        self,
        electorate: np.ndarray,
        candidates: np.ndarray,
        system: VotingSystem,
        plot: bool = False,
        seed: Optional[int] = None,
        log: Optional[logging.Logger] = None,
        scenario: Optional[str] = None,
    ):
        # misc settings
        np.random.seed(seed)  # None means random without seed
        self.plot = plot
        self.log = log if log is not None else common.conf_logger(1, "vsim.log")

        # sim params
        self.scenario = scenario if scenario is None else "no scenario"
        self.voting_system: VotingSystem = system

        # simulation agents
        self.electorate: np.ndarray = electorate
        self.candidates: np.ndarray = candidates

    @property
    def n_candidates(self) -> int:
        return int(self.candidates.shape[0])

    @property
    def n_voters(self) -> int:
        return int(self.electorate.shape[0])

    @property
    def n_issues(self) -> int:
        return int(self.electorate.shape[1])

    def calculate_fairness(self, result: ElectionResult) -> float:
        """Fairness is defined as the inversed average distance to the winner(s)"""
        avg_distances = []
        for winner in result.winners:
            avg_dist_to_winner = np.mean(
                np.linalg.norm(self.candidates[winner] - self.electorate)
            )
            avg_distances.append(avg_dist_to_winner)

        return 1 / float(np.mean(avg_distances))

    def calculate_weighted_fairness(self, result: ElectionResult) -> float:
        """Like above but weighted by election share outcome"""
        avg_distances = {}
        for candidate in result.cast_votes:
            avg_dist_to_candidate = np.mean(
                np.linalg.norm(self.candidates[candidate] - self.electorate)
            )
            avg_distances[candidate] = avg_dist_to_candidate

        votes_total = sum(v for v in result.cast_votes.values())
        avg_distances_weights = [dist / votes_total for dist in avg_distances]
        avg_distances = np.array(list(avg_distances.values()))

        return 1 / float(np.average(avg_distances, weights=avg_distances_weights))

    def display(self, result: ElectionResult, fairness: float):
        """Renders an election"""
        self.log.debug("displaying")
        assert self.n_issues <= 2, "can only visualise 2D elections"
        _, ax = plt.subplots()

        columns = [f"issue_{i}" for i in range(1, self.n_issues + 1)]
        electorate_df = pd.DataFrame(self.electorate, columns=columns)
        electorate_df["state"] = "voter"

        # add candidates to same df to ease plotting
        candidate_df = pd.DataFrame(self.candidates, columns=columns)
        candidate_df["state"] = "candidate"
        df = pd.concat([electorate_df, candidate_df])

        sns.scatterplot(data=df, x="issue_1", y="issue_2", hue="state", ax=ax)
        ax.set_title(f"scenario={self.scenario}, {fairness=}")

        plt.show()

    def run(self):
        self.log.debug("running voting sim")
        result = self.voting_system.elect(self.electorate, self.candidates)
        simulation_result = {
            "election_result": result,
            "unweighted_fairness": self.calculate_fairness(result),
            "weighted_fairness": self.calculate_weighted_fairness(result),
            "parameters": {},
        }

        if self.plot:
            self.display(result, simulation_result["unweighted_fairness"])

        return SimulationResult(**simulation_result)


if __name__ == "__main__":
    pass
