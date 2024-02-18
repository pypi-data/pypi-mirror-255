try:
    from sage_lib.master.FileManager import FileManager
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing FileManager: {str(e)}\n")
    del sys

try:
    from sage_lib.master.AtomicProperties import AtomicProperties
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing AtomicProperties: {str(e)}\n")
    del sys

try:
    import numpy as np
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys

try:
    import re
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing re: {str(e)}\n")
    del sys

class PDB(FileManager, AtomicProperties):
    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        FileManager.__init__(self, name=name, file_location=file_location)
        AtomicProperties.__init__(self)

    def export_as_PDB(self, file_location:str=None, bond_distance:float=None, save_to_file:str='w', bond_factor:float=None, verbose:bool=False) -> str:
        file_location  = file_location  if not file_location  is None else self.file_location+'config.pdb' if type(self.file_location) is str else self.file_location
        bond_factor = bond_factor if bond_factor is not None else 1.1    

        if verbose: print(f' >> Export as PDB >> {file_location}')

        pdb_str = ''
        for A, position_A in enumerate(self.atomPositions):     #loop over different atoms
            pdb_str += "ATOM  %5d %2s   MOL     1  %8.3f%8.3f%8.3f  1.00  0.00\n" % (int(A+1), self.atomLabelsList[A], position_A[0], position_A[1], position_A[2])

        for A, position_A in enumerate(self.atomPositions):       #loop over different atoms
            for B, position_B in enumerate(self.atomPositions):
                AB_bond_distance = float(bond_distance) if bond_distance is not None else (self.covalent_radii[self.atomLabelsList[A]] + self.covalent_radii[self.atomLabelsList[B]]) * bond_factor
                if  A>B and np.linalg.norm(position_A-position_B) < AB_bond_distance:
                    pdb_str += f'CONECT{int(A+1):>5}{int(B+1):>5}\n'
                    
        # Save the generated XYZ content to a file if file_location is specified and save_to_file is True
        if file_location and save_to_file:
            with open(file_location, save_to_file) as f:
                f.write(pdb_str)
            if verbose:
                print(f"XYZ content has been saved to {file_location}")

        return True
    