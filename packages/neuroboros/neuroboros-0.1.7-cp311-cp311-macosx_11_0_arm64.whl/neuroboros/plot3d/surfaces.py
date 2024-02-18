import os

import numpy as np
import vtk
from vtk.util import numpy_support

from ..io import DATA_ROOT

DEFAULT_LIGHTING = {'ambient': 0.6, 'diffuse': 0.3, 'specular': 0.1}


def load_vtp(fn):
    reader = vtk.vtkXMLPolyDataReader()
    reader.SetFileName(fn)
    reader.Update()
    surf = reader.GetOutput()
    return surf


class Surfaces(object):
    def __init__(self, surfaces, mapping_type, zoom=None, lighting=DEFAULT_LIGHTING):
        self.surfaces = surfaces
        self.mapping_type = mapping_type
        self.zoom = zoom
        self.lighting = lighting

    @classmethod
    def from_vtp(cls, fns, mapping_type, zoom, lighting):
        surfaces = []
        for fn in fns:
            surf = load_vtp(fn)
            surfaces.append(surf)
        instance = cls(
            surfaces=surfaces, mapping_type=mapping_type, zoom=zoom, lighting=lighting
        )
        return instance

    @property
    def focal_points(self):
        if not hasattr(self, '_focal_points'):
            self._focal_points = []
            for surf in self.surfaces:
                coords = numpy_support.vtk_to_numpy(surf.GetPoints().GetData())
                focal_point = list((coords.max(axis=0) + coords.min(axis=0)) * 0.5)
                self._focal_points.append(focal_point)
        return self._focal_points

    def add_colors(self, values, nan_value=0.7):
        for colors, surf in zip(values, self.surfaces):
            colors[np.isnan(colors)] = nan_value
            colors = (colors * 255).astype(int)
            Colors = vtk.vtkUnsignedCharArray()
            Colors.SetNumberOfComponents(3)
            Colors.SetName("Colors")
            for i in range(colors.shape[0]):
                c = colors[i, :]
                Colors.InsertNextTuple3(c[0], c[1], c[2])
            if self.mapping_type == 'vertex':
                surf.GetPointData().SetScalars(Colors)
            elif self.mapping_type == 'polygon':
                surf.GetCellData().SetScalars(Colors)
            surf.Modified()

    def get_actors(self, ambient=None, diffuse=None, specular=None):
        if ambient is None:
            ambient = self.lighting.get('ambient', 0.0)
        if diffuse is None:
            diffuse = self.lighting.get('diffuse', 0.0)
        if specular is None:
            specular = self.lighting.get('specular', 0.0)

        actors = []
        for surf in self.surfaces:
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputData(surf)
            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            actor.GetProperty().SetAmbient(ambient)
            actor.GetProperty().SetDiffuse(diffuse)
            actor.GetProperty().SetSpecular(specular)
            actors.append(actor)
        return actors


def get_surfaces(
    surf_type='inflated', mapping_type='polygon', lighting=DEFAULT_LIGHTING, zoom=None
):
    assert surf_type in [
        'pial',
        'midthickness',
        'white',
        'smoothwm',
        'inflated',
        'sphere',
    ]
    assert mapping_type in ['polygon', 'vertex']
    fns = [
        os.path.join(
            DATA_ROOT,
            'core',
            f'vtp_surfaces_{mapping_type}',
            'onavg-ico128',
            f'{lr}h_{surf_type}.vtp',
        )
        for lr in 'lr'
    ]
    d = {'inflated': 0.0136}
    # d = {'inflated': 0.0105}
    if zoom is None:
        zoom = d[surf_type] if surf_type in d else 0.0168
    surfaces = Surfaces.from_vtp(
        fns, mapping_type=mapping_type, zoom=zoom, lighting=lighting
    )
    return surfaces
