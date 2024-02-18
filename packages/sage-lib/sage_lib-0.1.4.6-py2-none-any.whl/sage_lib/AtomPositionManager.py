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
    import re
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing re: {str(e)}\n")
    del sys

class AtomPositionManager(FileManager):
    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        super().__init__(name=name, file_location=file_location)
        self._comment = None
        self._atomCount = None  # N total number of atoms
        self._scaleFactor = None  # scale factor
        self._uniqueAtomLabels = None  # [Fe, N, C, H]
        self._atomCountByType = None  # [n(Fe), n(N), n(C), n(H)]
        self._selectiveDynamics = None  # bool 
        self._atomPositions = None  # np.array(N, 3)
        self._atomicConstraints = None # np.array(N, 3)

        self._atomLabelsList = None  # [Fe, N, N, N, N, C, C, C, C, H]
        self._fullAtomLabelString = None  # FeFeFeNNNNNNNCCCCCCCCCCCCCCCHHHHHHHHHHHHHHHH
        self._atomPositions_tolerance = 1e-2

        self._distance_matrix = None
        
        self._total_charge = None
        self._magnetization = None
        self._total_force = None
        self._E = None
        self._Edisp = None
        self._IRdisplacement = None

    @property
    def distance_matrix(self):
        if self._distance_matrix is not None:
            return self._distance_matrix
        elif self._atomPositions is not None:
            from scipy.spatial.distance import cdist 
            self._distance_matrix = cdist(self._atomPositions, self._atomPositions, 'euclidean')
            return self._distance_matrix
        elif'_atomPositions' not in self.__dict__:
            raise AttributeError("Attribute _atomPositions must be initialized before accessing atomLabelsList.")
        else:
            return None

    @property
    def scaleFactor(self):
        if type(self._scaleFactor) in [int, float, list, np.array]:
            self._scaleFactor = np.array(self._scaleFactor)
            return self._scaleFactor
        elif self._scaleFactor is None: 
            self._scaleFactor = np.array([1])
            return self._scaleFactor
        elif self._scaleFactor is not None:
            return self._scaleFactor
        else:
            return None

    @property
    def atomCount(self):
        if self._atomCount is not None:
            return np.array(self._atomCount)
        elif self._atomPositions is not None: 
            self._atomCount = self._atomPositions.shape[0] 
            return self._atomCount
        elif self._atomLabelsList is not None: 
            self._atomCount = self._atomLabelsList.shape
            return self._atomCount   
        elif'_atomPositions' not in self.__dict__:
            raise AttributeError("Attribute _atomPositions must be initialized before accessing atomLabelsList.")
        else:
            return None

    @property
    def uniqueAtomLabels(self):
        if self._uniqueAtomLabels is not None:
            return self._uniqueAtomLabels
        elif self._atomLabelsList is not None: 
            self._uniqueAtomLabels = list(dict.fromkeys(self._atomLabelsList).keys())
            return np.array(self._uniqueAtomLabels)
        elif'_atomLabelsList' not in self.__dict__:
            raise AttributeError("Attribute _atomLabelsList must be initialized before accessing atomLabelsList.")
        else:
            return None

    @property
    def atomCountByType(self):
        if self._atomCountByType is not None:
            return self._atomCountByType
        elif self._atomLabelsList is not None: 
            atomCountByType, atomLabelByType = {}, []
            for a in self._atomLabelsList:
                if not a in atomCountByType:
                    atomLabelByType.append(1)
                    atomCountByType[a] = len(atomLabelByType)-1
                else:
                    atomLabelByType[atomCountByType[a]] += 1
            self._atomCountByType = np.array(atomLabelByType)
            return self._atomCountByType
        elif'_atomLabelsList' not in self.__dict__:
            raise AttributeError("Attribute _atomLabelsList must be initialized before accessing atomLabelsList.")
        else:
            return None

    @property
    def atomLabelsList(self):
        if '_atomCountByType' not in self.__dict__ or '_uniqueAtomLabels' not in self.__dict__:
            raise AttributeError("Attributes _atomCountByType and _uniqueAtomLabels must be initialized before accessing atomLabelsList.")
        elif self._atomLabelsList is None and not self._atomCountByType is None and not self._uniqueAtomLabels is None: 
            return np.array([label for count, label in zip(self._atomCountByType, self._uniqueAtomLabels) for _ in range(count)])
        else:
            return  self._atomLabelsList 

    @property
    def fullAtomLabelString(self):
        if '_atomCountByType' not in self.__dict__ or '_uniqueAtomLabels' not in self.__dict__:
            raise AttributeError("Attributes _atomCountByType and _uniqueAtomLabels must be initialized before accessing fullAtomLabelString.")
        elif self._fullAtomLabelString is None and not self._atomCountByType is None and not self._uniqueAtomLabels is None: 
            self._fullAtomLabelString = ''.join([label*count for count, label in zip(self._atomCountByType, self._uniqueAtomLabels)])
            return self._fullAtomLabelString
        else:
            return  self._fullAtomLabelString 

    @property
    def atomPositions(self):
        if self._atomPositions is list:
            return np.array(self._atomPositions)
        elif self._atomPositions is None:
            return np.array([]).reshape(0, 3) 
        else:
            return self._atomPositions

    @property
    def atomicConstraints(self):
        if self._atomicConstraints is list:
            return np.array(self._atomicConstraints)
        elif self._atomPositions is not None:
            self._atomicConstraints = np.ones_like(self._atomPositions) 
            return self._atomicConstraints
        else:
            return self._atomicConstraints

    def convert_to_periodic(self):
        return PeriodicSystem(**self.attributes)
    
    def convert_to_non_periodic(self):
        return NonPeriodicSystem(**self.attributes)

    def distance(self, r1, r2): return np.linalg.norm(r1, r2)

    def move_atom(self, atom_index:int, displacement:np.array):
        self._atomPositions[atom_index,:] += displacement
        self._distance_matrix = None
        self._atomPositions_fractional = None

    def set_atomPositions(self, new_atomPositions:np.array):
        self._atomPositions = new_atomPositions
        self._distance_matrix = None
        self._atomPositions_fractional = None

    def remove_atom(self, atom_index: int):
        """Remove an atom at the given index."""
        self._atomicConstraints = np.delete(self.atomicConstraints, atom_index, axis=0)
        self._atomPositions = np.delete(self.atomPositions, atom_index, axis=0)
        self._atomPositions_fractional = np.delete(self._atomPositions_fractional, atom_index, axis=0)
        self._atomLabelsList = np.delete(self.atomLabelsList, atom_index)
        self._total_charge = np.delete(self.total_charge, atom_index) if self._total_charge is not None else self._total_charge
        self._magnetization = np.delete(self.magnetization, atom_index) if self._magnetization is not None else self._magnetization
        self._total_force = np.delete(self.total_force, atom_index) if self._total_force is not None else self._total_force
        self._atomCount -= 1
        self._atomCountByType = None
        self._fullAtomLabelString = None
        self._uniqueAtomLabels = None

        if self._distance_matrix is not None:
            self._distance_matrix = np.delete(self._distance_matrix, var, axis=0)  # Eliminar fila
            self._distance_matrix = np.delete(self._distance_matrix, var, axis=1)  # Eliminar columna

    def add_atom(self, atomLabels: str, atomPosition: np.array, atomicConstraints: np.array = np.array([1, 1, 1])) -> bool:
        """
        Adds an atom to the AtomContainer.

        :param atomLabels: Label for the new atom.
        :param atomPosition: Position of the new atom as a numpy array.
        :param atomicConstraints: Atomic constraints as a numpy array (defaults to [1,1,1]).
        """
        # Add to atomPositions
        self._atomPositions = np.atleast_2d(atomPosition) if self.atomPositions is None else np.vstack([self.atomPositions, atomPosition])

        # Add to atomLabelsList
        self._atomLabelsList = np.array([atomLabels]) if self.atomLabelsList is None else np.append(self.atomLabelsList, atomLabels)

        # Add to atomicConstraints
        self._atomicConstraints = np.vstack([self.atomicConstraints, atomicConstraints]) if self.atomicConstraints is not None else np.atleast_2d(atomicConstraints)

        # Increment atomCount
        self._atomCount = 1 if self._atomCount is None else self._atomCount + 1

        # Reset dependent attributes
        self._reset_dependent_attributes()

        # Group elements and positions
        self.group_elements_and_positions()
        return True

    def _reset_dependent_attributes(self):
        """
        Resets dependent attributes to None.
        """
        attributes_to_reset = ['_total_charge', '_magnetization', '_total_force', '_atomPositions_fractional', 
                               '_atomCountByType', '_fullAtomLabelString', '_uniqueAtomLabels', '_distance_matrix']
        for attr in attributes_to_reset:
            setattr(self, attr, None)

    def find_n_closest_neighbors(self, position, n):
        """Find the n closest neighbors to a given atom."""
        #distance_matrix = self.distanceamtrix
        #distances = distance_matrix[atom_index]
        
        # Sort the distances and get the indices of the n closest neighbors.
        # We exclude the first index because it's the atom itself (distance=0).
        distances = [self.distance( position, a) for a in self.atomPositions ]
        closest_indices = np.argsort( distances )[:n]
        
        # Get the labels and positions of the closest neighbors.
        closest_labels = [self._atomLabelsList[i] for i in closest_indices]
        closest_distance = [ distances[i] for i in closest_indices]
        
        return closest_indices, closest_labels, closest_distance

    def compare_chemical_environments(self, distances1, labels1, distances2, labels2, label_weights=None, distance_decay=1.0):
        """
        Compare two chemical environments and return a similarity score.

        Parameters:
        - distances1, distances2: List of distances to the atoms in the environments.
        - labels1, labels2: List of labels indicating the type of each atom in the environments.
        - label_weights: Dictionary assigning weights to each type of atom label. If None, all weights are set to 1.
        - distance_decay: A decay factor for the influence of distance in the similarity score.

        Returns:
        - float: A similarity score. Lower values indicate more similar environments.
        """
        if label_weights is None:
            label_weights = {label: 1.0 for label in set(labels1 + labels2)}
        
        # Initialize similarity score
        similarity_score = 0.0

        for d1, l1 in zip(distances1, labels1):
            min_diff = float('inf')
            for d2, l2 in zip(distances2, labels2):
                if l1 == l2:
                    diff = np.abs(d1 - d2)
                    min_diff = min(min_diff, diff)
            
            if min_diff != float('inf'):
                weight = label_weights.get(l1, 1.0)
                similarity_score += weight * np.exp(-distance_decay * min_diff)

        return similarity_score

    def get_plane(self, atom1, atom2, atom3):
        v1 = self.atomPositions[atom1, :] - self.atomPositions[atom2, :]
        v2 = self.atomPositions[atom2, :] - self.atomPositions[atom3, :]
        # | i        j     k   | #
        # | v1x    v1y    v1z  | #
        # | v2x    v2y    v2z  | #
        return np.array([   v1[1]*v2[2]-v1[2]*v2[1],
                            v1[2]*v2[0]-v1[0]*v2[2],
                            v1[0]*v2[1]-v1[1]*v2[0], ])

    def get_dihedric(self, atom1, atom2, atom3, atom4):
        p1 = self.get_plane(atom1, atom2, atom3)
        p2 = self.get_plane(atom2, atom3, atom4)
        '''
     ****         xxx
        ****    xxx
          ****xxxfilename
            xxx***
          xxx   *****
        xxx (P2)   ***** (P1)
        '''
        return self.get_vector_angle(p1, p2)

    def get_angle(self, atom1, atom2, atom3):
        v1 = self.atomPositions[atom1, :] - self.atomPositions[atom2, :]
        v2 = self.atomPositions[atom2, :] - self.atomPositions[atom3, :]

        return self.get_vector_angle(v1, v2)

    def get_vector_angle(self, v1, v2):
        '''
        1.     The get_vector_angle function takes two vectors as input. These vectors represent the direction and magnitude of an angle between the vectors.
        2.     The function calculates the angle between the vectors using the arccosine function.
        3.     The angle returned is a unit vector in the direction of the angle.
        '''
        unit_vector_1 = v1 / np.linalg.norm(v1)
        unit_vector_2 = v2 / np.linalg.norm(v2)
        dot_product = np.dot(unit_vector_1, unit_vector_2)
        angle = np.arccos(dot_product)

        return angle

    def rotation_matrix(self, axis, phi):
        """Create a rotation matrix given an axis and an angle phi."""
        axis = normalize(axis)
        a = np.cos(phi / 2)
        b, c, d = -axis * np.sin(phi / 2)
        aa, bb, cc, dd = a * a, b * b, c * c, d * d
        bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
        return np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                         [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                         [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])

    def rotate_atoms(self, atoms, axis, phi):
        """
        Rotate a set of atoms around an axis by an angle phi.

        :param atoms: A Nx3 matrix of atomic coordinates.
        :param axis: A 3D vector representing the rotation axis.
        :param phi: The rotation angle in radians.
        :return: The rotated Nx3 matrix of atomic coordinates.
        """
        # Create the rotation matrix
        R = self.rotation_matrix(axis, phi)
        # Apply the rotation matrix to each row (atom) in the atoms matrix
        return np.dot(atoms, R.T)

    def group_elements_and_positions(self, atomLabelsList:list=None, atomPositions:list=None):
        # Verificar que la longitud de element_labels coincide con el número de filas en position_matrix
        atomLabelsList = atomLabelsList if atomLabelsList is not None else self.atomLabelsList
        atomPositions = atomPositions if atomPositions is not None else self.atomPositions

        # Crear un diccionario para almacenar los índices de cada tipo de elemento
        element_indices = {}
        for i, label in enumerate(atomLabelsList):
            if label not in element_indices:
                element_indices[label] = []
            element_indices[label].append(i)

        # Crear una nueva lista de etiquetas y una nueva matriz de posiciones
        atomLabelsList_new = []
        atomPositions_new = []
        uniqueAtomLabels_new = element_indices.keys()
        for label in element_indices:
            atomLabelsList_new.extend([label] * len(element_indices[label]))
            atomPositions_new.extend(atomPositions[element_indices[label]])

        self._atomLabelsList = atomLabelsList_new
        self._atomPositions = np.array(atomPositions_new)
        self._uniqueAtomLabels = None  # [Fe, N, C, H]
        self._atomCountByType = None  # [n(Fe), n(N), n(C), n(H)]
        self._fullAtomLabelString = None  # FeFeFeNNNNNNNCCCCCCCCCCCCCCCHHHHHHHHHHHHHHHH

        return True

    def atomLabelFilter(self, ID, v=False):  
        return np.array([ True if n in ID else False for n in self.atomLabelsList])

    def rattle(self, stdev:float=0.001, seed:float=None, rng:float=None):
        """Randomly displace atoms.

        This method adds random displacements to the atomic positions,
        taking a possible constraint into account.  The random numbers are
        drawn from a normal distribution of standard deviation stdev.

        For a parallel calculation, it is important to use the same
        seed on all processors!  """

        if seed is not None and rng is not None:
            raise ValueError('Please do not provide both seed and rng.')

        if rng is None:
            if seed is None:
                seed = 42
            rng = np.random.RandomState(seed)

        self.set_atomPositions(self.atomPositions +
                           rng.normal(scale=stdev, size=self.atomPositions.shape))

        '''
    def calculate_rms_displacement_in_angstrom(atomic_mass_amu, temperature, frequency_au=1.0):
        """
        Calculate the root-mean-square displacement of an atom in a harmonic potential in Ångströms.

        Parameters:
        atomic_mass_amu (float): Atomic mass of the element in atomic mass units (amu).
        temperature (float): Temperature in Kelvin.
        frequency_au (float): Vibrational frequency in atomic units (default is 1.0).

        Returns:
        float: RMS displacement in Ångströms.
        """
        # Constants in atomic units
        k_B_au = 3.1668114e-6  # Boltzmann constant in hartree/Kelvin
        amu_to_au = 1822.888486209  # Conversion from amu to atomic units of mass
        bohr_to_angstrom = 0.529177  # Conversion from Bohr radius to Ångströms

        # Convert mass from amu to atomic units
        mass_au = atomic_mass_amu * amu_to_au

        # Force constant in atomic units
        k_au = mass_au * frequency_au**2

        # RMS displacement in atomic units
        sigma_au = np.sqrt(k_B_au * temperature / k_au)

        # Convert RMS displacement to Ångströms
        sigma_angstrom = sigma_au * bohr_to_angstrom
        
        return sigma_angstrom
        '''

    def exportAsPDB(self, file_location:str=None, bond_distance:float=2.3, v:bool=False) -> bool:
        if v: print(f' Export as PDB >> {file_location}')
        
        file_location  = file_location  if not file_location  is None else self.file_location+'.pdb'

        filePDB = open(f'{file_location}', 'w')
        for i, pos in enumerate(self.atomPositions):     #loop over different atoms
            S = "ATOM  %5d %2s   MOL     1  %8.3f%8.3f%8.3f  1.00  0.00\n" % (int(i+1), self.atomLabelsList[i], pos[0], pos[1], pos[2])
            filePDB.write(S) #ATOM

        for i1, pos1 in enumerate(self.atomPositions):       #loop over different atoms
            for i2, pos2 in enumerate(self.atomPositions):
                if  i1>i2 and np.linalg.norm(pos1-pos2) < bond_distance:
                    filePDB.write(f'CONECT{int(i1+1):>5}{int(i2+1):>5}\n')

        filePDB.close()
        return True

    def exportAsPOSCAR(self, file_location:str=None, v:bool=False) -> bool:
        file_location  = file_location  if not file_location  is None else self.file_location+'POSCAR' if self.file_location is str else self.file_location
        self.group_elements_and_positions()

        with open(file_location, 'w') as file:
            # Comentario inicial
            file.write(f'POSCAR : JML code \n')

            # Factor de escala
            file.write(f"{' '.join(map(str, self.scaleFactor))}\n")

            # Vectores de la celda unitaria
            for lv in self.latticeVectors:
                file.write('{:>18.15f}\t{:>18.15f}\t{:>18.15f}\n'.format(*lv))

            # Tipos de átomos y sus números
            file.write('    '.join(self.uniqueAtomLabels) + '\n')
            file.write('    '.join(map(str, self.atomCountByType)) + '\n')

            # Opción para dinámica selectiva (opcional)
            if self._selectiveDynamics:     file.write('Selective dynamics\n')
            # Tipo de coordenadas (Direct o Cartesian)
            aCT = 'Cartesian' if self.atomCoordinateType[0].capitalize() in ['C', 'K'] else 'Direct'
            file.write(f'{aCT}\n')

            # Coordenadas atómicas y sus restricciones
            for i, atom in enumerate(self.atomPositions if self.atomCoordinateType[0].capitalize() in ['C', 'K'] else self.atomPositions_fractional):
                coords = '\t'.join(['{:>18.15f}'.format(n) for n in atom])
                constr = '\tT\tT\tT' if self.atomicConstraints is None else '\t'.join(['T' if n else 'F' for n in self.atomicConstraints[i]]) 
                file.write(f'\t{coords}\t{constr}\n')

            # Comentario final (opcional)
            file.write('Comment_line\n')

    def export_as_xyz(self, file_location:str=None, save_to_file:str='w', verbose:bool=False) -> str:
        """
        Export atomistic information in the XYZ format.

        Parameters:
            file_location (str): The location where the XYZ file will be saved. Ignored if save_to_file is False.
            save_to_file (bool): Flag to control whether to save the XYZ content to a file.
            verbose (bool): Flag to print additional information, if True.

        Returns:
            str: The generated XYZ content.
        """
        file_location  = file_location  if not file_location  is None else self.file_location+'config.xyz' if self.file_location is str else self.file_location
        self.group_elements_and_positions()

        # Initialize an empty string to store the XYZ content
        xyz_content = ""

        # Write the number of atoms
        xyz_content += f"{self.atomCount}\n"

        # Write information about the unit cell, energy, etc.
        lattice_str = " ".join(map(str, self._latticeVectors.flatten()))
        #pbc_str = ' '.join(['T' if val else 'F' for val in self.pbc])
        xyz_content += f'Lattice="{lattice_str}" Properties=species:S:1:pos:R:3:DFT_forces:R:3 DFT_energy={self._E}  pbc="T T T"\n'

        # Column widths for alignment. These can be adjusted.
        col_widths = {'element': 5, 'position': 12, 'force': 12}
        # Write the atom positions, masses, and forces
        for i in range(self.atomCount):
            atom_label = self.atomLabelsList[i]
            pos = " ".join(map("{:12.6f}".format, self.atomPositions[i])) if self.atomPositions is not None else ''
            force = " ".join(map("{:14.6f}".format, self.total_force[i])) if self.total_force is not None else ''  # Assuming that self._total_force is an array (N, 3)
            xyz_content += f"{atom_label:<{col_widths['element']}}{pos}{force}\n"

        # Save the generated XYZ content to a file if file_location is specified and save_to_file is True
        if file_location and save_to_file:
            with open(file_location, save_to_file) as f:
                f.write(xyz_content)
            if verbose:
                print(f"XYZ content has been saved to {file_location}")

        return xyz_content

    def export_as_PDB(self, file_location:str=None, bond_distance:float=None, save_to_file:str='w', bond_factor=1.1, verbose:bool=False) -> str:
        file_location  = file_location  if not file_location  is None else self.file_location+'config.pdb' if type(self.file_location) is str else self.file_location
            
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

    def read_configXYZ(self, file_location: str = None, lines: list = None, energy_key: str = 'energy', 
                       masses_key: str = 'masses', forces_key: str = 'forces', position_key: str = 'pos',  
                       species_key: str = 'species', PBC_key: str = 'pbc', verbose: bool = False):
        """
        Reads and parses data from a XYZ configuration file used in molecular simulations.

        :param file_location: Location of the XYZ file. If None, uses default file location.
        :param lines: List of lines from the file to be read. If None, reads from the file directly.
        :param energy_key: Key string for energy data in the file.
        :param masses_key: Key string for atomic masses data in the file.
        :param forces_key: Key string for forces data in the file.
        :param position_key: Key string for atomic positions data in the file.
        :param species_key: Key string for atomic species data in the file.
        :param PBC_key: Key string for periodic boundary conditions data in the file.
        :param verbose: If True, prints additional information during processing.
        :return: True if the file is successfully read and parsed, False otherwise.
        """        
        file_location = file_location if isinstance(file_location, str) else self.file_location

        pattern = r'(\w+)=("[^"]+"|\S+)'
        data = {'species', 'pos', 'masses', 'forces', 'E'}
        read_header = False


        lines = lines if lines is not None else list(self.read_file(file_location,strip=False))

        for i, line in enumerate(lines):
            if read_header:
                matches = re.findall(pattern, line)
                body = np.array( [ n.strip().split() for n in lines[i+1:i+self._atomCount+1] ])
                for key, value in matches:
                    if key == 'Lattice':
                        self._latticeVectors = np.array([ [ float(value[1:-1].strip().split()[i*3+j]) for j in range(3) ] for i in range(3) ])
                        self._atomCoordinateType = 'C'
                        
                    if key == 'Properties':
                        matches_Properties_count = 0
                        matches_Properties_vec = value.split(':')
                        for pi, p in enumerate(matches_Properties_vec):
                            if forces_key in p:
                                self._total_force = np.array(body[:, matches_Properties_count:matches_Properties_count+3], dtype=np.float64)

                            elif masses_key in p:
                                self._mass = body[:, matches_Properties_count]

                            elif position_key in p:
                                self._atomPositions = np.array(body[:, matches_Properties_count:matches_Properties_count+3], dtype=np.float64)

                            elif species_key in p:
                                self._atomLabelsList = body[:, matches_Properties_count]

                            if pi%3==0:
                                matches_Properties_count += int(matches_Properties_vec[pi+2])

                    if key == energy_key:
                        self._E = float(value)

                    if key == PBC_key:
                        self._pbc = list( ['T' in v  for v in value.split()] )

                return True

            elif line.strip().isdigit():
                num_atoms = int(line.strip())
                if num_atoms > 0:
                    self._atomCount = num_atoms
                    read_header = True 