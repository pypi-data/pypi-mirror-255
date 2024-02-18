import itertools
import logging
import re
from functools import partial
from typing import Dict, List, Tuple

import jax
import jax.numpy as jnp
import numpy as np
import numpyro
import pandas as pd
from jax import lax, random
from numpyro import distributions as dist
from numpyro.infer import MCMC, NUTS, Predictive
from sktime.forecasting.base import BaseForecaster, ForecastingHorizon
from sktime.transformations.hierarchical.aggregate import Aggregator
from sktime.transformations.hierarchical.reconcile import _get_s_matrix

from prophet_numpyro.base import BaseBayesianForecaster
from prophet_numpyro.exogenous_priors import (get_exogenous_priors,
                                              sample_exogenous_coefficients)
from prophet_numpyro.hierarchical_prophet._distribution import NormalReconciled
from prophet_numpyro.hierarchical_prophet._transformations import (
    ChangepointMatrix, ExogenousDataFrameToMatrixTransformer, TimeScaler)
from prophet_numpyro.hierarchical_prophet._utils import (
    convert_dataframe_to_tensors, convert_index_to_days_since_epoch,
    loc_bottom_series, series_to_tensor)
from prophet_numpyro.prophet.jax_functions import (additive_mean_model,
                                                   get_logistic_trend,
                                                   get_piecewise_linear_trend,
                                                   multiplicative_mean_model)

logger = logging.getLogger("sktime-numpyro")

NANOSECONDS_TO_SECONDS = 1000 * 1000 * 1000


