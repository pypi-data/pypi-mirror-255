try:
    import numpy as np
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys


class AtomPositionMaker:
    """
    A class to build and manipulate molecular structures, particularly diatomic and triatomic compounds.

    Attributes:
        _diatomic_compounds (dict): A dictionary containing information about various diatomic compounds.
        _triatomic_compounds (dict): A dictionary containing information about various triatomic compounds.

    Methods:
        get_triatomic_compound(name): Retrieves the information of a triatomic compound based on its name.
        build_molecule(atomLabels, atomPositions, center): Constructs a molecule from atom labels and positions.
        build(name): Builds a molecule based on the given name, looking up its structure from predefined compounds.
    """

    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        """
        Initializes the AtomPositionMaker class.

        Args:
            file_location (str, optional): The location of a file containing molecular data.
            name (str, optional): The name of the molecule.

        The class also accepts additional keyword arguments (**kwargs) for future extensions.
        """

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
        """
        Retrieves the information of a specified triatomic compound.

        Args:
            name (str): The name of the triatomic compound.

        Returns:
            dict: A dictionary containing the atom labels and positions of the compound, or None if not found.
        """
        return self._triatomic_compounds.get(name, None)

    def build_molecule(self, atomLabels:list, atomPositions:np.array, center:str='mass_center'):
        """
        Constructs a molecule from provided atom labels and positions, and aligns it based on the specified center.

        Args:
            atomLabels (list): A list of atom labels.
            atomPositions (np.array): A NumPy array of atom positions.
            center (str): The centering method to be used for the molecule ('mass_center', 'gravity_center', 'geometric_center', or 'baricenter').

        This function adds atoms to the molecule, calculates the displacement based on the chosen centering method, and aligns the molecule accordingly.
        """
        # Add atoms to the molecule
        for al, ap in zip(atomLabels, atomPositions):
            self.add_atom(al, ap, [1,1,1])

        # Calculate displacement based on the centering method
        if center == 'mass_center' or center == 'gravity_center':
            displacement = np.sum(self.atomPositions.T * self.mass_list, axis=1) /  np.sum(self.mass_list)

        elif center == 'geometric_center' or center == 'baricenter':
            displacement = np.mean(self.atomPositions, axis=1)
        
        else:
            displacement = np.array([0,0,0])

        # Align the molecule by adjusting atom positions
        self.set_atomPositions(self.atomPositions-displacement)

    def build(self, name:str):
        """
        Builds a molecule based on the given name.

        Args:
            name (str): The name of the molecule to be built.

        This method looks up the molecule's structure from predefined compounds and constructs it.
        """
        if name in self.diatomic_compounds:
            atomLabels = self.diatomic_compounds[name]['atomLabels']
            atomPositions = self.diatomic_compounds[name]['atomPositions']

        if name in self.triatomic_compounds:
            atomLabels = self.triatomic_compounds[name]['atomLabels']
            atomPositions = self.triatomic_compounds[name]['atomPositions']
        
        self.build_molecule(atomLabels, atomPositions)

