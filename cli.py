import argparse
from datetime import datetime
from vsim import candidates, electorate, voting_system, common, simulation

# setup cli
parser = argparse.ArgumentParser("vsim", description="Voting simulator 0.0.1")
parser.add_argument("--issues", "-i", type=int, default=2)
parser.add_argument("--population", "-p", type=int, default=10_000)
parser.add_argument(
    "--voting-system",
    "-vs",
    choices=voting_system.SUPPORTED_VOTING_SYSTEMS.keys(),
    required=True,
)
parser.add_argument("--candidates", "-c", type=int, default=2)
parser.add_argument(
    "--candidate-scenario",
    "-cs",
    choices=candidates.CANDIDATE_OPTIONS.keys(),
    default="default",
)
parser.add_argument(
    "--electorate-scenario",
    "-es",
    choices=electorate.ELECTORATE_SCENARIOS.keys(),
)
parser.add_argument("--seed", "-s", type=int, default=None)
parser.add_argument("--log", "-l", type=str, default="DEBUG", required=False)
parser.add_argument("--debug", "-d", action="store_true", default=False)
parser.add_argument("--output-dir", "-o", type=str, default="")


def main():
    args = parser.parse_args()

    # setup logger
    filepath = f'logs/voting-sim-{datetime.now().strftime("%d-%m-%Y")}.log'
    log = common.conf_logger(args.log, filepath)

    system = voting_system.setup_voting_system(args.voting_system)
    voters = electorate.setup_electorate(
        electorate_size=args.population,
        issues=args.issues,
        scenario=args.electorate_scenario,
        seed=args.seed,
    )
    parties = candidates.setup_candidates(
        candidates=args.candidates,
        electorate=voters,
        scenario=args.candidate_scenario,
        seed=args.seed,
    )

    sim = simulation.VotingSimulator(
        system=system,
        electorate=voters,
        candidates=parties,
        seed=args.seed,
        plot=args.debug,
        scenario=args.electorate_scenario,
        log=log,
    )
    result = sim.run()
    print(result)


if __name__ == "__main__":
    main()
