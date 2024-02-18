# Molecular Moments and Polarizabilities Calculator

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

![HMPOLImage](./img/HMpolImg.jpg)
## Overview

The Python code is designed for calculating higher-order moments and polarizabilities of small molecules. It is a versatile tool that provides insights into the molecular properties essential for understanding electronic structure and molecular interactions. The moments and polarizabilites so calculated are used as the parameter sets for the SCME code. 

## Features

### Moments Calculation
- **Dipole Moment:** Measure of the separation of positive and negative charges within a molecule.
- **Quadrupole Moment:** Describes the distribution of charge within a molecule in terms of quadrupole tensors.
- **Octapole Moment:** Characterizes higher-order charge distributions beyond quadrupoles.
- **Hexadecapole Moment:** Captures even higher-order charge distributions, providing a comprehensive view of molecular charge.

### Polarizabilities Calculation
- **Dipole-Dipole Polarizability:** Reflects the ability of a molecule to induce a dipole moment in an adjacent molecule.
- **Dipole-Quadrupole Polarizability:** Measures the interaction between the dipole moment of one molecule and the quadrupole moment of another.
- **Quadrupole-Quadrupole Polarizability:** Quantifies the influence of quadrupole moments on the polarization of adjacent molecules.

## How to Use

1. **Installation:**
    ```bash
    pip install molecular-moments-polarizabilities-calculator
    ```

2. **Usage:**
    ```python
    from molecular_calculator import MolecularPropertiesCalculator

    # Create a molecule object
    molecule = MolecularPropertiesCalculator(molecule_structure)

    # Calculate moments
    dipole = molecule.calculate_dipole_moment()
    quadrupole = molecule.calculate_quadrupole_moment()
    octapole = molecule.calculate_octapole_moment()
    hexadecapole = molecule.calculate_hexadecapole_moment()

    # Calculate polarizabilities
    dipole_dipole_polarizability = molecule.calculate_dipole_dipole_polarizability()
    dipole_quadrupole_polarizability = molecule.calculate_dipole_quadrupole_polarizability()
    quadrupole_quadrupole_polarizability = molecule.calculate_quadrupole_quadrupole_polarizability()
    ```

## Example

```python
from molecular_calculator import MolecularPropertiesCalculator

# Define a water molecule
water_structure = {
    'atoms': ['O', 'H', 'H'],
    'coordinates': [
        [0.000, 0.000, 0.000],
        [0.758, 0.586, 0.000],
        [-0.758, 0.586, 0.000]
    ]
}

# Create a molecule object
water_molecule = MolecularPropertiesCalculator(water_structure)

# Calculate moments
dipole_moment = water_molecule.calculate_dipole_moment()
quadrupole_moment = water_molecule.calculate_quadrupole_moment()

# Calculate polarizabilities
dipole_dipole_polarizability = water_molecule.calculate_dipole_dipole_polarizability()
dipole_quadrupole_polarizability = water_molecule.calculate_dipole_quadrupole_polarizability()

print(f"Dipole Moment: {dipole_moment} Debye")
print(f"Quadrupole Moment: {quadrupole_moment} Debye*angstrom")
print(f"Dipole-Dipole Polarizability: {dipole_dipole_polarizability} Debye^2")
print(f"Dipole-Quadrupole Polarizability: {dipole_quadrupole_polarizability} Debye^3*Å^2")
