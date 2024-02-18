from typing import Tuple

import numpy as np
import numba as nb
from numba import njit, prange

# Numba-optimised functions
@njit
def ols_estim(y: np.array, X: np.array) -> Tuple[np.array, float]:
    """Estimates the beta and R-squared of an OLS regression

    Assumes that the intercept is included in X.

    Args:
        y (np.array): Dependent variable observations (dimension T x 1)
        X (np.array): Explanatory variables observations (dimension T x K)

    Returns:
        Tuple[np.array, float]: Beta coefficients (dimension K x 1), R-squared
    """
    p = X.shape[1]
    try:
        XtXinv = np.linalg.inv(X.T @ X)

        # Estimate coefficients
        beta = XtXinv @ (X.T @ y)

        # Compute residuals
        e = y - X @ beta
        # Compute R^2 and adj R^2
        r2 = 1 - np.sum(e**2) / np.sum((y - np.mean(y)) ** 2)

    except Exception:
        beta = np.full((p, 1), np.nan)
        r2 = np.nan

    return beta, r2


@njit
def ols_estim_se(y: np.array, X: np.array) -> Tuple[np.array, np.array, float]:
    """Estimates the beta, White standard errors, and R-squared of an OLS regression

    Assumes that the intercept is included in X.

    Args:
        y (np.array): Dependent variable observations (dimension T x 1)
        X (np.array): Explanatory variables observations (dimension T x K)

    Returns:
        Tuple[np.array, np.array, float]: Beta coefficients (dimension K x 1), standard errors (dimension K x K), R-squared
    """
    p = X.shape[1]
    try:
        XtXinv = np.linalg.inv(X.T @ X)

        # Estimate coefficients
        beta = XtXinv @ (X.T @ y)

        # Compute residuals
        e = y - X @ beta
        # Compute R^2 and adj R^2
        r2 = 1 - np.sum(e**2) / np.sum((y - np.mean(y)) ** 2)

        # Compute standard errors (White)
        Sigma_HC = XtXinv @ (X.T @ np.diag(e.flatten() ** 2) @ X) @ XtXinv
        se = np.diag(Sigma_HC) ** 0.5

    except Exception:
        beta = np.full((p, 1), np.nan)
        se = np.full((p,), np.nan)
        r2 = np.nan

    return beta, se, r2


@njit
def compute_unbiasedness_reg_jit(
    data: nb.typed.typedlist.List,
) -> Tuple[np.array, np.array]:
    """Estimates the betas and R-squared of an unbiasedness regression

    Assumes that the intercept is included in X, and that there is only one explanatory variable.
    The beta coefficient is the coefficient on the explanatory variable.

    Args:
        data (nb.typed.typedlist.List): A list of tuples (y, X) where y is the dependent variable observations (dimension T x 1) and X is the explanatory variables observations (dimension T x K)

    Returns:
        Tuple[np.array, np.array, np.array]: Beta coefficients (dimension N x 1), R-squared (dimension N x 1)
    """
    N = len(data)
    beta = np.empty(N)
    r2 = np.empty(N)
    for i in prange(N):
        estim_i = ols_estim(data[i][0], data[i][1])
        beta[i] = estim_i[0][1][0]
        r2[i] = estim_i[1]
    return beta, r2


@njit
def compute_unbiasedness_reg_se_jit(
    data: nb.typed.typedlist.List,
) -> Tuple[np.array, np.array, np.array]:
    """Estimates the betas, White standard errors, and R-squared of an unbiasedness regression

    Assumes that the intercept is included in X, and that there is only one explanatory variable.
    The beta coefficient (and associated standard errors) is the coefficient on the explanatory variable.

    Args:
        data (nb.typed.typedlist.List): A list of tuples (y, X) where y is the dependent variable observations (dimension T x 1) and X is the explanatory variables observations (dimension T x K)

    Returns:
        Tuple[np.array, np.array, np.array]: Beta coefficients (dimension N x 1), standard errors (dimension N x 1), R-squared (dimension N x 1)
    """
    N = len(data)
    beta = np.empty(N)
    se = np.empty(N)
    r2 = np.empty(N)
    for i in prange(N):
        estim_i = ols_estim_se(data[i][0], data[i][1])
        beta[i] = estim_i[0][1][0]
        se[i] = estim_i[1][1]
        r2[i] = estim_i[2]
    return beta, se, r2
