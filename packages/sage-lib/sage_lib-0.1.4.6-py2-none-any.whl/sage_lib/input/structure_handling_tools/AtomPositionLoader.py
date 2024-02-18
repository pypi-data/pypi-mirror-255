try:
    import numpy as np
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys

try:
    from sage_lib.input.structure_handling_tools.structural_file_readers.CIF import CIF
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing sage_lib.input.structure_handling_tools.structural_file_readers.CIF: {str(e)}\n")
    del sys

try:
    from sage_lib.input.structure_handling_tools.structural_file_readers.PDB import PDB
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing sage_lib.input.structure_handling_tools.structural_file_readers.PDB: {str(e)}\n")
    del sys

try:
    from sage_lib.input.structure_handling_tools.structural_file_readers.POSCAR import POSCAR
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing sage_lib.input.structure_handling_tools.structural_file_readers.POSCAR: {str(e)}\n")
    del sys

try:
    from sage_lib.input.structure_handling_tools.structural_file_readers.XYZ import XYZ
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing sage_lib.input.structure_handling_tools.structural_file_readers.XYZ: {str(e)}\n")
    del sys

try:
    from sage_lib.input.structure_handling_tools.structural_file_readers.SI import SI
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing sage_lib.input.structure_handling_tools.structural_file_readers.SI: {str(e)}\n")
    del sys

try:
    from sage_lib.input.structure_handling_tools.structural_file_readers.ASE import ASE
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing sage_lib.input.structure_handling_tools.structural_file_readers.ASE: {str(e)}\n")
    del sys
    
try:
    from sage_lib.input.structure_handling_tools.structural_file_readers.AIMS import AIMS
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing sage_lib.input.structure_handling_tools.structural_file_readers.AIMS: {str(e)}\n")
    del sys

class AtomPositionLoader(CIF, POSCAR, XYZ, SI, PDB, ASE, AIMS):
    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        CIF.__init__(self, name=name, file_location=file_location)
        POSCAR.__init__(self, name=name, file_location=file_location)
        XYZ.__init__(self, name=name, file_location=file_location)
        SI.__init__(self, name=name, file_location=file_location)
        PDB.__init__(self, name=name, file_location=file_location)
        ASE.__init__(self, name=name, file_location=file_location)
        AIMS.__init__(self, name=name, file_location=file_location)

        self._comment = None
        self._atomCount = None  # N total number of atoms

        self.export_dict = {
                            'VASP': 'export_as_VASP',
                            'AIMS': 'export_as_AIMS',
                            }
                            
    def read(self, source:str='VASP', file_location:str=None):
        metodo = getattr(self, self.export_dict[source], None)
        if callable(metodo):
            metodo(file_location)
        else:
            print(f"Metodo '{self.export_dict[source]}' no encontrado.")

    def export(self, source:str='VASP', file_location:str=None):
        metodo = getattr(self, self.export_dict[source], None)
        if callable(metodo):
            metodo(file_location)
        else:
            print(f"Metodo '{self.export_dict[source]}' no encontrado.")
  
'''
a = AtomPositionLoader('/home/akaris/Documents/code/Physics/VASP/v6.2/files/dataset/CoFeNiOOH_jingzhu/bulk_NiFe/POSCAR')
a.read_POSCAR()
#print(AtomPositionLoader.__mro__)
'''