"""
==================================================
Linear algebra utilities (:mod:`neuroboros.ridge`)
==================================================

.. currentmodule:: neuroboros.ridge

.. autosummary::
    :toctree:

    ridge - Ridge regression.
    ridge_grid - Ridge regression with a grid search of hyperparameters.
    ridge_ensemble - Ensemble ridge regression models with cross-validation.

"""
import warnings

import numpy as np
from joblib import Parallel, delayed

from .linalg import safe_svd


def ridge(X, Y, alpha, npc, fit_intercept=True, X_test=None, mask=None):
    """
    Ridge regression.

    Parameters
    ----------
    X : ndarray of shape (n_samples, n_features)
        The design matrix in NumPy array format. If ``mask`` is not None,
        ``X[mask]`` should have shape (n_samples, n_features) instead.
    Y : ndarray of shape (n_samples,) or (n_samples, n_measures)
        The target vector in NumPy array format.
    alpha : float
        The regularization parameter.
    npc : {int, None}
        The number of principal components (PCs) to be used. If None, all PCs
        are used.
    fit_intercept : bool, default=True
        Whether to fit the intercept or not.
    X_test : ndarray of shape (n_test_samples, n_features), default=None
        The design matrix for the test data. If not None, the predicted values
        for the test data are returned.
    mask : ndarray, default=None
        The mask for the design matrix. If not None, ``X[mask]`` is used
        in training instead of ``X``.

    Returns
    -------
    beta : ndarray of shape (n_features,) or (n_features + 1,)
        The regression coefficients. If ``fit_intercept`` is True, the last
        element is the intercept.
    Yhat : ndarray of shape (n_test_samples,) or (n_test_samples, n_measures)
        The predicted values for the test data. Returned only when
        ``X_test`` is not None.

    Notes
    -----
    The ``npc`` parameter depends on the ``fit_intercept`` parameter to be
    ``True`` to be used. The PCs are based on a SVD of the design matrix
    ``X``. When ``X`` is not centered, the eigenvectors do not correspond to
    the PCs.
    """
    if mask is not None:
        X = X[mask]

    if fit_intercept:
        X_offset = X.mean(axis=0, keepdims=True)
        Y_offset = Y.mean(axis=0, keepdims=True)
        if np.allclose(X_offset, 0, atol=1e-10):
            X_offset = None
        else:
            X = X - X_offset
        if np.allclose(Y_offset, 0, atol=1e-10):
            Y_offset = np.zeros_like(Y_offset)
        else:
            Y = Y - Y_offset

    if npc is not None and not fit_intercept:
        warnings.warn(
            'The `npc` parameter is based on an SVD of `X`. When '
            '`fit_intercept` is False, the eigenvectors of the SVD '
            'do not correspond to the principal components.'
        )

    U, s, Vt = safe_svd(X, remove_mean=False)
    d = s[:npc] / (alpha + s[:npc] ** 2)
    UT_Y = U.T[:npc, :] @ Y
    while len(d.shape) < len(UT_Y.shape):
        d = d[..., np.newaxis]
    d_UT_Y = d * UT_Y

    beta = Vt.T[:, :npc] @ d_UT_Y
    if fit_intercept:
        beta0 = Y_offset - (0 if X_offset is None else (X_offset @ beta))
        beta = np.concatenate((beta, beta0), axis=0)

    if X_test is not None:
        if fit_intercept:
            Yhat = X_test @ beta[:-1] + beta[-1]
        else:
            Yhat = X_test @ beta
        return beta, Yhat

    return beta


