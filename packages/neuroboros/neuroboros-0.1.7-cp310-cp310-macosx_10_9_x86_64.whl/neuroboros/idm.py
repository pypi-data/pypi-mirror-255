import numpy as np
from scipy.spatial.distance import squareform


def compute_indices(g, extra=False, uu=None):
    is_same = squareform(g[:, None] == g[None, :], checks=False)
    w_idx = np.where(is_same)[0]
    b_idx = np.where(np.logical_not(is_same))[0]
    output = [w_idx, b_idx]
    if extra:
        g_idx = []
        if uu is None:
            uu = np.unique(g)
        for j, u in enumerate(uu):
            mask = g == u
            in_group = squareform(
                np.logical_and(mask[:, None], mask[None, :]), checks=False
            )
            idx = np.where(in_group)[0]
            g_idx.append(idx)
        output.append(g_idx)
    return output


def permutation_indices(groups, n_reps=10000, seed=0, extra=False):
    w_li, b_li = [], []
    if extra:
        uu = np.unique(groups)
        g_li = [[] for _ in uu]
    rng = np.random.default_rng(seed)
    for i in range(n_reps):
        g = groups.copy()
        rng.shuffle(g)
        if extra:
            w_idx, b_idx, g_idx = compute_indices(g, True, uu)
            for j, idx in enumerate(g_idx):
                g_li[j].append(idx)
        else:
            w_idx, b_idx = compute_indices(g, False)
        w_li.append(w_idx)
        b_li.append(b_idx)

    w_li, b_li = np.array(w_li), np.array(b_li)
    if extra:
        for i, li in enumerate(g_li):
            g_li[i] = np.array(li)
        return w_li, b_li, g_li
    return w_li, b_li


def compute_statistics(IDMs, b_idx, w_idx, g_idx=None):
    std_dof = len(w_idx) + len(b_idx) - 2
    bb, ww = IDMs[:, b_idx], IDMs[:, w_idx]
    b_m = bb.mean(axis=1, keepdims=True)
    w_m = ww.mean(axis=1, keepdims=True)
    ss = np.sum((bb - b_m) ** 2, axis=1) + np.sum((ww - w_m) ** 2, axis=1)
    std = np.sqrt(ss / std_dof)
    cohen = (b_m - w_m).ravel() / std
    output = [b_m.ravel(), w_m.ravel(), std, cohen]
    if g_idx is not None:
        for g in g_idx:
            output.append(IDMs[:, g].mean(axis=1))
    output = np.array(output)
    return output
