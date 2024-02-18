import os

import numpy as np

cimport numpy as np


def triangle_subdivision(n_div):
    faces = []
    for i in range(1, n_div + 1)[::-1]:
        for j in range(n_div + 1 - i):
            k = n_div - i - j
            f = [(i, j, k), (i - 1, j + 1, k), (i - 1, j, k + 1)]
            faces.append(f)
    for i in range(1, n_div + 1)[::-1]:
        for j in range(1, n_div + 1 - i):
            k = n_div - i - j
            f = [(i, j, k), (i - 1, j, k + 1), (i, j - 1, k + 1)]
            faces.append(f)
    return faces


def subdivide_edges(np.ndarray coords, np.ndarray faces, size_t n_div):
    cdef size_t nv, nv_new, n_edges, count, i, a, b, aa, bb, ii, jj

    n_edges = faces.shape[0] * 3 // 2
    nv_new = n_edges * (n_div - 1)
    new_coords = np.zeros((nv_new, 3), dtype=coords.dtype)

    nv = coords.shape[0]
    count = 0
    # edges = []
    edges = set()
    e_mapping = {}
    for f in faces:
        for ii, jj in ((0, 1), (0, 2), (1, 2)):
            a = f[ii]
            b = f[jj]

            if a < b:
                aa = a
                bb = b
            else:
                aa = b
                bb = a
            if (aa, bb) in edges:
                continue
            edges.add((aa, bb))

            for i in range(1, n_div):
                c = (coords[a] * i + coords[b] * (n_div - i)) / n_div
                # c /= np.linalg.norm(c)
                # new_coords.append(c)
                new_coords[count] = c
                e_mapping[(aa, bb, i)] = count + nv
                count += 1

    return new_coords, e_mapping