def ridge_grid(
    X, Y, alphas, npcs, fit_intercept=True, X_test=None, mask=None, test_mask=None
):
    """Ridge regression with a grid of hyperparameters.

    Returns the predicted values for the test data with the grid of hyperparameters.

    Parameters
    ----------
    X : ndarray of shape (n_samples, n_features)
        The design matrix in NumPy array format. If ``mask`` is not None,
        ``X[mask]`` should have shape (n_samples, n_features) instead.
    Y : ndarray of shape (n_samples,) or (n_samples, n_measures)
        The target vector or matrix in NumPy array format.
    alphas : list of float
        The regularization parameters for grid search.
    npcs : list of {int, None}
        The numbers of principal components (PCs) to be used for grid search.
        If None, all PCs are used.
    fit_intercept : bool, default=True
        Whether to fit the intercept or not.
    X_test : ndarray of shape (n_test_samples, n_features), default=None
        The design matrix for the test data. If None, ``X`` is used.
    mask : ndarray, default=None
        If not None, ``X[mask]`` is used in training instead of ``X``.
    test_mask : ndarray, default=None
        If not None, ``X_test[test_mask]`` is used in testing instead of ``X_test``.

    Returns
    -------
    yhat : ndarray
        The predicted values for the test data with the grid of
        hyperparameters. The shape is (n_test_samples, n_alphas, n_npcs) or
        (n_test_samples, n_measures, n_alphas, n_npcs) depending on the shape
        of ``y``.
    """
    if X_test is None:
        X_test = X
    if test_mask is not None:
        X_test = X_test[test_mask]
    if mask is not None:
        X = X[mask]

    if fit_intercept:
        X_offset = X.mean(axis=0, keepdims=True)
        Y_offset = Y.mean(axis=0, keepdims=True)
        if np.allclose(X_offset, 0, atol=1e-10):
            X_offset = None
        else:
            X = X - X_offset
        if np.allclose(Y_offset, 0, atol=1e-10):
            Y_offset = np.zeros_like(Y_offset)
        else:
            Y = Y - Y_offset
    else:
        X_offset = None
        Y_offset = np.zeros_like(Y)

    U, s, Vt = safe_svd(X, remove_mean=False)

    if fit_intercept and X_offset is not None:
        X_test_V = (X_test - X_offset) @ Vt.T  # (n_test_samples, k)
    else:
        X_test_V = X_test @ Vt.T
    UT_Y = U.T @ Y  # (k, )

    d = s[:, np.newaxis] / (np.array(alphas)[np.newaxis, :] + (s**2)[:, np.newaxis])
    # (k, n_alphas)

    if len(Y.shape) == 1:
        d_UT_Y = d * UT_Y[..., np.newaxis]  # (k, n_alphas)
        Yhat = np.zeros((X_test.shape[0], len(alphas), len(npcs)))
    elif len(Y.shape) == 2:
        d_UT_Y = d[:, np.newaxis, :] * UT_Y[..., np.newaxis]
        # d_UT_Y: (k, n_measures, n_alphas)
        Yhat = np.zeros((X_test.shape[0], Y.shape[1], len(alphas), len(npcs)))
        Y_offset = Y_offset[:, :, np.newaxis, np.newaxis]
    else:
        raise ValueError('`y` must be a 1D or 2D array.')

    npcs_ = [0] + list(npcs)
    for i in range(len(npcs)):
        Yhat[..., i] = np.tensordot(
            X_test_V[:, npcs_[i] : npcs[i]], d_UT_Y[npcs_[i] : npcs[i]], axes=(1, 0)
        )
    Yhat = np.cumsum(Yhat, axis=-1)

    if fit_intercept:
        Yhat += Y_offset

    return Yhat


def ridge_ensemble(
    X,
    y,
    alphas,
    npcs,
    n_iters=20,
    n_folds=5,
    output='best',
    fit_intercept=True,
    withhold=None,
    seed=0,
    n_jobs=-1,
):
    ns = X.shape[0]
    arng = np.arange(ns)
    candidates0 = arng if withhold is None else np.setdiff1d(arng, withhold)
    assert output in ['raw', 'all', 'best']

    yhats = np.zeros((ns, ns, len(alphas), len(npcs)))
    counts = np.zeros((ns, ns), dtype=int)

    train_idx_li, test_idx_li = [], []
    rng = np.random.default_rng(seed)
    for iter in range(n_iters):
        candidates = candidates0.copy()
        rng.shuffle(candidates)
        folds = np.array_split(candidates, n_folds)
        for fold in folds:
            train_idx = rng.choice(
                np.setdiff1d(candidates0, fold), len(candidates0), replace=True
            )
            test_idx = np.setdiff1d(arng, train_idx)
            train_idx_li.append(train_idx)
            test_idx_li.append(test_idx)

    jobs = [
        delayed(ridge_grid)(
            X,
            y[train_idx],
            alphas,
            npcs,
            fit_intercept=fit_intercept,
            mask=train_idx,
            test_mask=test_idx,
        )
        for train_idx, test_idx in zip(train_idx_li, test_idx_li)
    ]

    with Parallel(n_jobs=n_jobs) as parallel:
        results = parallel(jobs)
    for yhat, test_idx in zip(results, test_idx_li):
        yhats[np.ix_(test_idx, test_idx)] += yhat
        counts[np.ix_(test_idx, test_idx)] += 1

    if output == 'raw':
        return yhats, counts

    yhats /= counts[..., np.newaxis, np.newaxis]
    if output == 'all':
        return yhats

    yhat = np.zeros_like(y)
    params = np.zeros((ns, 2), dtype=int)
    for i in range(ns):
        train = np.setdiff1d(arng, i)
        if withhold is not None:
            train = np.setdiff1d(train, withhold)
        loss = np.sum(
            (yhats[i, train, :, :] - y[train, np.newaxis, np.newaxis]) ** 2, axis=0
        )
        j, k = np.unravel_index(np.argmin(loss), loss.shape)
        yhat[i] = yhats[i, i, j, k]
        params[i] = j, k
    return yhat, params
