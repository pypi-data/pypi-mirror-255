# En __init__.py del paquete que contiene AtomPositionManager
try:
    from sage_lib.AtomPositionManager import AtomPositionManager
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing AtomPositionManager: {str(e)}\n")
    del sys

try:
    from sage_lib.NonPeriodicSystem import NonPeriodicSystem
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing NonPeriodicSystem: {str(e)}\n")
    del sys


try:
    import numpy as np
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys

class MoleculeBuilder(NonPeriodicSystem):
    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        super().__init__(name=name, file_location=file_location)

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
            'H2O': {'atomLabels': ['O', 'H', 'H'], 'atomPositions': [[0, 0, 0], [.9584 * np.sin(np.radians(1.045/2)), 0, -.9584 * np.cos(np.radians(1.045/2))], [-.9584 * np.sin(np.radians(1.045/2)), 0, -.9584 * np.cos(np.radians(1.045/2))]]},
            'SO2': {'atomLabels': ['S', 'O', 'O'], 'atomPositions': [[0, 0, 0], [1.57 * np.sin(np.radians(1.195/2)), 0, -1.57 * np.cos(np.radians(1.195/2))], [-1.57 * np.sin(np.radians(1.195/2)), 0, -1.57 * np.cos(np.radians(1.195/2))]]},
            'O3':  {'atomLabels': ['O', 'O', 'O'], 'atomPositions': [[0, 0, 0], [1.28 * np.sin(np.radians(1.168/2)), 0, -1.28 * np.cos(np.radians(1.168/2))], [-1.28 * np.sin(np.radians(1.168/2)), 0, -1.28 * np.cos(np.radians(1.168/2))]]},
            'HCN': {'atomLabels': ['H', 'C', 'N'], 'atomPositions': [[0, 0, 1.20], [0, 0, 0], [0, 0, -1.16]]}
                             }

    def build_molecule(self, atomLabels:list, atomPositions:np.array):
        self._atomPositions = self._atomPositions if self._atomPositions else [] 
        self._atomLabelsList = self._atomLabelsList if self._atomLabelsList else [] 
        self._atomicConstraints = self._atomicConstraints if self._atomicConstraints else [] 

        for al, ap in zip(atomLabels, atomPositions):
            self.add_atom(al, ap, [1,1,1])

    def build(self, name:str):

        if name in self.diatomic_compounds:
            atomLabels = self.diatomic_compounds[name]['atomLabels']
            atomPositions = self.diatomic_compounds[name]['atomPositions']
            self.build_molecule(atomLabels, atomPositions)

        if name in self.triatomic_compounds:
            atomLabels = self.triatomic_compounds[name]['atomLabels']
            atomPositions = self.triatomic_compounds[name]['atomPositions']
            self.build_molecule(atomLabels, atomPositions)


'''
mb = MoleculeBuilder()
mb.build('H2O')
print( mb.atomPositions )
'''