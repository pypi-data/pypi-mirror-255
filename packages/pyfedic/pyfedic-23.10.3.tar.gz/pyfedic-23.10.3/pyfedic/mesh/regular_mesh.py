import numpy as np
from functools import cache

from ..cells import Q4, C8
from .base_mesh import BaseMesh

class RegularBaseMesh(BaseMesh):
    """

    """

    def __init__(self, xlims, ylims, zlims=None, elt_size=16):
        ""

        if zlims is None:
            nex, ney = int(np.diff(xlims) // elt_size), int(np.diff(ylims) // elt_size)
            nnx, nny = nex+1, ney+1
            c00 = np.array([0, 1, nnx+1, nnx])
            c0 = np.arange(nex).repeat(4).reshape(nex,4) + c00.reshape(1,4).repeat(nex, axis=0)
            cell_type = Q4
            cells = np.arange(ney).repeat(4*nex).reshape(nex*ney,4)*nnx + np.tile(c0, (ney, 1))
        else:
            nex, ney, nez = int(np.diff(xlims) // elt_size), int(np.diff(ylims) // elt_size), int(np.diff(zlims) // elt_size)
            nnx, nny, nnz = nex+1, ney+1, nez+1
            c000 = np.array([0, 1, nnx+1, nnx, nnx*nny, nnx*nny+1, nnx*nny+nnx+1, nnx*nny+nnx])
            c00 = np.arange(nex).repeat(8).reshape(nex,8) + c000.reshape(1,8).repeat(nex, axis=0)
            c0 = np.arange(ney).repeat(8*nex).reshape(nex*ney,8)*nnx + np.tile(c00, (ney, 1))
            cell_type = C8
            cells = np.arange(nez).repeat(8*nex*ney).reshape(nex*ney*nez,8)*nnx*nny + np.tile(c0, (nez, 1))

        xn = np.round(np.arange(nnx)*elt_size+xlims[0]+((xlims[1]-xlims[0]) % elt_size)/2)-0.5
        yn = np.round(np.arange(nny)*elt_size+ylims[0]+((ylims[1]-ylims[0]) % elt_size)/2)-0.5
        if zlims is None:
            zn = [0]
            regular = (ney, nex), elt_size
        else:
            zn = np.round(np.arange(nnz)*elt_size+zlims[0]+((zlims[1]-zlims[0]) % elt_size)/2)-0.5
            regular = (nez, ney, nex), elt_size

        zn, yn, xn = np.meshgrid(zn, yn, xn, indexing='ij')
        nodes = np.vstack((xn.flat, yn.flat, zn.flat)).T

        super().__init__(nodes, cells, cell_type)
        self.regular = regular

    @cache
    def _get_regular_base(self):
        ndim = self.ndim
        nelems, elt_size = self.regular
        pix_coords = np.mgrid[(slice(0,elt_size),)*ndim].reshape((ndim, elt_size**ndim)).T
        coords = ((pix_coords - (elt_size-1)/2)*2/elt_size)[:,::-1]
        Ne = self.cell_type.N(coords).astype('f4').reshape((self.cell_type.n_nodes, elt_size**ndim))
        coefs = np.array([np.prod(np.array(nelems)[idim+1:]*elt_size) for idim in range(ndim)])

        return pix_coords, Ne, coefs

    def iter_Nc(self):
        nelems, elt_size = self.regular
        n = len(nelems)
        mv = nelems[::-1]
        ks = [0]*n
        while True:
            if ks[n-1] >= mv[n-1]:
                break
            yield np.array(ks[::-1])*elt_size
            ks[0] += 1
            for i in range(n-1):
                if ks[i] >= mv[i]:
                    ks[i] = 0
                    ks[i+1] += 1
