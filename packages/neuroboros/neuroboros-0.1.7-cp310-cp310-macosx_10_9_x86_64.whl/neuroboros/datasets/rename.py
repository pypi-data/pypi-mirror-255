import os
from glob import glob

if __name__ == '__main__':
    fns = sorted(glob(os.path.join('*', 'resampled', '*', '*', '*', 'sub-*.npy')))
    print(len(fns))
    for fn in fns:
        parts = []
        head = fn
        while head:
            head, tail = os.path.split(head)
            parts.insert(0, tail)
        fmriprep_version, _, space, structure, resample, basename = parts
        d = {}
        parts = basename[:-4].split('_')
        for p in parts:
            name, val = p.split('-')
            d[name] = val
        assert len(d) == 2
        assert d['task'] == 'rest'
        out_basename = f"sub-{d['sub']}_task-{d['task']}_run-01.npy"
        out_fn = os.path.join(
            fmriprep_version, 'renamed', space, structure, resample, out_basename
        )
        relpath = os.path.relpath(fn, os.path.dirname(out_fn))
        print(relpath)
        os.makedirs(os.path.dirname(out_fn), exist_ok=True)
        if not os.path.lexists(out_fn):
            os.symlink(relpath, out_fn)

    fns = sorted(
        glob(os.path.join('*', 'confounds', 'sub-*.npy'))
        + glob(os.path.join('*', 'confounds', 'sub-*.tsv'))
    )
    print(len(fns))
    for fn in fns:
        parts = []
        head = fn
        while head:
            head, tail = os.path.split(head)
            parts.insert(0, tail)
        print(parts)
        fmriprep_version, _, basename = parts
        d = {}
        parts = basename[:-4].split('_')
        for p in parts:
            if '-' not in p:
                assert p == 'timeseries'
                continue
            name, val = p.split('-')
            d[name] = val
        assert len(d) == 3
        assert d['task'] == 'rest'
        out_basename = (
            f"sub-{d['sub']}_task-{d['task']}_run-01_desc-{d['desc']}_timeseries"
            + os.path.splitext(fn)[1]
        )
        out_fn = os.path.join(fmriprep_version, 'renamed_confounds', out_basename)
        relpath = os.path.relpath(fn, os.path.dirname(out_fn))
        print(relpath)
        os.makedirs(os.path.dirname(out_fn), exist_ok=True)
        if not os.path.lexists(out_fn):
            os.symlink(relpath, out_fn)
