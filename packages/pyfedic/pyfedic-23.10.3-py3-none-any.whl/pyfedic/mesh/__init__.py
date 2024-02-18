# -*- coding: utf-8 -*-
"""

The :py:class:`pyFEDIC.mesh.Mesh` object is a key element for **pyFEDIC** but can also be used for other purposes like reading
and vritting ``.vtk`` file or do some finite element manipulation using the shape function to interpolate values.

You can build automatically a mesh using :py:meth:`pyFEDIC.mesh.gen_mesh` or load a mesh using :py:meth:`pyFEDIC.io.read_mesh`.

"""


from .base_mesh import BaseMesh
from .composite_mesh import CompositeBaseMesh
from .regular_mesh import RegularBaseMesh
from .image_mesh import ImageMesh

class Mesh(BaseMesh, ImageMesh):
    """
    """

    def __init__(self, nodes, cells, cell_type, nodes_ids=None):
        BaseMesh.__init__(self, nodes, cells, cell_type, nodes_ids)
        ImageMesh.__init__(self)

class RegularMesh(RegularBaseMesh, ImageMesh):
    """
    """

    def __init__(self, xlims, ylims, zlims=None, elt_size=16):
        RegularBaseMesh.__init__(self, xlims, ylims, zlims, elt_size)
        ImageMesh.__init__(self)

class CompositeMesh(CompositeBaseMesh, ImageMesh):
    """
    """

    def __init__(self, nodes, cells_by_type, nodes_ids=None):
        CompositeBaseMesh.__init__(self, nodes, cells_by_type, nodes_ids)
        ImageMesh.__init__(self)

def gen_mesh(xlims, ylims, zlims=None, elt_size=16, adjust_to_roi=False):
    #
    import numpy as np

    mesh = RegularMesh(xlims, ylims, zlims, elt_size)

    if adjust_to_roi:
        nn = [ne+1 for ne in mesh.regular[0]]
        xn = np.linspace(xlims[0], xlims[1], nn[0])
        yn = np.linspace(ylims[0], ylims[1], nn[1])
        if zlims is None:
            zn = [0]
        else:
            zn = np.linspace(zlims[0], zlims[1], nn[2])

        zn, yn, xn = np.meshgrid(zn, yn, xn, indexing='ij')
        nodes = np.vstack((xn.flat, yn.flat, zn.flat)).T
        mesh = Mesh(mesh.cells, nodes)

    return mesh

__all__ = [
    'Mesh',
    'CompositeMesh',
    'RegularMesh',
    'gen_mesh'
]
