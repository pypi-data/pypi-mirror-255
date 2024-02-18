import logging
import re
from functools import partial

import jax
import jax.numpy as jnp
import numpy as np
import numpyro
import pandas as pd
from jax import lax, random
from numpyro import distributions as dist
from numpyro.infer import MCMC, NUTS, Predictive
from sktime.forecasting.base import BaseForecaster, ForecastingHorizon

from prophet_numpyro.base import BaseBayesianForecaster
from prophet_numpyro.exogenous_priors import (get_exogenous_priors,
                                              sample_exogenous_coefficients)
from prophet_numpyro.prophet.jax_functions import (
    additive_mean_model, get_changepoint_coefficient_matrix,
    get_changepoint_offset_adjustment, get_logistic_trend,
    get_piecewise_linear_trend, multiplicative_mean_model)

logger = logging.getLogger("prophet-numpyro")

NANOSECONDS_TO_SECONDS = 1000 * 1000 * 1000


class Prophet(BaseBayesianForecaster):
    """
    Prophet is a Bayesian time series forecasting model based on the Prophet-Numpyro library.

    Args:
        n_changepoints (int): Number of changepoints to be considered in the model.
        changepoint_range (float): Proportion of the data range in which changepoints will be considered.
        changepoint_prior_scale (float): Scale parameter for the Laplace prior distribution of the changepoints.
        growth_offset_prior_scale (float): Scale parameter for the prior distribution of the growth offset.
        capacity_prior_scale (float): Scale parameter for the prior distribution of the capacity.
        capacity_prior_loc (float): Location parameter for the prior distribution of the capacity.
        noise_scale (float): Scale parameter for the observation noise.
        trend (str): Type of trend to be considered in the model. Options are "linear" and "logistic".
        seasonality_mode (str): Mode of seasonality to be considered in the model. Options are "additive" and "multiplicative".
        mcmc_samples (int): Number of MCMC samples to be drawn.
        mcmc_warmup (int): Number of MCMC warmup steps.
        mcmc_chains (int): Number of MCMC chains.
        exogenous_priors (dict): Dictionary specifying the prior distributions for the exogenous variables.
        default_exogenous_prior (tuple): Default prior distribution for the exogenous variables.
        rng_key (jax.random.PRNGKey): Random number generator key.

    Attributes:
        n_changepoints (int): Number of changepoints to be considered in the model.
        changepoint_range (float): Proportion of the data range in which changepoints will be considered.
        changepoint_prior_scale (float): Scale parameter for the Laplace prior distribution of the changepoints.
        noise_scale (float): Scale parameter for the observation noise.
        growth_offset_prior_scale (float): Scale parameter for the prior distribution of the growth offset.
        capacity_prior_scale (float): Scale parameter for the prior distribution of the capacity.
        capacity_prior_loc (float): Location parameter for the prior distribution of the capacity.
        seasonality_mode (str): Mode of seasonality to be considered in the model. Options are "additive" and "multiplicative".
        trend (str): Type of trend to be considered in the model. Options are "linear" and "logistic".
        exogenous_priors (dict): Dictionary specifying the prior distributions for the exogenous variables.
        default_exogenous_prior (tuple): Default prior distribution for the exogenous variables.
        rng_key (jax.random.PRNGKey): Random number generator key.
        _ref_date (None): Reference date for the time series.
        _linear_global_rate (float): Global rate of the linear trend.
        _linear_offset (float): Offset of the linear trend.
        _changepoint_t (jax.numpy.ndarray): Array of changepoint times.
        _n_exogenous (int): Number of exogenous variables.
        _exogenous_dists (list): List of prior distributions for the exogenous variables.
        _exogenous_permutation_matrix (jax.numpy.ndarray): Permutation matrix for the exogenous variables.
        _exogenous_coefficients (jax.numpy.ndarray): Coefficients for the exogenous variables.
        _changepoint_coefficients (jax.numpy.ndarray): Coefficients for the changepoints.
        _linear_offset_coef (float): Coefficient for the linear offset.
        _capacity (float): Capacity parameter for the logistic trend.
        _samples_predictive (dict): Dictionary of predictive samples.

    """

    _tags = {
        "requires-fh-in-fit": False,
        "y_inner_mtype": "pd.DataFrame",
    }

    def __init__(
        self,
        n_changepoints=25,
        changepoint_range=0.8,
        changepoint_prior_scale=None,
        growth_offset_prior_scale=1,
        capacity_prior_scale=None,
        capacity_prior_loc=1,
        noise_scale=1,
        trend="linear",
        seasonality_mode="multiplicative",
        mcmc_samples=2000,
        mcmc_warmup=200,
        mcmc_chains=4,
        exogenous_priors={},
        default_exogenous_prior=(dist.Normal, 0, 1),
        rng_key=random.PRNGKey(24),
        
    ):  
        """
        Initializes a Prophet object.

        Args:
            n_changepoints (int): Number of changepoints to be considered in the model.
            changepoint_range (float): Proportion of the data range in which changepoints will be considered.
            changepoint_prior_scale (float): Scale parameter for the Laplace prior distribution of the changepoints.
            growth_offset_prior_scale (float): Scale parameter for the prior distribution of the growth offset.
            capacity_prior_scale (float): Scale parameter for the prior distribution of the capacity.
            capacity_prior_loc (float): Location parameter for the prior distribution of the capacity.
            noise_scale (float): Scale parameter for the observation noise.
            trend (str): Type of trend to be considered in the model. Options are "linear" and "logistic".
            seasonality_mode (str): Mode of seasonality to be considered in the model. Options are "additive" and "multiplicative".
            mcmc_samples (int): Number of MCMC samples to be drawn.
            mcmc_warmup (int): Number of MCMC warmup steps.
            mcmc_chains (int): Number of MCMC chains.
            exogenous_priors (dict): Dictionary specifying the prior distributions for the exogenous variables.
            default_exogenous_prior (tuple): Default prior distribution for the exogenous variables.
            rng_key (jax.random.PRNGKey): Random number generator key.
        """

        self.n_changepoints = n_changepoints
        self.changepoint_range = changepoint_range
        self.changepoint_prior_scale = changepoint_prior_scale
        self.noise_scale = noise_scale
        self.growth_offset_prior_scale = growth_offset_prior_scale
        self.capacity_prior_scale = capacity_prior_scale
        self.capacity_prior_loc = capacity_prior_loc
        self.seasonality_mode = seasonality_mode
        self.trend = trend
        self.exogenous_priors = exogenous_priors
        self.default_exogenous_prior = default_exogenous_prior

        super().__init__(
            rng_key=rng_key,
            method="mcmc",
            mcmc_samples=mcmc_samples,
            mcmc_warmup=mcmc_warmup,
            mcmc_chains=mcmc_chains,
        )

        self._ref_date = None

    def convert_index_to_days_since_epoch(self, idx: pd.Index):
        """
        Converts a pandas Index object to an array of days since epoch.

        Args:
            idx (pd.Index): Pandas Index object.

        Returns:
            np.ndarray: Array of days since epoch.
        """
        t = idx
        if isinstance(t, pd.PeriodIndex):
            t = t.to_timestamp()

        return t.to_numpy(dtype=np.int64) // NANOSECONDS_TO_SECONDS / (3600 * 24.0)

    def _set_scales(self, y):
        """
        Sets the scales for the time series data.

        Args:
            y (pd.DataFrame): Time series data.
        """
        t_days = self.convert_index_to_days_since_epoch(y.index)
        self.t_start = t_days.min()
        self.t_scale = t_days.max() - t_days.min()

        y_vector = y.values.flatten()
        self.y_scale = np.max(np.abs(y_vector))

        t_scaled = self._scale_index(y.index)

        self._linear_global_rate = (y_vector.max() - y_vector.min()) / (
            t_scaled.max() - t_scaled.min()
        )
        self._linear_offset = y_vector.min() - self._linear_global_rate * t_scaled.min()
        if self.capacity_prior_loc is None:
            self.capacity_prior_loc = y_vector.max()
        if self.capacity_prior_scale is None:
            self.capacity_prior_scale = (y_vector.max() - y_vector.min()) / 2

    def _replace_hyperparam_nones_with_defaults(self, y):
        """
        Replaces None values in hyperparameters with default values.

        Args:
            y (pd.DataFrame): Time series data.
        """
        if self.changepoint_prior_scale is None:
            if self.trend == "logistic":
                self.changepoint_prior_scale = 0.1
            else:
                self.changepoint_prior_scale = y.diff().dropna().values.std()


    def _get_numpyro_model_data(self, y, X, fh):
        """
        Prepares the data for the Numpyro model.

        Args:
            y (pd.DataFrame): Time series data.
            X (pd.DataFrame): Exogenous variables.
            fh (ForecastingHorizon): Forecasting horizon.

        Returns:
            dict: Dictionary of data for the Numpyro model.
        """
        self._set_scales(y)
        self._replace_hyperparam_nones_with_defaults(y)
        self._set_exogenous_priors(X)
        t = self._convert_periodindex_to_floatarray(y.index)

        self._n_exogenous = X.shape[1] if X is not None else 0

        self._set_changepoints_t(t)

        return dict(y=jnp.array(y.values.flatten()),
                    X=jnp.array(X.loc[y.index].values),
                    t=t)

    def _scale_index(self, idx):
        """
        Scales the index values.

        Args:
            idx (pd.Index): Pandas Index object.

        Returns:
            np.ndarray: Scaled index values.
        """
        t_days = self.convert_index_to_days_since_epoch(idx)
        return (t_days - self.t_start) / self.t_scale

    def _convert_periodindex_to_floatarray(self, period_index):
        """
        Converts a pandas PeriodIndex object to a float array.

        Args:
            period_index (pd.PeriodIndex): Pandas PeriodIndex object.

        Returns:
            jnp.ndarray: Float array.
        """
        return jnp.array(self._scale_index(period_index))

    def _set_changepoints_t(self, t):
        """
        Sets the array of changepoint times.

        Args:
            t (jnp.ndarray): Array of time values.
        """
        # Calculate the total number of data points
        n_data = len(t)

        # Calculate the number of data points in the changepoint range
        n_changepoint_range = int(n_data * self.changepoint_range)

        # Calculate the indices of the changepoints
        changepoint_indices = jnp.linspace(
            start=0,
            stop=n_changepoint_range,
            num=self.n_changepoints,
            dtype=int,
        )

        # Get the actual changepoints
        self._changepoint_t = t[changepoint_indices]

    def _get_changepoints_matrix(self, t):
        """
        Generates the changepoint coefficient matrix.

        Args:
            t (jnp.ndarray): Array of time values.

        Returns:
            jnp.ndarray: Changepoint coefficient matrix.
        """
        A = jnp.tile(t.reshape((-1, 1)), (1, len(self._changepoint_t)))
        A = (A >= self._changepoint_t).astype(int)
        return A

    def init_params(self):
        """
        Initializes the model parameters.
        """
        self._exogenous_coefficients = sample_exogenous_coefficients(exogenous_dists=self._exogenous_dists, exogenous_permutation_matrix=self._exogenous_permutation_matrix)
        changepoints_loc = jnp.zeros(len(self._changepoint_t))
        changepoints_loc.at[0].set(self._linear_global_rate)
        if self.trend == "linear":
            self._changepoint_coefficients = numpyro.sample(
                "delta",
                dist.Laplace(
                    changepoints_loc,
                    jnp.ones(len(self._changepoint_t))
                    * (self.changepoint_prior_scale * self.y_scale),
                ),
            )

            self._linear_offset_coef = numpyro.sample(
                "linear_offset",
                dist.Normal(
                    self._linear_offset,
                    0.1,
                ),
            )

        if self.trend == "logistic":
            self._changepoint_coefficients = numpyro.sample(
                "delta",
                dist.Laplace(
                    changepoints_loc,
                    jnp.ones(len(self._changepoint_t))
                    
                ),
            )

            self._linear_offset_coef = numpyro.sample(
                "linear_offset",
                dist.Normal(
                    0,
                    0.1,
                ),
            )

            self._capacity = numpyro.sample(
                "capacity",
                dist.LogNormal(
                    self.capacity_prior_loc,
                    self.capacity_prior_scale,
                ),
            )

    def _get_trend(self, t, *args, **kwargs):
        """
        Computes the trend component of the model.

        Args:
            t (jnp.ndarray): Array of time values.

        Returns:
            jnp.ndarray: Trend component.
        """
        changepoints_matrix = self._get_changepoints_matrix(t)
        if self.trend == "linear":
            return get_piecewise_linear_trend(
                t,
                changepoints_matrix,
                self._changepoint_t,
                changepoint_coefficients=self._changepoint_coefficients,
                linear_offset_coef=self._linear_offset_coef,
            )
        elif self.trend == "logistic":
            return get_logistic_trend(
                t,
                changepoints_matrix,
                self._changepoint_t,
                changepoint_coefficients=self._changepoint_coefficients,
                linear_offset_coef=self._linear_offset_coef,
                capacity=self._capacity,
            )

    def _observation_mean(self, trend, exogenous_effect):
        """
        Computes the mean of the observation.

        Args:
            trend (jnp.ndarray): Trend component.
            exogenous_effect (jnp.ndarray): Exogenous effect.

        Returns:
            jnp.ndarray: Mean of the observation.
        """
        if self.seasonality_mode == "additive":
            return additive_mean_model(trend, exogenous_effect)
        else:
            return multiplicative_mean_model(trend, exogenous_effect)

    def model(self, y, X, t, *args, **kwargs):
        """
        Defines the Numpyro model.

        Args:
            y (jnp.ndarray): Array of time series data.
            X (jnp.ndarray): Array of exogenous variables.
            t (jnp.ndarray): Array of time values.
        """
        self.init_params()
        trend = self._get_trend(t, *args, **kwargs)
        exogenous_effect = self._get_exogenous_effect(X)
        mean = self._observation_mean(trend, exogenous_effect)

        std_observation = numpyro.sample(
            "std_observation", dist.HalfNormal(self.noise_scale * self.y_scale)
        )

        with numpyro.plate("obs_plate", len(t)):
            numpyro.sample(
                "obs",
                dist.Normal(mean.flatten(), std_observation),
                obs=y,
            )

    def _predict_samples(self, X, fh: ForecastingHorizon):
        """
        Generates predictive samples.

        Args:
            X (pd.DataFrame): Exogenous variables.
            fh (ForecastingHorizon): Forecasting horizon.

        Returns:
            dict: Dictionary of predictive samples.
        """
        fh_dates = self.fh_to_index(fh)
        fh_as_index = pd.Index(list(fh_dates.to_numpy()))

        t = self._convert_periodindex_to_floatarray(fh_as_index)

        predictive = Predictive(
            self.model, self.posterior_samples_, return_sites=["obs"]
        )
        self.samples_predictive_ = predictive(
            self.rng_key, y=None, X=jnp.array(X.loc[fh_as_index].values), t=t
        )
        return self.samples_predictive_

    def _set_exogenous_priors(self, X):
        """
        Sets the prior distributions for the exogenous variables.

        Args:
            X (pd.DataFrame): Exogenous variables.

        Returns:
            self: Returns self.
        """
        (
            self._exogenous_dists,
            self._exogenous_permutation_matrix,
        ) = get_exogenous_priors(X, self.exogenous_priors, self.default_exogenous_prior)
        return self

    def _get_exogenous_effect(self, X):
        """
        Computes the exogenous effect.

        Args:
            X (jnp.ndarray): Array of exogenous variables.

        Returns:
            jnp.ndarray: Exogenous effect.
        """
        return X @ self._exogenous_coefficients.reshape((-1, 1))