class Prophet2(BaseBayesianForecaster):
    """Prophet2 forecaster.

    Parameters:
    ----------
    changepoint_freq : int, default=25
        Frequency of potential changepoints in the time series.
    exogenous_priors : dict, default={}
        Dictionary of prior distributions for exogenous variables.
    default_exogenous_prior : Distribution, default=dist.Normal(0, 1)
        Default prior distribution for exogenous variables.
    changepoint_prior_scale : float or list of floats, default=None
        Prior scale for changepoint distribution. If a list is provided, it should have the same length as the number of series.
    capacity_prior_scale : float, default=None
        Prior scale for capacity distribution.
    capacity_prior_loc : float, default=1
        Prior location for capacity distribution.
    noise_scale : float, default=1
        Scale parameter for the observation noise.
    trend : str, default="linear"
        Type of trend. Options are "linear" or "logistic".
    seasonality_mode : str, default="multiplicative"
        Mode of seasonality. Options are "additive" or "multiplicative".
    individual_regressors : list, default=[]
        List of column names of individual regressors.
    mcmc_samples : int, default=2000
        Number of MCMC samples.
    mcmc_warmup : int, default=200
        Number of MCMC warmup steps.
    mcmc_chains : int, default=4
        Number of MCMC chains.
    rng_key : jax.random.PRNGKey, default=random.PRNGKey(24)
        Random number generator key.

    Attributes:
    ----------
    n_series : int
        Number of time series.
    _time_scaler : TimeScaler
        Time scaler object.
    _changepoint_matrix_maker : ChangepointMatrix
        Changepoint matrix maker object.
    _linear_global_rates : ndarray
        Global rates for linear trend.
    _linear_initial_offsets : ndarray
        Initial offsets for linear trend.
    _changepoint_prior_loc_vector : ndarray
        Prior location vector for changepoint distribution.
    _changepoint_prior_scale_vector : ndarray
        Prior scale vector for changepoint distribution.
    _exogenous_matrix_maker : ExogenousDataFrameToMatrixTransformer
        Exogenous matrix maker object.
    _exogenous_coefficients : ndarray
        Coefficients for exogenous variables.
    _changepoint_coefficients : ndarray
        Coefficients for changepoints.
    _linear_offset_param : ndarray
        Offset parameter for linear trend.
    _capacity : ndarray
        Capacity parameter for logistic trend.
    """

    _tags = {
        "scitype:y": "univariate",  # which y are fine? univariate/multivariate/both
        "ignores-exogeneous-X": False,  # does estimator ignore the exogeneous X?
        "handles-missing-data": False,  # can estimator handle missing data?
        "y_inner_mtype": [
            "pd.Series",
            "pd_multiindex_hier",
            "pd-multiindex",
        ],
        "X_inner_mtype": [
            "pd_multiindex_hier",
            "pd-multiindex",
        ],  # which types do _fit, _predict, assume for X?
        "requires-fh-in-fit": False,  # is forecasting horizon already required in fit?
        "X-y-must-have-same-index": False,  # can estimator handle different X/y index?
        "enforce_index_type": None,  # index type that needs to be enforced in X/y
        "capability:pred_int": False,  # does forecaster implement proba forecasts?
        "fit_is_empty": False,
        "capability:pred_int": True,
        "capability:pred_int:insample": True,
    }

    def __init__(
        self,
        changepoint_freq=25,
        exogenous_priors={},
        default_exogenous_prior=(dist.Normal, 0, 1),
        changepoint_prior_scale=0.1,
        capacity_prior_scale=1,
        capacity_prior_loc=1,
        noise_scale=1,
        trend="linear",
        seasonality_mode="multiplicative",
        individual_regressors=[],
        mcmc_samples=2000,
        mcmc_warmup=200,
        mcmc_chains=4,
        rng_key=random.PRNGKey(24),
    ):
        """
        Initialize the Prophet2 forecaster.

        Parameters:
        ----------
        changepoint_freq : int, default=25
            Frequency of potential changepoints in the time series.
        exogenous_priors : dict, default={}
            Dictionary of prior distributions for exogenous variables.
        default_exogenous_prior : Distribution, default=dist.Normal(0, 1)
            Default prior distribution for exogenous variables.
        changepoint_prior_scale : float or list of floats, default=None
            Prior scale for changepoint distribution. If a list is provided, it should have the same length as the number of series.
        capacity_prior_scale : float, default=None
            Prior scale for capacity distribution.
        capacity_prior_loc : float, default=1
            Prior location for capacity distribution.
        noise_scale : float, default=1
            Scale parameter for the observation noise.
        trend : str, default="linear"
            Type of trend. Options are "linear" or "logistic".
        seasonality_mode : str, default="multiplicative"
            Mode of seasonality. Options are "additive" or "multiplicative".
        individual_regressors : list, default=[]
            List of column names of individual regressors.
        mcmc_samples : int, default=2000
            Number of MCMC samples.
        mcmc_warmup : int, default=200
            Number of MCMC warmup steps.
        mcmc_chains : int, default=4
            Number of MCMC chains.
        rng_key : jax.random.PRNGKey, default=random.PRNGKey(24)
            Random number generator key.
        """
        self.changepoint_freq = changepoint_freq
        self.changepoint_prior_scale = changepoint_prior_scale
        self.noise_scale = noise_scale
        self.capacity_prior_scale = capacity_prior_scale
        self.capacity_prior_loc = capacity_prior_loc
        self.seasonality_mode = seasonality_mode
        self.trend = trend
        self.exogenous_priors = exogenous_priors
        self.default_exogenous_prior = default_exogenous_prior
        self.individual_regressors = individual_regressors

        super().__init__(
            rng_key=rng_key,
            method="mcmc",
            mcmc_samples=mcmc_samples,
            mcmc_warmup=mcmc_warmup,
            mcmc_chains=mcmc_chains,
        )

        self.n_series = None
        self._time_scaler = TimeScaler()

        self._changepoint_matrix_maker = None

        self._linear_global_rates = None
        self._linear_initial_offsets = None
        self._changepoint_prior_loc_vector = None
        self._changepoint_prior_scale_vector = None
        self._exogenous_matrix_maker = None
        self._exogenous_coefficients = None
        self._changepoint_coefficients = None
        self._linear_offset_param = None
        self._capacity = None

    @property
    def changepoint_freq_list(self):
        if isinstance(self.changepoint_freq, int):
            return [self.changepoint_freq] * self.n_series
        return self.changepoint_freq

    @property
    def changepoint_prior_scale_list(self):
        if isinstance(self.changepoint_prior_scale, (int, float)):
            return [self.changepoint_prior_scale] * self.n_series
        return self.changepoint_prior_scale

    @property
    def capacity_prior_scale_list(self):
        if isinstance(self.capacity_prior_scale, (int, float)):
            return [self.capacity_prior_scale] * self.n_series
        return self.capacity_prior_scale

    def _get_numpyro_model_data(self, y, X, fh):
        """
        Fit the Prophet2 forecaster to the training data.

        Parameters:
        ----------
        y : pd.DataFrame
            Training target time series.
        X : pd.DataFrame
            Training exogenous variables.
        fh : ForecastingHorizon
            Forecasting horizon.

        Returns:
        -------
        self : Prophet2
            The fitted Prophet2 forecaster.
        """
        # Convert X and y to tensors
        # Set scales
        # Get prior locs and scales
        # Create parameters

        self._has_exogenous_variables = True
        if X is None:
            self._has_exogenous_variables = False
            X = pd.DataFrame(index=y.index)

        X = X.loc[y.index]
        y_bottom = loc_bottom_series(y)
        X_bottom = X.loc[y_bottom.index]

        self.s_matrix_df = _get_s_matrix(y)
        self.s_matrix = jnp.array(self.s_matrix_df.values)
        self.n_series = self.s_matrix.shape[1]

        # Convert inputs to array, including the time index
        _, y_arrays = convert_dataframe_to_tensors(y)

        if self._has_exogenous_variables:
            _, X_arrays = convert_dataframe_to_tensors(X_bottom)

        t_arrays, y_bottom_arrays = convert_dataframe_to_tensors(y_bottom)

        # Setup model parameters and scalers, and get
        self._setup_model_parameters_and_scalers(t_arrays, y_bottom_arrays)

        # Exog variables
        if self._has_exogenous_variables:
            self._setup_exogenous_variables_and_transformer(X)
            exogenous_matrix = self._exogenous_matrix_maker.transform(X=X_arrays)
        else:
            exogenous_matrix = jnp.zeros_like(t_arrays)
        # Changepoints
        self._setup_changepoint_variables_and_transformer(t_arrays)
        changepoints_matrix = self._changepoint_matrix_maker.transform(t=t_arrays)

        return dict(
            t=t_arrays,
            y=y_arrays.squeeze().T,
            X=exogenous_matrix,
            changepoints_matrix=changepoints_matrix,
            s_matrix=self.s_matrix,
        )

    def model(self, t, y, X, changepoints_matrix, s_matrix, *args, **kwargs):
        """
        Define the probabilistic model for Prophet2.

        Parameters:
        ----------
        t : ndarray
            Time index.
        y : ndarray
            Target time series.
        X : ndarray
            Exogenous variables.
        changepoints_matrix : ndarray
            Changepoint matrix.
        s_matrix : ndarray
            Reconciliation matrix.
        args, kwargs : additional arguments and keyword arguments
            Additional arguments and keyword arguments for the model.

        Returns:
        -------
        None
        """
        self.init_params()
        _trend_wo_offset = self._get_trend(t, changepoints_matrix, *args, **kwargs)
        trend = _trend_wo_offset + self._linear_offset_param.reshape(
            (-1, 1, 1)
        ) * self.y_scales.reshape((-1, 1, 1))
        exogenous_effect = self._get_exogenous_effect(X)
        mean = self._observation_mean(trend, exogenous_effect)

        std_observation = numpyro.sample(
            "std_observation", dist.HalfNormal(self.noise_scale * self.y_scales)
        )

        numpyro.deterministic("mean", mean)
        numpyro.deterministic("trend", trend)
        numpyro.deterministic("exogenous_effect", exogenous_effect)

        numpyro.sample(
            "obs",
            NormalReconciled(
                mean.T,
                std_observation,
                reconc_matrix=s_matrix,
            ),
            obs=y,
        )

    def _setup_model_parameters_and_scalers(self, t_arrays, y_arrays):
        """
        Setup model parameters and scalers.

        Parameters:
        ----------
        t_arrays : ndarray
            Transformed time index.
        y_arrays : ndarray
            Transformed target time series.

        Returns:
        -------
        None
        """
        self.y_scales = np.abs(y_arrays).max(axis=1).squeeze()
        self._time_scaler.fit(t=t_arrays)
        t_scaled = self._time_scaler.transform(t=t_arrays)

        self.y_scales = np.abs(y_arrays).max(axis=1).squeeze()

        # Setting loc and scales for the priors
        max_y = y_arrays.max(axis=1).squeeze()
        min_y = y_arrays.min(axis=1).squeeze()
        max_t = t_scaled.max(axis=1).squeeze()
        min_t = t_scaled.min(axis=1).squeeze()

        self._linear_global_rates = (max_y - min_y) / (max_t - min_t) / self.y_scales
        self._linear_initial_offsets = min_y - self._linear_global_rates * min_t
        if self.capacity_prior_loc is None:
            self.capacity_prior_loc = max_t
        if self.capacity_prior_scale is None:
            self.capacity_prior_scale = (max_y - min_y) / 2

    def _setup_exogenous_variables_and_transformer(self, X: pd.DataFrame):
        """
        Setup exogenous variables and transformer.

        Parameters:
        ----------
        X : pd.DataFrame
            Exogenous variables.

        Returns:
        -------
        None
        """
        self._set_exogenous_priors(X)
        X_arrays = convert_dataframe_to_tensors(X)[1]
        individual_regressors_idx = []
        if self.individual_regressors:
            individual_regressors_idx = X.columns.get_indexer(
                self.individual_regressors
            )
        shared_regressors = X.columns.difference(self.individual_regressors)
        shared_regressors_idx = X.columns.get_indexer(shared_regressors.tolist())

        self._exogenous_matrix_maker = ExogenousDataFrameToMatrixTransformer(
            n_series=self.n_series,
            individual_regressors_idx=individual_regressors_idx,
            shared_regressors_idx=shared_regressors_idx,
        )
        self._exogenous_matrix_maker.fit(X=X_arrays)

    def _get_exogenous_effect(self, X):
        """
        Get the effect of exogenous variables.

        Parameters:
        ----------
        X : ndarray
            Exogenous variables.

        Returns:
        -------
        ndarray
            Exogenous effect.
        """
        return X @ self._exogenous_coefficients.reshape((-1, 1))

    def _setup_changepoint_variables_and_transformer(self, t_arrays):
        """
        Setup changepoint variables and transformer.

        Parameters:
        ----------
        t_arrays : ndarray
            Transformed time index.

        Returns:
        -------
        None
        """
        self._changepoint_matrix_maker = ChangepointMatrix(self.changepoint_freq_list)
        self._changepoint_matrix_maker.fit(t=t_arrays)
        self._set_changepoint_prior_vectors()

    def _set_changepoint_prior_vectors(self):
        """
        Set the prior vectors for changepoint distribution.

        Returns:
        -------
        None
        """

        def zeros_with_first_value(size, first_value):
            x = jnp.zeros(size)
            x.at[0].set(first_value)
            return x

        changepoint_prior_scale_vector = np.concatenate(
            [
                np.ones(n_changepoint) * cur_changepoint_prior_scale
                for n_changepoint, cur_changepoint_prior_scale in zip(
                    self.n_changepoint_per_series, self.changepoint_prior_scale_list
                )
            ]
        )

        changepoint_prior_loc_vector = np.concatenate(
            [
                zeros_with_first_value(n_changepoint, estimated_global_rate)
                for n_changepoint, estimated_global_rate in zip(
                    self.n_changepoint_per_series, self._linear_global_rates
                )
            ]
        )

        self._changepoint_prior_loc_vector = jnp.array(changepoint_prior_loc_vector)
        self._changepoint_prior_scale_vector = jnp.array(changepoint_prior_scale_vector)

    def _get_changepoint_coefficients(self):
        """
        Get the coefficients for changepoints.

        Returns:
        -------
        ndarray
            Changepoint coefficients.
        """
        return numpyro.sample(
            "delta",
            dist.Laplace(
                self._changepoint_prior_loc_vector, self._changepoint_prior_scale_vector
            ),
        )

    def init_params(self):
        """
        Initialize the model parameters.

        Returns:
        -------
        None
        """

        if self._has_exogenous_variables:
            self._exogenous_coefficients = sample_exogenous_coefficients(self._exogenous_dists, self._exogenous_permutation_matrix)

        else:
            self._exogenous_coefficients = jnp.array([0])

        self._changepoint_coefficients = numpyro.sample(
            "delta",
            dist.Laplace(
                self._changepoint_prior_loc_vector, self._changepoint_prior_scale_vector
            ),
        )

        self._linear_offset_param = numpyro.sample(
            "linear_offset",
            dist.Normal(
                self._linear_initial_offsets / self.y_scales,
                jnp.array(self.changepoint_prior_scale),
            ),
        )

        if self.trend == "logistic":
            self._capacity = numpyro.sample(
                "capacity",
                dist.LogNormal(
                    self.capacity_prior_loc / self.y_scales,
                    self.capacity_prior_scale / self.y_scales,
                ),
            )

    def _get_trend(self, t, changepoints_matrix, *args, **kwargs):
        """
        Get the trend component.

        Parameters:
        ----------
        t : ndarray
            Time index.

        changepoints_matrix : ndarray
            Changepoint matrix.

        args, kwargs : additional arguments and keyword arguments
            Additional arguments and keyword arguments for the model.

        Returns:
        -------
        ndarray
            Trend component.
        """
        if self.trend == "linear":
            growth = get_piecewise_linear_trend(
                t=t,
                changepoints_matrix=changepoints_matrix,
                changepoint_t=self._changepoint_matrix_maker.changepoint_ts_array(),
                changepoint_coefficients=self._changepoint_coefficients,
            )

        elif self.trend == "logistic":
            growth = get_logistic_trend(
                t=t,
                changepoints_matrix=changepoints_matrix,
                changepoint_t=self._changepoint_matrix_maker.changepoint_ts_array(),
                changepoint_coefficients=self._changepoint_coefficients,
                capacity=self._capacity,
            )
        return growth

    def _observation_mean(self, trend, exogenous_effect):
        """
        Compute the mean of the observation.

        Parameters:
        ----------
        trend : ndarray
            Trend component.

        exogenous_effect : ndarray
            Exogenous effect.

        Returns:
        -------
        ndarray
            Mean of the observation.
        """
        if self.seasonality_mode == "additive":
            val = additive_mean_model(trend, exogenous_effect)

        elif self.seasonality_mode == "multiplicative":
            val = multiplicative_mean_model(trend, exogenous_effect, exponent=1)

        return val.squeeze()

    def _predict_samples(self, X, fh: ForecastingHorizon):
        """
        Generate samples for the given exogenous variables and forecasting horizon.

        Parameters:
        ----------
        X : pd.DataFrame
            Exogenous variables.

        fh : ForecastingHorizon
            Forecasting horizon.

        Returns:
        -------
        ndarray
            Predicted samples.
        """
        if not isinstance(fh, ForecastingHorizon):
            fh = self._check_fh(fh)
        fh_dates = fh.to_absolute(cutoff=self._y.index.get_level_values(-1).max())
        fh_as_index = pd.Index(list(fh_dates.to_numpy()))

        if self._has_exogenous_variables:
            X = X.loc[X.index.get_level_values(-1).isin(fh_as_index)]
            X_bottom = loc_bottom_series(X)
            X_arrays = series_to_tensor(X_bottom)

        t_arrays = jnp.array(convert_index_to_days_since_epoch(fh_as_index)).reshape(
            (1, -1, 1)
        )
        t_arrays = jnp.tile(t_arrays, (self.n_series, 1, 1))

        changepoints_matrix = self._changepoint_matrix_maker.transform(t=t_arrays)

        if self._has_exogenous_variables:
            exogenous_matrix = self._exogenous_matrix_maker.transform(X=X_arrays)
        else:
            exogenous_matrix = jnp.zeros_like(t_arrays)

        predictive = Predictive(
            self.model,
            self.posterior_samples_,
            return_sites=["obs"],
        )

        return predictive(
            self.rng_key,
            t=t_arrays,
            y=None,
            X=exogenous_matrix,
            changepoints_matrix=changepoints_matrix,
            changepoint_prior_loc_vector=self._changepoint_prior_loc_vector,
            changepoint_prior_scale_vector=self._changepoint_prior_scale_vector,
            s_matrix=self.s_matrix,
        )

    @property
    def n_changepoint_per_series(self):
        return self._changepoint_matrix_maker.n_changepoint_per_series

    def _set_exogenous_priors(self, X):
        # The dict self.exogenous_prior contain a regex as key, and a tuple (distribution, kwargs) as value.
        # The regex is matched against the column names of X, and the corresponding distribution is used to

        (
            self._exogenous_dists,
            self._exogenous_permutation_matrix,
        ) = get_exogenous_priors(X, self.exogenous_priors, self.default_exogenous_prior)
        return self
