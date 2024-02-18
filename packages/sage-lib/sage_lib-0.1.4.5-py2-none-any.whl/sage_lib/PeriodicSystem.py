# En __init__.py del paquete que contiene AtomPositionManager
try:
    from sage_lib.AtomPositionManager import AtomPositionManager
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing AtomPositionManager: {str(e)}\n")
    del sys

try:
    import numpy as np
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys

class PeriodicSystem(AtomPositionManager):
    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        super().__init__(name=name, file_location=file_location)
        self._reciprocalLatticeVectors = None # [b1, b2, b3]
        self._latticeVectors = None # [a1,a2,a3]
        self._latticeVectors_inv = None # [a1,a2,a3]

        self._symmetryEquivPositions = None
        self._atomCoordinateType = None  # str cartedian direct
        self._latticeParameters = None # [] latticeParameters
        self._latticeAngles = None  # [alpha, beta, gamma]
        self._cellVolumen = None  # float

        self._atomPositions_fractional = None

        self._latticeType = None
        self._latticeType_tolerance = 1e-4

        self._distance_matrix = None

        self._pbc = None
        self._is_surface = None
        self._is_bulk = None 
        
        self._surface_atoms_indices = None
        
    @property
    def surface_atoms_indices(self):
        if self._surface_atoms_indices is not None:
            return self._surface_atoms_indices
        elif self.atomPositions is not None:
            self._surface_atoms_indices = self.find_surface_atoms()
            return self._surface_atoms_indices
        elif'_atomPositions' not in self.__dict__:
            raise AttributeError("Attribute _atomPositions must be initialized before accessing atomLabelsList.")
        else:
            return None

    @property
    def distance_matrix(self):
        if self._distance_matrix is not None:
            return self._distance_matrix
        elif self._atomPositions is not None:
            distance_matrix = np.zeros((self.atomCount, self.atomCount))
            for i in range(self.atomCount):
                for j in range(i, self.atomCount):
                    distance_matrix[i, j] = self.minimum_image_distance( self.atomPositions[i], self.atomPositions[j] )
            self._distance_matrix = distance_matrix
            return self._distance_matrix
        elif'_atomPositions' not in self.__dict__:
            raise AttributeError("Attribute _atomPositions must be initialized before accessing atomLabelsList.")
        else:
            return None

    @property
    def latticeType(self):
        if not self._latticeType is None:
            return np.array(self._latticeType)
        elif self.latticeVectors is not None and self.latticeAngles is not None:
            a,b,c = [np.linalg.norm(vec) for vec in self.latticeVectors]
            alpha, beta, gamma = self.latticeAngles 

            # Check if angles are 90 degrees within tolerance
            is_90 = lambda angle: abs(angle - np.pi/2) < self._latticeType_tolerance

            # Check if angles are 120 or 60 degrees within tolerance
            is_120 = lambda angle: abs(angle - np.pi*2/3) < self._latticeType_tolerance
            is_60 = lambda angle: abs(angle - np.pi/3) < self._latticeType_tolerance

            # Check if lattice constants are equal within tolerance
            equal_consts = lambda x, y: abs(x - y) < self._latticeType_tolerance
            
            if all(map(is_90, [alpha, beta, gamma])):
                if equal_consts(a, b) and equal_consts(b, c):
                    return "SimpleCubic"
                elif equal_consts(a, b) or equal_consts(b, c) or equal_consts(a, c):
                    return "Tetragonal"
                else:
                    return "Orthorhombic"

            elif is_90(alpha) and is_90(beta) and is_120(gamma):
                if equal_consts(a, b) and not equal_consts(b, c):
                    return "Hexagonal"

            elif is_90(alpha) and is_90(beta) and is_90(gamma):
                if equal_consts(a, b) and not equal_consts(b, c):
                    return "Hexagonal"  # This is actually a special case sometimes considered under Tetragonal

            elif is_90(alpha):
                return "Monoclinic"

            else:
                return "Triclinic"

            return self._latticeType
        elif 'latticeVectors' not in self.__dict__:
            raise AttributeError("Attributes latticeVectors and latticeAngles must be initialized before accessing latticeParameters.")

    @property
    def atomPositions_fractional(self):
        if not self._atomPositions_fractional is None:
            return self._atomPositions_fractional
        elif self._atomPositions is not None:
            self._atomPositions_fractional = np.dot(self._atomPositions, self.latticeVectors_inv)
            return self._atomPositions_fractional
        elif '_atomPositions' not in self.__dict__:
            raise AttributeError("Attributes _atomPositions must be initialized before accessing latticeParameters.")

    @property
    def atomPositions(self):
        if not self._atomPositions is None:
            return np.array(self._atomPositions)
        elif self._atomPositions_fractional is not None:
            self._atomPositions = np.dot(self._atomPositions_fractional, self.latticeVectors)
            return self._atomPositions
        elif '_atomPositions_fractional' not in self.__dict__:
            raise AttributeError("Attributes _atomPositions_fractional must be initialized before accessing latticeParameters.")

    @property
    def reciprocalLatticeVectors(self):
        if not self._reciprocalLatticeVectors is None:
            return self._reciprocalLatticeVectors
        elif self._latticeVectors is not None:
            a1,a2,a3 = self._latticeVectors
            self._reciprocalLatticeVectors = np.array([
                    2 * np.pi * np.cross(a2, a3) / np.dot(a1, np.cross(a2, a3)),
                    2 * np.pi * np.cross(a3, a1) / np.dot(a2, np.cross(a3, a1)),
                    2 * np.pi * np.cross(a1, a2) / np.dot(a3, np.cross(a1, a2)) 
                                                    ])
            return self._reciprocalLatticeVectors


        elif '_latticeVectors' not in self.__dict__:
            raise AttributeError("Attributes _latticeParameters and _latticeAngles must be initialized before accessing latticeParameters.")

    @property
    def latticeAngles(self):
        if not self._latticeAngles is None:
            return self._latticeAngles
        elif self._latticeVectors is not None:
            a1,a2,a3 = self._latticeVectors 
            # Calculate magnitudes of the lattice vectors
            norm_a1 = np.linalg.norm(a1)
            norm_a2 = np.linalg.norm(a2)
            norm_a3 = np.linalg.norm(a3)
            # Calculate the angles in radians
            self._latticeAngles = np.array([
                    np.arccos(np.dot(a2, a3) / (norm_a2 * norm_a3)),
                    np.arccos(np.dot(a1, a3) / (norm_a1 * norm_a3)),
                    np.arccos(np.dot(a1, a2) / (norm_a1 * norm_a2))
                    ])
            return self._latticeAngles
        elif '_latticeVectors' not in self.__dict__:
            raise AttributeError("Attributes _latticeVectors and _latticeAngles must be initialized before accessing latticeParameters.")


    @property
    def latticeVectors(self):
        if not self._latticeVectors is None:
            return self._latticeVectors
        elif self._latticeAngles is not None and self._latticeParameters is not None:
            m1, m2, m3 = self._latticeParameters
            alpha, beta, gamma = self._latticeAngles  # Convert to radians
            
            self._latticeVectors = np.array([
                    [m1, 0, 0],
                    [m2 * np.cos(gamma), m2 * np.sin(gamma), 0],
                    [m3 * np.cos(beta),
                     m3 * (np.cos(alpha) - np.cos(beta) * np.cos(gamma)) / np.sin(gamma),
                     m3 * np.sqrt(1 - np.cos(beta)**2 - ((np.cos(alpha) - np.cos(beta) * np.cos(gamma)) / np.sin(gamma))**2)
                                            ] ])
            return self._latticeVectors
        elif '_latticeParameters' not in self.__dict__ or '_latticeAngles' not in self.__dict__:
            raise AttributeError("Attributes _latticeParameters and _latticeAngles must be initialized before accessing latticeParameters.")
 
    @property
    def latticeVectors_inv(self):
        if not self._latticeVectors_inv is None:
            return self._latticeVectors_inv
        elif self.latticeVectors is not None:
            self._latticeVectors_inv = np.linalg.inv(self.latticeVectors)
            return self._latticeVectors_inv
        elif 'latticeVectors' not in self.__dict__:
            raise AttributeError("Attributes latticeVectors must be initialized before accessing latticeParameters.")

    @property
    def latticeParameters(self):
        if '_latticeParameters' not in self.__dict__ or '_latticeParameters' not in self.__dict__:
            raise AttributeError("Attributes _latticeParameters and _latticeParameters must be initialized before accessing latticeParameters.")
        elif self._latticeParameters is not None:
            return self._latticeParameters  
        elif self._latticeVectors is not None:
            self._latticeParameters = np.linalg.norm(self.latticeVectors, axis=1)
            return self._latticeParameters
        else:
            return None

    @property
    def cellVolumen(self):
        if '_cellVolumen' not in self.__dict__ or '_cellVolumen' not in self.__dict__:
            raise AttributeError("Attributes _cellVolumen and _cellVolumen must be initialized before accessing cellVolumen.")
        elif not self._cellVolumen is None: 
            return  self._cellVolumen 
        elif self._latticeParameters is not None or self._latticeAngles is not None:
            a, b, c = self._latticeParameters
            alpha, beta, gamma = self._latticeAngles  # Convert to radians

            # Calculate volume using the general formula for triclinic cells
            self._cellVolumen = a * b * c * np.sqrt(
                1 - np.cos(alpha)**2 - np.cos(beta)**2 - np.cos(gamma)**2 +
                2 * np.cos(alpha) * np.cos(beta) * np.cos(gamma)
            )
            return self._cellVolumen
        else:
            return None

    @property
    def pbc(self):
        if self._pbc is not None:
            return self._pbc
        else:
            vacum_criteria = 4 # A 
            self.pack_to_unit_cell()

            pbc = [True, True, True]
            for axis in range(3):
                L = self.latticeParameters[axis]
                for a1 in range(int(L) - vacum_criteria + 1):
                    if not np.any((self.atomPositions[:, axis] >= a1) & (self.atomPositions[:, axis] < a1+vacum_criteria)):
                        pbc[axis] = False
                        break  # No need to continue if one region is already missing an atom
            self._pbc = pbc
            return self._pbc

    @property
    def is_surface(self):
        if self._is_surface is not None:
            return self._is_surface
        else:
            return np.sum(self.pbc)==2 

    @property
    def is_bulk(self):
        if self._is_bulk is not None:
            return self._is_bulk
        else:
            return np.sum(self._pbc)==3

    def move_atom(self, atom_index:int, displacement:np.array):
        new_position = self.atomPositions[atom_index,:] + displacement
        self._atomPositions[atom_index,:] = new_position
        self._atomPositions_fractional = None

    def to_fractional_coordinates(self, cart_coords):
        inv_lattice_matrix = np.linalg.inv(self.latticeVectors)
        return np.dot(inv_lattice_matrix, cart_coords.T).T
    
    def to_cartesian_coordinates(self, frac_coords):
        return np.dot(self.latticeVectors.T, frac_coords.T).T
    
    def distance(self, r1, r2): return self.minimum_image_distance(r1, r2)

    def pack_to_unit_cell(self, ):
        # Apply minimum image convention
        self._atomPositions_fractional = self.atomPositions_fractional%1.0
        
        # Convert back to Cartesian coordinates
        self._atomPositions = np.dot(self.atomPositions_fractional, self.latticeVectors)

    def minimum_image_distance(self, r1, r2, n_max=1):
        """
        Calcula la distancia mínima entre dos puntos en un sistema periódico usando NumPy.
        
        Parámetros:
        r1, r2 : arrays de NumPy
            Las coordenadas cartesianas de los dos puntos.
        lattice_vectors : matriz de 3x3
            Los vectores de la red cristalina.
        n_max : int
            El número máximo de imágenes a considerar en cada dimensión.
            
        Retorna:
        d_min : float
            La distancia mínima entre los dos puntos.
        """
        
        # Generar todas las combinaciones de índices de celda
        n_values = np.arange(-n_max, n_max + 1)
        n_combinations = np.array(np.meshgrid(n_values, n_values, n_values)).T.reshape(-1, 3)
        
        # Calcular todas las imágenes del segundo punto
        r2_images = r2 + np.dot(n_combinations, self.latticeVectors)
        
        # Calcular las distancias entre r1 y todas las imágenes de r2
        distances = np.linalg.norm(r1 - r2_images, axis=1)
        
        # Encontrar y devolver la distancia mínima
        d_min = np.min(distances)
        return d_min

    def minimum_image_interpolation(self, r1, r2, n:int=2, n_max=1):
        """
        Calcula la distancia mínima entre dos puntos en un sistema periódico usando NumPy.
        
        Parámetros:
        r1, r2 : arrays de NumPy
            Las coordenadas cartesianas de los dos puntos.
        lattice_vectors : matriz de 3x3
            Los vectores de la red cristalina.
        n_max : int
            El número máximo de imágenes a considerar en cada dimensión.
            
        Retorna:
        d_min : float
            La distancia mínima entre los dos puntos.
        """
        
        # Generar todas las combinaciones de índices de celda
        n_values = np.arange(-n_max, n_max + 1)
        n_combinations = np.array(np.meshgrid(n_values, n_values, n_values)).T.reshape(-1, 3)
        
        # Calcular todas las imágenes del segundo punto
        r2_images = r2 + np.dot(n_combinations, self.latticeVectors)
        
        # Calcular las distancias entre r1 y todas las imágenes de r2
        distances = np.linalg.norm(r1 - r2_images, axis=1)
        
        # Encontrar y devolver la distancia mínima
        darg_min = np.argmin(distances)

        # Generate a sequence of n evenly spaced scalars between 0 and 1
        t_values = np.linspace(0, 1, n)  # Exclude the endpoints
        
        # Calculate the intermediate points
        points = np.outer(t_values, r2_images[darg_min] - r1) + r1

        return points


    def generate_supercell(self, repeat:np.array=np.array([2,2,2], dtype=np.int64) ):
        """
        Generate a supercell from a given unit cell in a crystalline structure.

        Parameters:
        - repeat (list): A list of three integers (nx, ny, nz) representing the number of times the unit cell is replicated 
                            along the x, y, and z directions, respectively.

        Returns:
        - np.array: An array of atom positions in the supercell.
        """

        # Extract lattice vectors from parameters
        a, b, c = self.latticeVectors
        nx, ny, nz = repeat

        # Generate displacement vectors
        displacement_vectors = [a * i + b * j + c * k for i in range(nx) for j in range(ny) for k in range(nz)]

        # Replicate atom positions and apply displacements
        atom_positions = np.array(self.atomPositions)
        supercell_positions = np.vstack([atom_positions + dv for dv in displacement_vectors])

        # Replicate atom identities and movement constraints
        supercell_atomLabelsList = np.tile(self.atomLabelsList, nx * ny * nz)
        supercell_atomicConstraints = np.tile(self.atomicConstraints, (nx * ny * nz, 1))

        self._atomLabelsList = supercell_atomLabelsList
        self._atomicConstraints = supercell_atomicConstraints
        self._atomPositions = supercell_positions
        self._latticeVectors = self._latticeVectors*np.array(repeat)
        self._atomPositions_fractional = None
        self._atomCount = None
        self._atomCountByType = None
        self._fullAtomLabelString = None

        return True

    def is_point_inside_unit_cell(self, point):
        """
        Check if a given point is inside the unit cell.

        Args:
            point (list or np.array): A 3D point to be checked.

        Returns:
            bool: True if the point is inside the unit cell, False otherwise.
        """
        # Convert point to numpy array for calculation
        point = np.array(point)

        # Inverting the lattice vectors matrix for transformation
        inv_lattice = np.linalg.inv(self._latticeVectors)

        # Converting the point to fractional coordinates
        fractional_coords = inv_lattice.dot(point)

        # Check if all fractional coordinates are between 0 and 1
        return np.all(fractional_coords >= 0) and np.all(fractional_coords <= 1)

    # ======== SURFACE CODE ======== # 
    def find_opposite_atom(self, atom_position, label, tolerance_z=2.2, tolerance_distance=-10):
        """Find the symmetrically opposite atom's index."""
        # Convert to fractional coordinates and find center
        lattice_matrix = np.array(self._latticeVectors)
        atom_frac = self.to_fractional_coordinates(atom_position)
        inv_lattice_matrix = np.linalg.inv(lattice_matrix)
        center_frac = np.mean(np.dot(inv_lattice_matrix, self.atomPositions.T).T, axis=0)

        # Find opposite atom in fractional coordinates
        opposite_atom_position_frac = 2 * center_frac - atom_frac
        opposite_atom_position = np.dot(lattice_matrix, opposite_atom_position_frac)

        removed_atom_closest_indices, removed_atom_closest_labels, removed_atom_closest_distance = self.find_n_closest_neighbors(atom_position, 4)

        # Calculate distances to find opposite atom
        distances = -np.ones(self.atomCount)*np.inf
        for i, a in enumerate(self.atomPositions):
            if (self.atomLabelsList[i] == label and
                np.abs(atom_position[2] - a[2]) >= tolerance_z and
                np.abs(opposite_atom_position[2] - a[2]) <= tolerance_z):

                closest_indices, closest_labels, closest_distance = self.find_n_closest_neighbors(a, 4)
                distances[i] = self.compare_chemical_environments(removed_atom_closest_distance, removed_atom_closest_labels,
                                                            closest_distance, closest_labels)#self.minimum_image_distance(opposite_atom_position, a)
                distances[i] -= np.abs(opposite_atom_position[2] - a[2]) * 4

        opposite_atom_index = np.argmax(distances)
        opposite_atom_distance = np.max(distances)

        return opposite_atom_index if opposite_atom_distance >= tolerance_distance else None
    
    def find_surface_atoms(self, threshold=2.0):
        """
        Identify indices of surface atoms in a slab of atoms.

        Atoms are considered to be on the surface if there are no other atoms 
        within a certain threshold distance above them. This function assumes 
        that the z-coordinate represents the height.

        Parameters:
        - threshold: The distance within which another atom would disqualify 
                     an atom from being considered as part of the surface.

        Returns:
        - A list of indices corresponding to surface atoms.
        """

        # Sort atom indices by their z-coordinate in descending order (highest first)
        indices_sorted_by_height = np.argsort(-self.atomPositions[:, 2])

        # A helper function to determine if any atom is within the threshold distance
        def is_atom_on_surface(idx, compared_indices):
            position = np.array([self.atomPositions[idx, 0], self.atomPositions[idx, 1], 0]) # Only x, y coordinates

            for idx_2 in compared_indices:
                if self.distance(position ,np.array([self.atomPositions[idx_2,0], self.atomPositions[idx_2,1], 0])) < threshold:
                    return False
            return True

        # Use list comprehensions to identify surface atoms from top and bottom
        top_surface_atoms_indices = [
            idx for i, idx in enumerate(indices_sorted_by_height)
            if is_atom_on_surface(idx, indices_sorted_by_height[:i])
        ]

        bottom_surface_atoms_indices = [
            idx for i, idx in enumerate(indices_sorted_by_height[::-1])
            if is_atom_on_surface(idx, indices_sorted_by_height[::-1][:i])
        ]

        # Store the surface atom indices
        self._surface_atoms_indices = {'top':top_surface_atoms_indices, 'bottom':bottom_surface_atoms_indices}

        return self._surface_atoms_indices

        # Use a set to store indices of surface atoms for quick membership checks
        top_surface_atoms_indices = list()
        bottom_surface_atoms_indices = list()

        # Iterate over each atom, starting with the highest atom
        for i, inx in enumerate([indices_sorted_by_height, indices_sorted_by_height[::-1]]):
            for i, idx in enumerate(indices_sorted_by_height):
                position_1 = np.array([self.atomPositions[idx,0], self.atomPositions[idx,1], 0])
                # Check if the current atom is far enough from all atoms already identified as surface atoms
                threshold_pass = True
                for idx_2 in indices_sorted_by_height[:i]:
                    if self.distance(position_1 ,np.array([self.atomPositions[idx_2,0], self.atomPositions[idx_2,1], 0])) < threshold:
                        threshold_pass = False
                        break
                if threshold_pass: 
                    if i==0: bottom_surface_atoms_indices.append(idx) 
                    else:           top_surface_atoms_indices.append(idx) 

        # Convert the set of indices back to a list before returning
        self._surface_atoms_indices = list(surface_atoms_indices)

        return self._surface_atoms_indices

    def get_adsorption_sites(self, division:int=2, threshold=5.0):
        adsorption_sites = {}
        SAI = self.surface_atoms_indices

        for side in SAI:
            adsorption_sites[side]=[]
            for i1, n1 in enumerate(SAI[side]):
                position_a = self.atomPositions[n1,:]
                for n2 in SAI[side][i1+1:]:
                    position_b = self.atomPositions[n2,:]

                    if self.distance(position_a, position_b) < threshold:
                        n1,n2, position_a, position_b
                        sites = self.minimum_image_interpolation(position_a, position_b, division+2)
                        adsorption_sites[side].append(sites)

            adsorption_sites[side] = np.vstack(adsorption_sites[side])

        self._adsorption_sites = adsorption_sites
        return self._adsorption_sites 

    def summary(self, v=0):
        text_str = ''
        text_str += f'{self._latticeVectors} \n'
        text_str += f'Atom:{self._atomCount} \n'
        text_str += f'Atom:{self._uniqueAtomLabels} \n'
        text_str += f'Atom:{self._atomCountByType} \n'

        return text_str

    def readPOSCAR(self, file_location:str=None):
        file_location = file_location if type(file_location) == str else self._file_location

        lines = [n for n in self.read_file() ]
        
        self._comment = lines[0].strip()
        self._scaleFactor = list(map(float, lines[1].strip().split()))
        
        # Reading lattice vectors
        self._latticeVectors = np.array([list(map(float, line.strip().split())) for line in lines[2:5]])
        
        # Species names (optional)
        if self.is_number(lines[5].strip().split()[0]):
            self._uniqueAtomLabels = None
            offset = 0
        else:
            self._uniqueAtomLabels = lines[5].strip().split()
            offset = 1
  
        # Ions per species
        self._atomCountByType = np.array(list(map(int, lines[5+offset].strip().split())))
        
        # Selective dynamics (optional)
        if not self.is_number(lines[6+offset].strip()[0]):
            if lines[6+offset].strip()[0].capitalize() == 'S':
                self._selectiveDynamics = True
                offset += 1
            else:
                self._selectiveDynamics = False
        
        # atomic coordinated system
        if lines[6+offset].strip()[0].capitalize() in ['C', 'K']:
            self._atomCoordinateType = 'cartesian'
        else:
            self._atomCoordinateType = 'direct'

        # Ion positions
        self._atomCount = np.array(sum(self._atomCountByType))
        if self._atomCoordinateType == 'cartesian':
            self._atomPositions = np.array([list(map(float, line.strip().split()[:3])) for line in lines[7+offset:7+offset+self._atomCount]])
        else:
            self._atomPositions_fractional = np.array([list(map(float, line.strip().split()[:3])) for line in lines[7+offset:7+offset+self._atomCount]])

        self._atomicConstraints = np.array([list(map(str, line.strip().split()[3:])) for line in lines[7+offset:7+offset+self._atomCount]])
        # Check for lattice velocities
        # Check for ion velocities

    def readCIF(self, file_location:str=None):
        file_location = file_location if type(file_location) == str else self._file_location

        lines = [n for n in self.read_file() ]
        # Initialize variables
        self._latticeParameters = [0,0,0]
        self._latticeAngles = [0,0,0]
        self._atomPositions = []
        self._symmetryEquivPositions = []
        self._atomLabelsList = []

        # Flags to indicate the reading context
        reading_atoms = False
        reading_symmetry = False

        for line in lines:
            line = line.strip()

            # Lattice Parameters
            if line.startswith('_cell_length_a'):
                self._latticeParameters[0] = float(line.split()[1])
            elif line.startswith('_cell_length_b'):
                self._latticeParameters[1] = float(line.split()[1])
            elif line.startswith('_cell_length_c'):
                self._latticeParameters[2] = float(line.split()[1])

            # Lattice angles
            if line.startswith('_cell_angle_alpha'):
                self._latticeAngles[0] = np.radians(float(line.split()[1]))
            elif line.startswith('_cell_angle_beta'):
                self._latticeAngles[1] = np.radians(float(line.split()[1]))
            elif line.startswith('_cell_angle_gamma'):
                self._latticeAngles[2] = np.radians(float(line.split()[1]))


            # Symmetry Equiv Positions
            elif line.startswith('loop_'):
                reading_atoms = False  # Reset flags
                reading_symmetry = False  # Reset flags
            elif line.startswith('_symmetry_equiv_pos_as_xyz'):
                reading_symmetry = True
                continue  # Skip the line containing the column headers
            elif reading_symmetry:
                self._symmetryEquivPositions.append(line)

            # Atom positions
            elif line.startswith('_atom_site_label'):
                reading_atoms = True  # Set flag to start reading atoms
                continue  # Skip the line containing the column headers
            elif reading_atoms:
                tokens = line.split()
                if len(tokens) >= 4:  # Make sure it's a complete line
                    label, x, y, z = tokens[:4]
                    self._atomPositions.append([float(x), float(y), float(z)])
                    self._atomLabelsList.append(label)

        # Convert to numpy arrays
        self._atomPositions = np.array(self._atomPositions, dtype=np.float64)
        self._atomicConstraints = np.ones_like(self._atomPositions)
        self._atomCount = self._atomPositions.shape[0]
        self._atomCoordinateType = 'direct'
        self._selectiveDynamics = True
        self._scaleFactor = [1]

        return True

    def readSIFile(self, file_location:str=None):
        # read files commondly presente in the SI
        file_location = file_location if type(file_location) == str else self._file_location

        lines = [n for n in self.read_file() ]
                    
        # Flags to indicate which section of the file we are in
        reading_lattice_vectors = False
        reading_atomic_positions = False

        self._latticeVectors = []
        self._atomLabelsList = []
        self._atomPositions = []

        for line in lines:
            # Remove leading and trailing whitespaces
            line = line.strip()

            # Check for section headers
            if "Supercell lattice vectors" in line:
                reading_lattice_vectors = True
                reading_atomic_positions = False
                continue
            elif "Atomic positions" in line:
                reading_lattice_vectors = False
                reading_atomic_positions = True
                continue
            
            # Read data based on current section
            if reading_lattice_vectors:
                vector = [float(x) for x in line.split(",")]
                self._latticeVectors.append(vector)
            elif reading_atomic_positions:
                elements = line.split()
                self._atomLabelsList.append(elements[0])
                self._atomPositions.append([ float(n) for n in elements[1:] ])

        self._atomPositions = np.array(self._atomPositions)             
        self._atomLabelsList = np.array(self._atomLabelsList)             
        self._latticeVectors = np.array(self._latticeVectors)             
        self._atomCoordinateType = 'Cartesian'
        self._atomicConstraints = np.ones_like(self._atomPositions)
        self._atomCount = self._atomPositions.shape[0]
        self._selectiveDynamics = True
        self._scaleFactor = [1]

        return True

