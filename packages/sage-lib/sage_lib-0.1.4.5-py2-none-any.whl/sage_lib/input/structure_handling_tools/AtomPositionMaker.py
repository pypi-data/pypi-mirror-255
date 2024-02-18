try:
    import numpy as np
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys


class AtomPositionMaker:
    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        #super().__init__(name=name, file_location=file_location)

        self._diatomic_compounds = {
            'H2':  {'atomLabels': ['H', 'H'],   'atomPositions': [[0, 0, 0], [0, 0,  .62]]},
            'O2':  {'atomLabels': ['O', 'O'],   'atomPositions': [[0, 0, 0], [0, 0, 1.32]]},
            'N2':  {'atomLabels': ['N', 'N'],   'atomPositions': [[0, 0, 0], [0, 0, 1.42]]},
            'F2':  {'atomLabels': ['F', 'F'],   'atomPositions': [[0, 0, 0], [0, 0, 1.14]]},
            'Cl2': {'atomLabels': ['Cl', 'Cl'], 'atomPositions': [[0, 0, 0], [0, 0, 2.04]]},
            'Br2': {'atomLabels': ['Br', 'Br'], 'atomPositions': [[0, 0, 0], [0, 0, 2.40]]},
            'I2':  {'atomLabels': ['I', 'I'],   'atomPositions': [[0, 0, 0], [0, 0, 2.78]]},
            'HF':  {'atomLabels': ['H', 'F'],   'atomPositions': [[0, 0, 0], [0, 0,  .88]]},
            'CO':  {'atomLabels': ['C', 'O'],   'atomPositions': [[0, 0, 0], [0, 0, 1.42]]},
            'NO':  {'atomLabels': ['N', 'O'],   'atomPositions': [[0, 0, 0], [0, 0, 1.37]]}
                            }
        self._triatomic_compounds = {
            'CO2': {'atomLabels': ['C', 'O', 'O'], 'atomPositions': [[0, 0, 0], [0, 0, 1.16], [0, 0, -1.16]]},
            'H2O': {'atomLabels': ['O', 'H', 'H'], 'atomPositions': [
                [                                   0, 0,                                    0], 
                [.9584 * np.cos(np.radians(104.5/2)), 0,  .9584 * np.sin(np.radians(104.5/2))], 
                [.9584 * np.cos(np.radians(104.5/2)), 0, -.9584 * np.sin(np.radians(104.5/2))]]},
            'SO2': {'atomLabels': ['S', 'O', 'O'], 'atomPositions': [[0, 0, 0], [1.57 * np.sin(np.radians(1.195/2)), 0, -1.57 * np.cos(np.radians(1.195/2))], [-1.57 * np.sin(np.radians(1.195/2)), 0, -1.57 * np.cos(np.radians(1.195/2))]]},
            'O3':  {'atomLabels': ['O', 'O', 'O'], 'atomPositions': [[0, 0, 0], [1.28 * np.sin(np.radians(1.168/2)), 0, -1.28 * np.cos(np.radians(1.168/2))], [-1.28 * np.sin(np.radians(1.168/2)), 0, -1.28 * np.cos(np.radians(1.168/2))]]},
            'HCN': {'atomLabels': ['H', 'C', 'N'], 'atomPositions': [[0, 0, 1.20], [0, 0, 0], [0, 0, -1.16]]}
                             }

    def get_triatomic_compound(self, name):
        return self._triatomic_compounds.get(name, None)

    def build_molecule(self, atomLabels:list, atomPositions:np.array, center:str='mass_center'):
        '''
        '''
        for al, ap in zip(atomLabels, atomPositions):
            self.add_atom(al, ap, [1,1,1])

        if center == 'mass_center' or center == 'gravity_center':
            displacement = np.sum(self.atomPositions.T * self.mass_list, axis=1) /  np.sum(self.mass_list)

        elif center == 'geometric_center' or center == 'baricenter':
            displacement = np.mean(self.atomPositions, axis=1)

        else:
            displacement = np.array([0,0,0])

        self.set_atomPositions(self.atomPositions-displacement)

    def build(self, name:str):
        '''
        '''
        if name in self.diatomic_compounds:
            atomLabels = self.diatomic_compounds[name]['atomLabels']
            atomPositions = self.diatomic_compounds[name]['atomPositions']

        if name in self.triatomic_compounds:
            atomLabels = self.triatomic_compounds[name]['atomLabels']
            atomPositions = self.triatomic_compounds[name]['atomPositions']
        
        self.build_molecule(atomLabels, atomPositions)


'''
a = AtomPositionMaker()
print( a.get_triatomic_compound('H2O') )
    def molecules_for_target_density(
        existing_molecules,
        solvent_molecule,
        target_density,
        boxsize):
        """Calculate how many solvent molecules to add to reach target density

        Parameters
        ----------
        existing_molecules : dict
           mapping of AtomGroups to number in box
        solvent_molecule : AtomGroup
           solvent molecule you want to add
        target_density : float
           target system density in kg/m3
        boxsize : 3 floats
           boxsize in each dimension in Angstrom

        Returns
        -------
        nsolvent, density
          number of solvent molecules to add, resulting density

        Example
        -------
        To find how many water molecules to solvate our protein to a density of
        985 kg/m^3.  We load AtomGroups "protein" and "water" (making sure that
        the mass is correct for these).  We specify that there will be 1 protein
        molecule in the box, and the solvent is the water AtomGroup.  We then
        pass the density and size of our box (20x20x20 is this example)::

           >>> molecules_for_target_density({protein: 1}, water,
                                            985.0, [20.0, 20.0, 20.0])
        """
        # system volume

        vol = boxsize[0] * boxsize[1] * boxsize[2] * 10 ** -30

        target_mass = target_density * vol  # kg

        existing_mass = sum(mol.total_mass() * quantity
                           for mol, quantity in existing_molecules.items())
        # from g/mol to kg
        existing_mass /= 1000 * N_A

        required_mass = target_mass - existing_mass

        solvent_mass = solvent_molecule.total_mass() / (1000 * N_A)

        nreq = int(required_mass / solvent_mass)
        # calculate resulting density as a check
        actual_density = (existing_mass + nreq * solvent_mass) / vol

        return nreq, actual_density
'''