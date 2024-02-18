from pyscf import gto
from ase.io import read
from poltensor import Pols
import numpy as np
from ase.visualize import view


mol = gto.Mole()
molecule = read("monomerA.xyz")
print(molecule.get_positions() + 7*np.ones(3))

# view(molecule)


molecule.set_positions(molecule.get_positions() + 7*np.ones(3))

# view(molecule)
# molecule.set_positions(molecule.get_positions()-np.ones(3))
mol.atom = "monomerA.xyz" 
mol.basis = "augccpvqz"
mol.build()

pols = Pols(molecule,mol, irrep=False)

# print(pols.calcAijk())
print(pols.calc_dd_pol())
print(pols.calc_dq_pol())
print(pols.calc_qq_pol())