'''
path = '/home/akaris/Documents/code/Physics/VASP/v6.1/files/dataset/CoFeNiOOH_jingzhu/bulk_NiFe/rattle'
ap = PeriodicSystem(file_location=path+'/POSCAR')
ap.readPOSCAR()
print(ap.atomLabelsList)
ap.generate_supercell()
print(ap.atomLabelsList.shape)
print(ap.atomPositions.shape)

ap.exportAsPOSCAR(path+'/POSCAR_222')


print(ap.surface_atoms_indices)

ap.readSIFile()

print(ap.pbc)


print(ap.atomPositions)
ap.exportAsPDB(path+'/PDB.pdb')

ap.readSIFile()
#ap.pack_to_unit_cell()
ap.exportAsPOSCAR(path+'/POSCAR')

path = '/home/akaris/Documents/code/Physics/VASP/v6.1/files/POSCAR/Cristals/NiOOH/*OH surface with Fe(HS)'
ap = PeriodicSystem(file_location=path+'/SUPERCELL')
ap.readSIFile()
ap.exportAsPOSCAR(path+'/POSCAR')


path = '/home/akaris/Documents/code/Physics/VASP/v6.1/files/POSCAR/Eg'
ap = PeriodicSystem(file_location=path+'/POSCAR_tetragonal')
ap.readPOSCAR()
print(ap.atomPositions)
print( ap.latticeType )

print( ap.latticeVectors )
print( ap.minimum_image_distance( [0,0,0], [0,0,4.187]) )
fsad

path = '/home/akaris/Documents/code/Physics/VASP/v6.1/files/POSCAR/Cristals/NiOOH/Bulk FeOOH with β-NiOOH structure (Fe(LS))'
path = '/home/akaris/Documents/code/Physics/VASP/v6.1/files/POSCAR/Cristals/NiOOH/Bulk FeOOH with β-NiOOH structure (Fe(HS))'
path = '/home/akaris/Documents/code/Physics/VASP/v6.1/files/POSCAR/Cristals/NiOOH/Bulk β-NiOOH doped with 1 Fe(HS)'

ap = PeriodicSystem(file_location=path+'/SUPERCELL')
ap.readSIFile()
print( ap.latticeType )
ap.exportAsPOSCAR(path+'/POSCAR')
'''


'''
_uniqueAtomLabels
uniqueAtomLabels

#ap = PeriodicSystem(file_location='/home/akaris/Documents/code/Physics/VASP/v6.1/files/POSCAR/Cristals/Hydrotalcite/Hydrotalcite.cif')
#ap.readCIF()
#print(ap.latticeParameters, ap.latticeAngles)
#ap.exportAsPOSCAR()

ap = PeriodicSystem(file_location='/home/akaris/Documents/code/Physics/VASP/v6.1/files/POSCAR/SAM/FeBzBzAu/FePC_5Bz_OH')
ap.readPOSCAR()


print(ap.atomicConstraints )

print( ap.atomPositions )
ap.cellDuplication( [2,2,1] )
print( ap.atomicConstraints.shape )
'''


