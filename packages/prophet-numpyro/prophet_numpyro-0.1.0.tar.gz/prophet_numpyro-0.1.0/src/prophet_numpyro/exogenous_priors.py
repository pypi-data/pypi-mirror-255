import re
from typing import Dict, List, Tuple

import numpyro
import numpyro.distributions as dist
import pandas as pd
from jax import numpy as jnp
from jax import random


def get_exogenous_priors(
    X: pd.DataFrame,
    exogenous_priors: Dict[str, Tuple[dist.Distribution, ...]],
    default_exogenous_prior=None,
) -> Tuple[Tuple[str, dist.Distribution], jnp.ndarray]:
    """
    Get the exogenous priors for each column in the input DataFrame.

    Parameters:
        X (pd.DataFrame): The input DataFrame.
        exogenous_priors (Dict[str, Tuple[dist.Distribution, ...]]): A dictionary mapping regular expressions to tuples of distributions and their arguments.

    Returns:
        Tuple[dist.Distribution, jnp.ndarray]: A tuple containing the exogenous distributions and the permutation matrix.
    """
    exogenous_dists = []

    exogenous_permutation_matrix = []
    remaining_columns_regex = check_regexes_and_return_remaining_regex(
        exogenous_priors, X
    )

    exogenous_priors = exogenous_priors.copy()

    if remaining_columns_regex:
        exogenous_priors[remaining_columns_regex] = default_exogenous_prior

    for i, (regex, (Distribution, *args)) in enumerate(exogenous_priors.items()):
        # Find columns that match the regex
        columns = [column for column in X.columns if re.match(regex, column)]
        # Get idx of columns that match the regex
        idx = jnp.array([X.columns.get_loc(column) for column in columns])
        # Set the distribution for each column that matches the regex
        distribution: dist.Distribution = Distribution(
            *[jnp.ones(len(idx)) * arg for arg in args]
        )

        name = "exogenous_coefficients_{}".format(i)

        # Matrix of shape (len(columns), len(idx) that map len(idx) to the corresponding indexes
        exogenous_permutation_matrix.append(jnp.eye(len(X.columns))[idx].T)
        exogenous_dists.append((name, distribution))

    exogenous_permutation_matrix = jnp.concatenate(exogenous_permutation_matrix, axis=1)

    return exogenous_dists, exogenous_permutation_matrix


def sample_exogenous_coefficients(exogenous_dists, exogenous_permutation_matrix):

    parameters = []
    for regex, distribution in exogenous_dists:
        parameters.append(
            numpyro.sample(
                "exogenous_coefficients_{}".format(regex), distribution
            ).reshape((-1, 1))
        )

    return exogenous_permutation_matrix @ jnp.concatenate(parameters, axis=0)


def check_regexes_and_return_remaining_regex(
    exogenous_priors: List[Tuple], X: pd.DataFrame
) -> str:
    already_set_columns = set()
    for regex, _ in exogenous_priors.items():
        columns = [column for column in X.columns if re.match(regex, column)]
        if already_set_columns.intersection(columns):
            raise ValueError(
                "Columns {} are already set".format(
                    already_set_columns.intersection(columns)
                )
            )
        already_set_columns = already_set_columns.union(columns)
    remaining_columns = X.columns.difference(already_set_columns)

    # Create a regex that matches all remaining columns
    remaining_regex = "|".join(remaining_columns)
    return remaining_regex
