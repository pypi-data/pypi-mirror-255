import os

import numpy as np
import scipy.sparse as sparse

from .io import DATA_ROOT


def load_dists(space, lr):
    fn = os.path.join(DATA_ROOT, 'dijkstra', f'{space}_{lr}h.npy')
    d = np.load(fn)
    ico = int(space.split('-ico')[1])
    nv = ico**2 * 10 + 2
    mat = np.zeros((nv, nv), dtype=d.dtype)
    idx1, idx2 = np.triu_indices(nv, 1)
    mat[idx1, idx2] = d
    mat = np.maximum(mat, mat.T)
    return mat


def smooth(space, lr, fwhm, mask=None):
    d = load_dists(space, lr)
    if mask is not None:
        d = d[np.ix_(mask, mask)]
    s2 = fwhm / (4.0 * np.log(2))
    weights = np.exp(-(d**2) / s2)
    weights = sparse.csr_matrix(weights)
    return weights
