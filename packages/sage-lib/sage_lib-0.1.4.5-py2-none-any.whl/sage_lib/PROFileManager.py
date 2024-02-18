try:
    from sage_lib.FileManager import FileManager
except ImportError as e:
    import sys
    sys.stderr.write(f"Error importing FileManager: {e}\n")
    sys.exit(1)  # Exit if the FileManager is essential for DOSManager

try:
    import numpy as np
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys

class PROFileManager(FileManager):
    """
    The PROFileManager class manages the reading and interpreting of VASP's PROCAR file data.
    It extracts the k-points, band energies, occupations, and projections of wavefunctions onto atomic orbitals.
    """

    def __init__(self, file_location: str = None, name: str = None, **kwargs):
        """
        Initialize the PROFileManager with an optional file location and name.
        
        :param file_location: Path to the file containing PROCAR data.
        :param name: Descriptive name for the PROCAR data set.
        :param kwargs: Additional keyword arguments for the base FileManager class.
        """
        super().__init__(name=name, file_location=file_location)

        self.KPOINTS = None
        self.BANDS = None
        self.data = None

    def _read_band(self, band_lines:list, BAND_number:int, KPOINT_number:int):
        b0_split = band_lines[0].split()
        self.BANDS[KPOINT_number, BAND_number, :] = [ float(b0_split[4]), float(b0_split[7]) ]
        for ac in range(self.atomCount):
            self.data[KPOINT_number, BAND_number, ac] = list(map(float, band_lines[3+ac].split())) 

        band_lines[-1]

    def _read_kpoint(self, kpoint_lines:list, KPOINT_number:int, verbosity:bool=True):
        print( '>>', kpoint_lines[0] )
        k0_split = kpoint_lines[0].split()
        self.KPOINTS[KPOINT_number, :] = [ float(k0_split[3]), float(k0_split[4]), float(k0_split[5]), float(k0_split[8]) ]
        for bn in range(self.BANDS_number):
            self._read_band( kpoint_lines[2+(self.atomCount+5)*bn : 1+(self.atomCount+5)*(bn+1)], BAND_number=bn, KPOINT_number=KPOINT_number)

    def load(self, file_location:str=None) -> bool:
        """
        Load PROCAR data from a file specified by the file location.
        
        :param file_name: Path to the file to load. If None, defaults to initialized file location.
        """
        file_location = file_location if type(file_location) == str else self.file_location

        lines = [n for n in self.read_file(file_location) ]


        line1_vec = lines[1].strip().split()

        self._KPOINTS_number, self._BANDS_number, self._atomCount = int(line1_vec[3]), int(line1_vec[7]), int(line1_vec[11])

        print(f'Reanding : KPOINTS {self.KPOINTS_number} BANDS {self.BANDS_number} IONS {self.atomCount}')  

        self.KPOINTS = np.zeros((self.KPOINTS_number, 4))
        self.BANDS = np.zeros((self.KPOINTS_number, self.BANDS_number, 2))
        self.data = np.zeros((self.KPOINTS_number, self.BANDS_number, self.atomCount, 11))

        ac_bn = (self.atomCount+5)*(self.BANDS_number)
        for k in range(self.KPOINTS_number):
            self._read_kpoint( lines[3+(ac_bn+3)*k:(ac_bn+3)*(k+1)+1], KPOINT_number=k )

       	return True

'''
path = '/home/akaris/Documents/code/Physics/VASP/v6.1/files/PROCAR'
PF = PROFileManager( path+'/PROCAR' )
PF.load()

import matplotlib.pyplot as plt
plt.plot( PF.BANDS[:,:,0] - -1.60584051 )
plt.show()

PROCAR lm decomposed
# of k-points:  110         # of bands:  432         # of ions:   82

 k-point     1 :    0.00000000 0.00000000 0.00000000     weight = 0.00909091

band     1 # energy  -30.55092313 # occ.  1.00000000
 
ion      s     py     pz     px    dxy    dyz    dz2    dxz  x2-y2    tot
    1  0.000  0.000  0.000  0.000  0.000  0.000  0.000  0.000  0.000  0.000
    2  0.000  0.000  0.000  0.000  0.000  0.000  0.000  0.000  0.000  0.000
    3  0.000  0.000  0.000  0.000  0.000  0.000  0.000  0.000  0.000  0.000



   79  0.000  0.000  0.000  0.000  0.000  0.000  0.000  0.000  0.000  0.000
   80  0.000  0.000  0.000  0.000  0.000  0.000  0.000  0.000  0.000  0.000
   81  0.000  0.000  0.000  0.000  0.000  0.000  0.000  0.000  0.000  0.000
   82  0.000  0.000  0.000  0.000  0.000  0.000  0.000  0.000  0.000  0.000
tot    0.969  0.000  0.000  0.000  0.000  0.000  0.000  0.000  0.000  0.969
 
band     3 # energy  -30.18706277 # occ.  1.00000000
 
ion      s     py     pz     px    dxy    dyz    dz2    dxz  x2-y2    tot
    1  0.000  0.000  0.000  0.000  0.000  0.000  0.000  0.000  0.000  0.000
    2  0.000  0.000  0.000  0.000  0.000  0.000  0.000  0.000  0.000  0.000
    3  0.000  0.000  0.000  0.000  0.000  0.000  0.000  0.000  0.000  0.000
    4  0.000  0.000  0.000  0.000  0.000  0.000  0.000  0.000  0.000  0.000





   81  0.000  0.001  0.000  0.000  0.000  0.000  0.000  0.000  0.000  0.002
   82  0.000  0.000  0.000  0.001  0.000  0.000  0.000  0.000  0.000  0.001
tot    0.038  0.053  0.082  0.053  0.014  0.023  0.025  0.048  0.010  0.347
 

 k-point     2 :    0.02777778 0.00000000 0.00000000     weight = 0.00909091

band     1 # energy  -30.55091432 # occ.  1.00000000
 
ion      s     py     pz     px    dxy    dyz    dz2    dxz  x2-y2    tot
    1  0.000  0.000  0.000  0.000  0.000  0.000  0.000  0.000  0.000  0.000
    2  0.000  0.000  0.000  0.000  0.000  0.000  0.000 

'''