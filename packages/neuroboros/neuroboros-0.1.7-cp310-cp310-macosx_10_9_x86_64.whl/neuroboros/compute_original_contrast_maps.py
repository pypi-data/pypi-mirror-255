import os
import tarfile
from datetime import datetime
import numpy as np
import pandas as pd
from scipy.stats import zscore
from nipy.modalities.fmri.hemodynamic_models import compute_regressor

from post_fmriprep.denoise_resample import legendre_regressors, default_columns

from config import get_config


def make_forrest_regressors(sid, run):
    timing_dir = os.path.expanduser('~/movie_datasets/DBIC/forrest_20-1-1/events')
    df = pd.read_csv(f'{timing_dir}/sub-{sid}_ses-localizer_task-objectcategories_run-{run}_events.tsv', sep='\t')
    categories = ['body', 'face', 'house', 'object', 'scene', 'scramble']
    nt = 156
    tr = 2.0
    regs = np.zeros((nt, len(categories)))
    for i, cat in enumerate(categories):
        events = np.array(df[df['trial_type'] == cat][['onset', 'duration']]).T
        events= np.concatenate([events, np.ones((1, events.shape[1]))], axis=0)
        regs[:, i] = compute_regressor(
            events, 'spm', frametimes=(np.arange(nt)+0.5) * tr, oversampling=128)[0].ravel()
    regs = zscore(regs, axis=0)
    return regs


def make_forrest_nuisance_regressors(sid, run):
    nt = 156
    confounds_dir = os.path.expanduser('~/movie_datasets/DBIC/forrest_20-1-1/confounds')
    tar_fn = f'{confounds_dir}/{sid}_confounds.tar.lzma'
    tsv_fn = f'sub-{sid}_ses-localizer_task-objectcategories_run-{run}_desc-confounds_regressors.tsv'
    with tarfile.open(tar_fn, 'r') as tf:
        buffer = tf.extractfile(tsv_fn)
        df = pd.read_csv(buffer, delimiter='\t', na_values='n/a')
    keys = df.keys()

    for column in default_columns:
        if column not in keys:
            print(sid, run, column)

    regressors = [np.array(df[column]) for column in default_columns if column in keys]
    regressors = np.nan_to_num(np.stack(regressors, axis=1))
    regressors = np.hstack([legendre_regressors(polyord=2, n_tp=nt), regressors])
    assert np.all(regressors[:, 0] == 1)
    regressors[:, 1:] = np.nan_to_num(zscore(regressors[:, 1:], axis=0))
    return regressors


def fit_glm(ds, regs):
    beta, ss_r = np.linalg.lstsq(regs, ds, rcond=None)[:2]
    diff = ds - np.dot(regs, beta)
    sigma = np.sqrt(np.sum(diff**2, axis=0) / (ds.shape[0] - regs.shape[1]))
    cov = np.dot(regs.T, regs)
    inv = np.linalg.inv(cov)

    contrasts = [
        # 'body', 'face', 'house', 'object', 'scene', 'scramble'
        [ 1, 0, 0, 0, 0, 0],  # 0
        [ 0, 1, 0, 0, 0, 0],
        [ 0, 0, 1, 0, 0, 0],
        [ 0, 0, 0, 1, 0, 0],
        [ 0, 0, 0, 0, 1, 0],
        [ 0, 0, 0, 0, 0, 1],  # 5

        [ 5,-1,-1,-1,-1,-1],  # 6
        [-1, 5,-1,-1,-1,-1],
        [-1,-1, 5,-1,-1,-1],
        [-1,-1,-1, 5,-1,-1],
        [-1,-1,-1,-1, 5,-1],
        [-1,-1,-1,-1,-1, 5],  # 11

        [ 1, 0, 0,-1, 0, 0],  # 12
        [ 0, 1, 0,-1, 0, 0],
        [ 0, 0, 1,-1, 0, 0],
        [ 0, 0, 0,-1, 1, 0],
        [ 0, 0, 0, 1, 0,-1],  # 16
    ]

    betas = []
    ts = []
    ses = []
    for contrast in contrasts:
        R = np.array(contrast + [0] * (regs.shape[1] - len(contrast))).reshape((1, -1))
        mid = np.linalg.inv(R @ inv @ R.T)
        ratio = np.sqrt(float(mid)) / sigma
        R_beta = np.dot(R, beta).ravel()
        t = R_beta * ratio
        betas.append(R_beta)
        ts.append(t)
        ses.append( sigma / np.sqrt(float(mid)) )  # t = b / SE
    betas, ts, ses = np.array(betas), np.array(ts), np.array(ses)
    results = np.stack([betas, ts, ses], axis=1)
    return results


def compute_contrasts(dset, sid, lr):
    out_fn = f'lab/forrest/catmap/original/{sid}_{lr}h.npy'
    if os.path.exists(out_fn):
        return
    os.makedirs(os.path.dirname(out_fn), exist_ok=True)

    results = []
    runs = [1, 2, 3, 4]
    for run in runs:
        regs = make_forrest_regressors(sid, run)
        nuisance = make_forrest_nuisance_regressors(sid, run)
        regs = np.concatenate([regs, nuisance], axis=1)
        ds = dset.load_data(sid, lr, 'objectcategories', run)
        res = fit_glm(ds, regs)
        results.append(res)
    results = np.stack(results, axis=0)
    np.save(out_fn, results)
    print(datetime.now(), out_fn, results.shape)


def compute_contrasts_concat(dset, sid, lr):
    out_fn = f'../lab/forrest/catmap/original/{sid}_{lr}h_concat.npy'
    if os.path.exists(out_fn):
        return
    os.makedirs(os.path.dirname(out_fn), exist_ok=True)

    runs = [1, 2, 3, 4]
    ds = [dset.load_data(sid, lr, 'objectcategories', run) for run in runs]
    ds = np.concatenate(ds, axis=0)
    all_regs = []
    all_nuisance = []
    for i, run in enumerate(runs):
        regs = make_forrest_regressors(sid, run)
        nuisance = make_forrest_nuisance_regressors(sid, run)
        n = [np.zeros_like(nuisance) if j != i else nuisance
             for j in range(len(runs))]
        all_regs.append(regs)
        all_nuisance.append(np.concatenate(n, axis=1))
    all_regs = np.concatenate(all_regs, axis=0)
    all_nuisance = np.concatenate(all_nuisance, axis=0)

    regs = np.concatenate([all_regs, all_nuisance], axis=1)
    res = fit_glm(ds, regs)
    np.save(out_fn, res)
    print(datetime.now(), out_fn, res.shape)


if __name__ == '__main__':
    dset_name = 'forrest'
    dset, blocksize, buffersize, fold_funcs = get_config(dset_name)
    sids = dset.subject_sets['all']

    for sid in sids:
        for lr in 'lr':
            # compute_contrasts(dset, sid, lr)
            compute_contrasts_concat(dset, sid, lr)
            # exit(0)
