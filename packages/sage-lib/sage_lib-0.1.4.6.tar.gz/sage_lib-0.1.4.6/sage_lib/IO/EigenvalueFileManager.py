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
    import json
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing json: {str(e)}\n")
    del sys

class EigenvalueFileManager(FileManager, AtomicProperties):
    def __init__(self, file_location:str=None, name:str=None, cell:np.array=None, fermi:float=None, **kwargs):
        """
        Initialize OutFileManager class.
        :param file_location: Location of the file to be read.
        :param name: Name identifier for the file.
        :param kwargs: Additional keyword arguments.
        """
        FileManager.__init__(self, name=name, file_location=file_location)
        AtomicProperties.__init__(self)
        self._comment = None

        self._n_electron, self._num_kpoints, self._num_bands = None, None, None

        self._eigenvals = None
        self._occupancy = None
        self._kpoints = None
        self._weight = None
        self._k_distance = None

        self._fermi = fermi
        self._cell = cell

    @property
    def cell(self):
        if self._cell is not None:
            return np.array(self._cell, dtype=np.float64)
        else:
            return None

    def read_EIGENVALmatrix(self, lines:list=None):
        if lines is None or self.are_all_lines_empty(lines): return 0

        KPOINTn_eigenvals = np.zeros( (self.num_bands, 2 if self.ISPIN == 2 else 1), dtype=np.float64 )
        KPOINTn_occupancy = np.zeros( (self.num_bands, 2 if self.ISPIN == 2 else 1), dtype=np.float64 )

        for i, n in enumerate(lines):
            vec = [float(m) for m in n.split(' ') if self.is_number(m) ] 
            
            KPOINTn_eigenvals[i,:] = np.array([ vec[1], vec[2] ]) if self.ISPIN == 2 else np.array([ vec[1] ]) 
            KPOINTn_occupancy[i,:] = np.array([ vec[3], vec[4] ]) if self.ISPIN == 2 else np.array([ vec[2] ]) 

        return KPOINTn_eigenvals, KPOINTn_occupancy

    def read_EIGENVAL(self, file_location:str=None):
        file_location = file_location if type(file_location) == str else self._file_location
        lines = [n for n in self.read_file(file_location) ]
        
        var = 0
        for i, n in enumerate(lines):
            vec = [float(m) for m in n.split(' ') if self.is_number(m) ] 
            if   i == 0: self._NIONS, self._ISPIN = vec[0], vec[-1]
            elif i == 1: self._cellVolumen = vec[0]
            elif i == 2: self.T = vec[0]
            elif i == 5: 
                self._n_electron, self._num_kpoints, self._num_bands = int(vec[0]), int(vec[1]), int(vec[2])
                self._eigenvals = np.zeros( (self.num_kpoints, self.num_bands, 2 if self.ISPIN == 2 else 1), dtype=np.float64 )
                self._occupancy = np.zeros( (self.num_kpoints, self.num_bands, 2 if self.ISPIN == 2 else 1), dtype=np.float64 )
                self._kpoints = np.zeros( (self.num_kpoints, 3), dtype=np.float64 )
                self._weight = np.zeros( (self.num_kpoints, 1), dtype=np.float64 )

            if len(vec) == 4 and i>5: 
                self.kpoints[var, :] = vec[:3]
                self.weight[var]  = vec[3]
                self.eigenvals[var, :], self.occupancy[var, :] = self.read_EIGENVALmatrix(lines=lines[i+1:i+self.num_bands+1])
                var+=1

        self.k_distance = np.zeros((len(self.kpoints)), dtype=np.float64)
        var = 0
        for n in range(len(self.k_distance)-1): 
            var += ((self.kpoints[n][0]-self.kpoints[n+1][0])**2+(self.kpoints[n][1]-self.kpoints[n+1][1])**2+(self.kpoints[n][2]-self.kpoints[n+1][2])**2)**0.5
            self.k_distance[n+1] = var

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

        self.eigenvals -= fermi 
        self.fermi = 0
        
        return True

    def _transform_bands(self, eigenvals:np.array=None):
        eigenvals = self.eigenvals
        return matrix.reshape(1, *eigenvals.shape) if eigenvals.ndim == 2 else (eigenvals.transpose(2, 0, 1).reshape(2, *eigenvals.shape[:2]) if eigenvals.ndim == 3 and eigenvals.shape[2] == 2 else None)

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

    def plot(self, file_location:str=None, subtract_fermi:bool=True, save:bool=False, emin:float=-5, emax:float=5) -> bool:
        import matplotlib.pyplot as plt

        file_location = file_location if type(file_location) == str else self._file_location+'img_band.png'
        emin = emin if emin is not None else -5
        emax = emax if emax is not None else  5

        print(self.eigenvals[:, :,0])
        if subtract_fermi: self._subtract_fermi()
        print(self.eigenvals[:, :,0])

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

        plt.ylim(emin, emax)

        if self.ISPIN == 1:
            plt.xticks(SP[:, 0].astype(np.float32), SP[:, 1])
            plt.plot(X, self.eigenvals[:, :,0], color=[0.8,0.1,0.1], alpha=0.6, lw=0.7 )

        if self.ISPIN == 2:
            plt.xticks(SP[:, 0].astype(np.float32), SP[:, 1])
            plt.plot(X, self.eigenvals[:,:,0], color=[0.8,0.1,0.1], alpha=0.6, lw=0.7 )
            plt.plot(X, self.eigenvals[:,:,1], color=[0.1,0.1,0.8], alpha=0.6, lw=0.7 )
     
        # Save the plot to a file
        if save:
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

