"""
Author: Anoop Ajaya Kumar Nair
Date: 2023-10-24
Description: Code calculates:
    - Density cube
    - Quadrupole

Contact Details:
- Email: mailanoopanair@gmail.com
- Company: University of Iceland
- Job Title: Doctoral researcher
"""

import numpy
from pyscf import lib
from pyscf.dft import numint, gen_grid
from pyscf import __config__

RESOLUTION = getattr(__config__, 'cubegen_resolution', None)
BOX_MARGIN = getattr(__config__, 'cubegen_box_margin', 10.0)
ORIGIN = getattr(__config__, 'cubegen_box_origin', None)
EXTENT = getattr(__config__, 'cubegen_box_extent', None)
import numpy as np


class Cube(object):
    def __init__(self, mol, nx=80, ny=80, nz=80, resolution=RESOLUTION,
                 margin=BOX_MARGIN, origin=ORIGIN, extent=EXTENT):
        from pyscf.pbc.gto import Cell
        self.mol = mol
        coord = mol.atom_coords()
        # print(coord)

        if isinstance(mol, Cell):
            self.box = mol.lattice_vectors()
            atom_center = (numpy.max(coord, axis=0) + numpy.min(coord, axis=0))/2
            box_center = (self.box[0] + self.box[1] + self.box[2])/2
            self.boxorig = atom_center - box_center
        else:
            
            if extent is None:
                extent = numpy.max(coord, axis=0) - numpy.min(coord, axis=0) + 2*margin
                extent.fill(np.max(extent))

            self.box = numpy.diag(extent)
            if origin is None:
                origin = np.zeros(3)
                origin.fill(numpy.min(coord) - margin)
            self.boxorig = numpy.asarray(origin)

        if resolution is not None:
            nx, ny, nz = numpy.ceil(numpy.diag(self.box) / resolution).astype(int)

        self.nx = nx
        self.ny = ny
        self.nz = nz

        if isinstance(mol, Cell):
            # Use an asymmetric mesh for tiling unit cells
            self.xs = numpy.linspace(0, 1, nx, endpoint=False)
            self.ys = numpy.linspace(0, 1, ny, endpoint=False)
            self.zs = numpy.linspace(0, 1, nz, endpoint=False)
        else:
            self.xs = numpy.linspace(0, 1, nx, endpoint=True)
            self.ys = numpy.linspace(0, 1, ny, endpoint=True)
            self.zs = numpy.linspace(0, 1, nz, endpoint=True)


    def get_coords(self) :
        """  Result: set of coordinates to compute a field which is to be stored
        in the file.
        """
        frac_coords = lib.cartesian_prod([self.xs, self.ys, self.zs])
        return frac_coords @ self.box + self.boxorig # Convert fractional coordinates to real-space coordinates

    def get_ngrids(self):
        return self.nx * self.ny * self.nz

    def get_volume_element(self):
        return (self.xs[1]-self.xs[0])*(self.ys[1]-self.ys[0])*(self.zs[1]-self.zs[0])






def density(mol, dm, outfile=None, nx=80, ny=80, nz=80,  resolution=RESOLUTION,
            margin=BOX_MARGIN):

    from pyscf.pbc.gto import Cell
    cc = Cube(mol, nx, ny, nz, resolution, margin)

    GTOval = 'GTOval'
    if isinstance(mol, Cell):
        GTOval = 'PBC' + GTOval

    # Compute density on the .cube grid
    coords = cc.get_coords()
    ngrids = cc.get_ngrids()
    coordMod = coords.reshape(nx, ny, nz,3)

    h_v = np.zeros(3)
    hv1 = coordMod[0,0,0]-coordMod[1,0,0]
    hv2 = coordMod[0,0,0]-coordMod[0,1,0]
    hv3 = coordMod[0,0,0]-coordMod[0,0,1]
    h_v[0] = abs(hv1[0])
    h_v[1] = abs(hv2[1])
    h_v[2] = abs(hv3[2])



    blksize = min(8000, ngrids)
    rho = numpy.empty(ngrids)
    for ip0, ip1 in lib.prange(0, ngrids, blksize):
        ao = mol.eval_gto(GTOval, coords[ip0:ip1])
        rho[ip0:ip1] = numint.eval_rho(mol, ao, dm)
    rho = rho.reshape(cc.nx,cc.ny,cc.nz)

    # Write out density to the .cube file
    if outfile !=None:
        cc.write(rho, outfile, comment='Electron density in real space (e/Bohr^3)')
    return rho,[nx,ny,nz],h_v,coordMod

def quadpoleElect(h_v,R_v,rho,n,coordMod):

    dV = h_v[0] * h_v[1] * h_v[2] #done

    Q_ab = np.zeros(6)
    for i in range(0,n[0]):
        x = i * h_v[0]
        for j in range(0,n[1]):
            y = j* h_v[1]
            for k in range(0,n[2]):
                z = k * h_v[2]
                r = np.zeros(3)
                r[0] = coordMod[i,j,k,0] - R_v[0]
                r[1] = coordMod[i,j,k,1] - R_v[1] 
                r[2] = coordMod[i,j,k,2] - R_v[2] 
                rr = (r[0] * r[0] + r[1] * r[1] + r[2] * r[2])
                rq = rr / 3.0
                cd = rho[i,j,k] * dV

                cq = cd * 3.0 / 2.0
                Q_ab[0] += cq * (r[0] * r[0] - rq)
                Q_ab[1] += cq * r[0] * r[1]
                Q_ab[2] += cq * r[0] * r[2]
                Q_ab[3] += cq * (r[1] * r[1] - rq)
                Q_ab[4] += cq * r[1] * r[2]
                Q_ab[5] += cq * (r[2] * r[2] - rq)
    quadPole = np.zeros((3,3))
    quadPole[0,0] = Q_ab[0] 
    quadPole[0,1] = quadPole[1,0] =  Q_ab[1] 
    quadPole[0,2] = quadPole[2,0] =  Q_ab[2] 
    quadPole[1,1] = Q_ab[3] 
    quadPole[1,2] = quadPole[2,1] =  Q_ab[4] 
    quadPole[2,2] = Q_ab[5] 
    return quadPole


def calcCOM(mol):
    atomicMass  = mol.atom_mass_list()
    atomicPos   = mol.atom_coords(unit = 'Bohr')
    Com = np.matmul(atomicMass.reshape(1,-1),atomicPos.reshape(-1,3))/atomicMass.sum()
    return Com[0]

def quadpoleNuc(mol):
    charges = mol.atom_charges()
    coords = mol.atom_coords(unit = 'Bohr')
    COM = calcCOM(mol)
    coordsMod = coords-COM
    # print("qcoord",coordsMod)

    rval = np.sum(np.square(coordsMod),axis=1)
    Quad  = np.zeros((3,3))
    for i in range(len(charges)):
        rvalDiag = np.zeros((3,3))
        rvalDiag[0,0] =  -rval[i]/2.0
        rvalDiag[1,1] =  -rval[i]/2.0
        rvalDiag[2,2] =  -rval[i]/2.0
        Quad += charges[i]*(3.0/2.0*np.outer(coordsMod[i],coordsMod[i])+rvalDiag)

 
    return Quad

def Quadrupole(mol,mf):
    quad_Nuc1 = quadpoleNuc(mol)
    R_v = calcCOM(mol)
    rho,n,h_v,coordMod = density(mol, mf.make_rdm1())
    Qelect1 = quadpoleElect(h_v,R_v,rho,n,coordMod)
    Qxx = np.round(quad_Nuc1-Qelect1,4)
    return Qxx





