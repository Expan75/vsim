"""
Module for generating different kinds of electorate, represented
as a (n_individuals, n_issues) matrix.
"""
import numpy as np
from functools import partial
from sklearn.datasets import make_blobs
from typing import Dict, Callable, Optional, Union


def generate_polarized_electorate(
    electorate_size: int,
    issues: int,
    clusters: int,
    seed: Optional[int] = None,
    cluster_std: Union[int, float] = 1,
) -> np.ndarray:
    """Generates a voter base which is polarized, i.e. split in distinct clusters"""
    return np.array(
        make_blobs(
            n_samples=electorate_size,
            n_features=issues,
            centers=clusters,
            random_state=seed,
            cluster_std=cluster_std,
        )[0]
    )


# shorthand for running certain parameter scenarios
ELECTORATE_SCENARIOS: Dict[str, Callable] = {
    "centered": partial(generate_polarized_electorate, clusters=1),
    "bipolar": partial(generate_polarized_electorate, clusters=2),
    "tripolar": partial(generate_polarized_electorate, clusters=3),
}


def normalize(v: np.ndarray) -> np.ndarray:
    """Needs to happen for our distance metric to be comparable across systems"""
    return v / (np.linalg.norm(v) + 1e-16)


def setup_electorate(
    electorate_size,
    issues,
    cluster_std: Union[float, int] = 1,
    clusters: Optional[int] = None,
    scenario: Optional[str] = None,
    seed: Optional[int] = None,
    *args,
    **kwargs
) -> np.ndarray:
    if scenario is not None:
        return normalize(
            ELECTORATE_SCENARIOS[scenario](
                electorate_size=electorate_size,
                issues=issues,
                seed=seed,
                cluster_std=cluster_std,
            )
        )
    else:
        assert clusters is not None
        assert cluster_std is not None
        return normalize(
            generate_polarized_electorate(
                electorate_size=electorate_size,
                issues=issues,
                clusters=clusters,
                cluster_std=cluster_std,
                seed=seed,
            )
        )


if __name__ == "__main__":
    pass
