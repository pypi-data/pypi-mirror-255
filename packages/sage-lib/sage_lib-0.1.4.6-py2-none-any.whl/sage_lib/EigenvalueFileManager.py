try:
    from sage_lib.FileManager import FileManager
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing FileManager: {str(e)}\n")
    del sys

try:
    import numpy as np
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys

try:
    import json
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing json: {str(e)}\n")
    del sys

class EigenvalueFileManager(FileManager):
    def __init__(self, file_location:str=None, name:str=None, cell:np.array=None, fermi:float=None, **kwargs):
        """
        Initialize OutFileManager class.
        :param file_location: Location of the file to be read.
        :param name: Name identifier for the file.
        :param kwargs: Additional keyword arguments.
        """
        super().__init__(name=name, file_location=file_location)
        self._comment = None

        self._bands = None
        self._kpoints = None
        self._k_distance = None

        self._fermi = fermi
        self._cell = cell

    @property
    def cell(self):
        if self._cell is not None:
            return np.array(self._cell, dtype=np.float64)
        else:
            return None

    def read_EIGENVAL(self, file_location:str=None):
        file_location = file_location if type(file_location) == str else self._file_location
        lines = [n for n in self.read_file(file_location) ]
        
        self.bands, self.kpoints=[], []
        var = -1
        for i, n in enumerate(lines):

            vec = [float(m) for m in n.split(' ') if self.is_number(m) ] 
            if i == 5: self.bands = np.zeros((int(vec[1]), int(vec[2]), 4))
            if len(vec) == 4 and i>5: self.kpoints.append(vec); var+=1
            if len(vec) == 5 and i>5: self.bands[var,int(vec[0]-1), :] = vec[1:]

        self.k_distance = np.zeros((len(self.kpoints)))
        var = 0
        for n in range(len(self.k_distance)-1): 
            var += ((self.kpoints[n][0]-self.kpoints[n+1][0])**2+(self.kpoints[n][1]-self.kpoints[n+1][1])**2+(self.kpoints[n][2]-self.kpoints[n+1][2])**2)**0.5
            self.k_distance[n+1] = var

        self.kpoints = np.array(self.kpoints)
        self.bands = np.array(self.bands)
        self.k_distance = np.array(self.k_distance)

        return True

    def _ndarray_2_list(self, array):
        return [list(array.shape), str(array.dtype), list(array.flatten(order='C'))]

    def _ndarray_2_dict(self, array):
        return {'__ndarray__':self._ndarray_2_list(array)}

    def _get_specialpoints(self, kpoints:np.array) -> list:
        """Check if points in a kpoints matrix exist in a lattice points dictionary."""
        found_points = []

        for point in kpoints:
            for label, special_lattice_point in self.special_lattice_points.items():
                # Compare only the first three elements (x, y, z coordinates)
                if self.is_close(point[:3], special_lattice_point[:3]):
                    found_points.append( label )
                    break

        return found_points
    
    def _subtract_fermi(self, fermi:float=None):
        fermi = fermi if fermi is not None else self.fermi 

        self.bands[:,:,:2] -= fermi 
        self.fermi = 0
        
        return True

    def _transform_bands(self, bands:np.array=None):
        bands = bands if bands is not None else self.bands[:,:,:1] if self.bands.shape[2] == 1 else self.bands[:,:,:2] 
        return matrix.reshape(1, *bands.shape) if bands.ndim == 2 else (bands.transpose(2, 0, 1).reshape(2, *bands.shape[:2]) if bands.ndim == 3 and bands.shape[2] == 2 else None)

    def export_as_json(self, file_location:str=None, subtract_fermi:bool=True) -> True:
        file_location = file_location if type(file_location) == str else self._file_location+'data.json'

        if subtract_fermi: self._subtract_fermi()

        SP = self._get_specialpoints(self.kpoints)

        # Crear el formato JSON
        json_data = {
            "path": {
                "kpts": self._ndarray_2_dict(self.kpoints[:,:3]),
                "special_points": {sp:self._ndarray_2_dict(self.special_lattice_points[sp]) for sp in SP},
                "labelseq": ''.join(SP),
                "cell": {"array": self._ndarray_2_dict(self.cell), "__ase_objtype__": "cell"},
                "__ase_objtype__": "bandpath"

                    },
            "energies": self._ndarray_2_dict( self._transform_bands() ), # SPIN x KPOINT x Nband
            "reference": self.fermi,
            "__ase_objtype__": "bandstructure"
        }

        self.save_to_json(json_data, file_location)
        
        return True

    def plot(self, file_location:str=None, subtract_fermi:bool=True, save:bool=False, Emin:float=-5, Emax:float=5) -> bool:
        import matplotlib.pyplot as plt

        file_location = file_location if type(file_location) == str else self._file_location+'img_band.png'

        if subtract_fermi: self._subtract_fermi()

        X_distance = [ np.min([k, 0.1]) for k in np.linalg.norm( self.kpoints[1:,:3] - self.kpoints[:-1,:3], axis=1 ) ] 
        X = [0]
        SP = []
        for k, point in enumerate(self.kpoints):

            for label, special_lattice_point in self.special_lattice_points.items():
                # Compare only the first three elements (x, y, z coordinates)
                if self.is_close(point[:3], special_lattice_point[:3]):
                    SP.append( [X[-1], label] )
                    break

            if k < self.kpoints.shape[0]-1: X.append( X[-1]+X_distance[k] )

        SP = np.array(SP)

        # Añadir líneas punteadas verticales
        for pos in SP[:, 0]:
            plt.axvline(x=float(pos), color='gray', linestyle='--', alpha=0.7 ,linewidth=1)
        plt.axhline(y=0, color='green', linestyle='-', alpha=0.2, linewidth=1)

        plt.ylim(-5, 5)

        Y = self.bands[:,:,:1] if self.bands.shape[2] == 1 else self.bands[:,:,:2] 
        plt.xticks(SP[:, 0].astype(np.float32), SP[:, 1])

        plt.plot(X, Y[:,:,0], color=[0.8,0.1,0.1], alpha=0.6, lw=0.7 )
        if self.bands.shape[2] == 4:
            plt.plot(X, Y[:,:,1], color=[0.1,0.1,0.8], alpha=0.6, lw=0.7 )
 

        # Save the plot to a file
        plt.savefig(f"{file_location}", dpi=350)  # Change the filename and format as needed


        # plt.show()



# Supongamos que tienes una matriz de 123x34. Aquí creamos una matriz de ejemplo.

'''
ei = EigenvalueFileManager('/home/akaris/Documents/code/Physics/VASP/v6.1/files/EIGENVAL/test/EIGENVAL', fermi=0)
ei.read_EIGENVAL()
ei.fermi = 0
ei.cell = [[1.0,0,0],[1,0,0],[1,0,0]]
ei.plot()
ei.export_as_json()

asdf
print(ei.bands.shape)

path = '/home/akaris/Documents/code/Physics/VASP/v6.1/files/EIGENVAL/bs_wz_ZnO.json'
with open(path, 'r') as file:
    data = json.load(file)
print( data['path'].keys() )

path = '/home/akaris/Documents/code/Physics/VASP/v6.1/files/EIGENVAL/EIGENVALdata.json'
with open(path, 'r') as file:
    data = json.load(file)
print( data['path'].keys() )

import matplotlib.pyplot as plt
plt.plot( ei.bands[:,:,1] )
plt.show()

#


        self.n_electrons = None
        self.n_kpoints = None
        self.n_bands = None
        self.bands = None
        self.kpoints = None
        self.k_distance = None
'''

