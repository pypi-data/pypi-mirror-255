from typing import List

import numpy as np


def get_changepoint_t(t : np.ndarray, changepoint_freq):
    """
    Get the changepoint time indices for each series.

    Parameters:
        t (ndarray): Time indices for each series.
        changepoint_freq (list): List of frequencies for each series.

    Returns:
        list: List of changepoint time indices for each series.
    """
    
    if t.ndim == 3:
        t = t[0]
    elif t != 2:
        raise ValueError("t must be a 2D or 3D array")
    
    changepoint_ts = []
    for _, freq in enumerate(changepoint_freq):
        changepoint_ts.append(t[::freq].flatten())
    return changepoint_ts


def compute_changepoint_design_matrix(t, changepoint_ts):
    """
    Compute the changepoint design matrix.

    Parameters:
        t (ndarray): Time indices for each series.
        changepoint_ts (list): List of changepoint time indices for each series.

    Returns:
        ndarray: Changepoint design matrix.
    """
    n_changepoint_per_series = [len(x) for x in changepoint_ts]
    changepoint_design_tensor = []
    for i, n_changepoints in enumerate(n_changepoint_per_series):
        A = np.tile(t[i].reshape((-1, 1)), (1, sum(n_changepoint_per_series)))
        A = (A >= np.concatenate(changepoint_ts, axis=0)).astype(int)

        start_idx = sum(n_changepoint_per_series[:i])
        end_idx = start_idx + n_changepoints
        mask = np.zeros_like(A)
        mask[:, start_idx:end_idx] = 1

        changepoint_design_tensor.append(A * mask)

    changepoint_design_tensor = np.stack(changepoint_design_tensor, axis=0)
    return changepoint_design_tensor


class TimeScaler:
    
    def fit(self, t):
        """
        Fit the time scaler.

        Parameters:
            t (ndarray): Time indices for each series.

        Returns:
            TimeScaler: The fitted TimeScaler object.
        """
        self.t_scale = (t[:, 1:] - t[:, :-1]).flatten().mean()
        self.t_min = t.min()
        return self

    def transform(self, t):
        """
        Transform the time indices.

        Parameters:
            t (ndarray): Time indices for each series.

        Returns:
            ndarray: Transformed time indices.
        """
        return (t - self.t_min) / self.t_scale

    def fit_transform(self, t):
        """
        Fit the time scaler and transform the time indices.

        Parameters:
            t (ndarray): Time indices for each series.

        Returns:
            ndarray: Transformed time indices.
        """
        self.fit(t)
        return self.transform(t)


class ChangepointMatrix:
    def __init__(self, changepoint_freq):
        """
        Initialize the ChangepointMatrix.

        Parameters:
            changepoint_freq (list): List of frequencies for each series.
        """
        self.changepoint_freq = changepoint_freq

    def fit(self, t):
        """
        Fit the ChangepointMatrix.

        Parameters:
            t (ndarray): Time indices for each series.

        Returns:
            ChangepointMatrix: The fitted ChangepointMatrix object.
        """
        self.changepoint_ts = get_changepoint_t(t, self.changepoint_freq)
        return self

    def transform(self, t):
        """
        Transform the time indices into the changepoint design matrix.

        Parameters:
            t (ndarray): Time indices for each series.

        Returns:
            ndarray: Changepoint design matrix.
        """
        A_tensor = compute_changepoint_design_matrix(t, self.changepoint_ts)
        return A_tensor

    def fit_transform(self, t):
        """
        Fit the ChangepointMatrix and transform the time indices into the changepoint design matrix.

        Parameters:
            t (ndarray): Time indices for each series.

        Returns:
            ndarray: Changepoint design matrix.
        """
        self.fit(t)
        return self.transform(t)

    def changepoint_ts_array(self):
        """
        Get the concatenated changepoint time indices array.

        Returns:
            ndarray: Concatenated changepoint time indices array.
        """
        return np.concatenate(self.changepoint_ts, axis=0)

    @property
    def n_changepoint_per_series(self):
        """
        Get the number of changepoints per series.

        Returns:
            list: List of the number of changepoints per series.
        """
        return [len(x) for x in self.changepoint_ts]


class ExogenousDataFrameToMatrixTransformer:
    def __init__(self, n_series, individual_regressors_idx, shared_regressors_idx):
        """
        Initialize the ExogenousXMatrix.

        Parameters:
            n_series (int): Number of series.
            individual_regressors_idx (list): List of indices for individual regressors.
            shared_regressors_idx (list): List of indices for shared regressors.
        """
        self.n_series = n_series
        self.individual_regressors_idx = individual_regressors_idx
        self.shared_regressors_idx = shared_regressors_idx

        self.n_individual_regressors = len(self.individual_regressors_idx)
        self.n_shared_regressors = len(self.shared_regressors_idx)

    def fit(self, X : np.ndarray):
        """
        Fit the ExogenousXMatrix.

        Parameters:
            X (ndarray): Exogenous variables.

        Returns:
            ExogenousXMatrix: The fitted ExogenousXMatrix object.
        """
        return self

    def fit_transform(self, X : np.ndarray) -> np.ndarray:
        """
        Fit the ExogenousXMatrix and transform the exogenous variables into the exogenous design matrix.

        Parameters:
            X (ndarray): Exogenous variables.

        Returns:
            ndarray: Exogenous design matrix.
        """
        self.fit(X)
        return self.transform(X)
    
    def transform(self, X : np.ndarray) -> np.ndarray:
        """
        Transform the exogenous variables into the exogenous design matrix.

        Parameters:
            X (ndarray): Exogenous variables.

        Returns:
            ndarray: Exogenous design matrix.
        """
        assert X.ndim == 3, "X must be a 3D array of (n_series, n_time, n_features)"
        
        X_tensor = []
        for i in range(self.n_series):
            _X = X[i]
            _X_tensor = np.zeros(
                (
                    _X.shape[0],
                    self.n_individual_regressors * self.n_series
                    + self.n_shared_regressors,
                )
            )

            if self.n_individual_regressors:
                _X_tensor[
                    :,
                    i
                    * self.n_individual_regressors : (i + 1)
                    * self.n_individual_regressors,
                ] = _X[:, self.individual_regressors_idx]
            if self.n_shared_regressors:
                _X_tensor[:, -self.n_shared_regressors :] = _X[
                    :, self.shared_regressors_idx
                ]
            X_tensor.append(_X_tensor)
        X_tensor = np.stack(X_tensor, axis=0)
        return X_tensor
