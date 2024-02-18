import numpy as np
from joblib import Parallel, delayed

from .linalg import ridge_grid


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
    candidates0 = np.setdiff1d(arng, withhold) if withhold else arng
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
            y,
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
