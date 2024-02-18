# En __init__.py del paquete que contiene AtomPositionManager
try:
    from sage_lib.IO.structure_handling_tools.AtomPositionManager import AtomPositionManager
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing sage_lib.IO.structure_handling_tools.AtomPositionManager: {str(e)}\n")
    del sys

try:
    import numpy as np
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys

class PeriodicSystem(AtomPositionManager):
    """
    A class representing a periodic system, typically a crystalline structure.

    Methods:
        __init__(file_location, name, **kwargs): Initializes the PeriodicSystem instance.
        atomCoordinateType: Property that returns the type of atom coordinates used.
        surface_atoms_indices: Property that returns indices of surface atoms.
        distance_matrix: Property that calculates and returns the distance matrix.
        latticeType: Property that determines and returns the lattice type.
        atomPositions_fractional: Property that calculates and returns fractional atom positions.
        atomPositions: Property that calculates and returns atom positions in Cartesian coordinates.
        reciprocalLatticeVectors: Property that calculates and returns reciprocal lattice vectors.
        latticeAngles: Property that calculates and returns the lattice angles.
        latticeVectors: Property that calculates and returns lattice vectors.
        latticeVectors_inv: Property that calculates and returns the inverse of lattice vectors.
        latticeParameters: Property that calculates and returns lattice parameters.
        cellVolumen: Property that calculates and returns the volume of the unit cell.
        pbc: Property that determines and returns periodic boundary conditions.
        is_surface: Property that determines if the structure is a surface.
        is_bulk: Property that determines if the structure is bulk.
        get_volume(): Returns the volume of the unit cell.
        move_atom(atom_index, displacement): Moves an atom by the specified displacement.
        to_fractional_coordinates(cart_coords): Converts Cartesian coordinates to fractional coordinates.
        to_cartesian_coordinates(frac_coords): Converts fractional coordinates to Cartesian coordinates.
        distance(r1, r2): Calculates the minimum image distance between two points.
        wrap(): Adjusts atom positions to be within the unit cell.
        pack_to_unit_cell(): Repositions atoms within the unit cell according to the minimum image convention.
        minimum_image_distance(r1, r2, n_max): Calculates the minimum distance between two points considering periodicity.
        minimum_image_interpolation(r1, r2, n, n_max): Interpolates points between two positions considering periodicity.
        generate_supercell(repeat): Generates a supercell from the unit cell.
        is_point_inside_unit_cell(point): Checks if a point is inside the unit cell.
        get_vacuum_box(tolerance): Determines the vacuum box for surface calculations.
        find_opposite_atom(atom_position, label, tolerance_z, tolerance_distance): Finds the symmetrically opposite atom.
        find_surface_atoms(threshold): Identifies indices of surface atoms based on their relative height.
        get_adsorption_sites(division, threshold): Identifies potential adsorption sites on a surface.
        summary(v): Generates a summary string of the periodic system's properties.

    Attributes:
        _reciprocalLatticeVectors (np.array): Array of reciprocal lattice vectors.
        _latticeVectors (np.array): Array of lattice vectors.
        _latticeVectors_inv (np.array): Inverse of the lattice vectors array.
        _symmetryEquivPositions (list): List of symmetry-equivalent positions.
        _atomCoordinateType (str): Type of atom coordinates ('Cartesian' or 'Direct').
        _latticeParameters (list): Parameters of the lattice.
        _latticeAngles (list): Angles of the lattice in radians.
        _cellVolumen (float): Volume of the unit cell.
        _atomPositions_fractional (np.array): Fractional atom positions.
        _latticeType (str): Type of the lattice (e.g., 'SimpleCubic', 'Tetragonal').
        _latticeType_tolerance (float): Tolerance used in determining the lattice type.
        _distance_matrix (np.array): Matrix of distances between atoms.
        _pbc (list): Periodic boundary conditions.
        _is_surface (bool): Indicates if the structure is a surface.
        _is_bulk (bool): Indicates if the structure is bulk.
        _surface_atoms_indices (list): Indices of atoms that are on the surface.
        Additional inherited attributes from AtomPositionManager.
    """
    
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
    def atomCoordinateType(self):
        if isinstance(self._atomCoordinateType, str):
            return self._atomCoordinateType
        else:
            self._atomCoordinateType = 'Cartesian'
            return self._atomCoordinateType

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
        elif self.latticeParameters is not None or self.latticeAngles is not None:
            a, b, c = self.latticeParameters
            alpha, beta, gamma = self.latticeAngles  # Convert to radians

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
            if type(self.latticeVectors) is None:
                self._pbc = [False, False, False]
            else:
                self._pbc = [True, True, True]

            '''
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
            '''
            return self._pbc

    def get_real_coordinates(self, r):
        return np.dot(self.get_fractional_coordinates(r), self.latticeVectors)

    def get_fractional_coordinates(self, r):
        return np.dot(r, self.latticeVectors_inv) % 1.0

    def get_pbc(self): return self.pbc

    def get_atomic_numbers(self): return np.array([self.atomic_numbers[label] for label in self.atomLabelsList])

    def get_cell(self): return np.array(self.latticeVectors)

    def get_positions(self): return np.array(self.atomPositions)

    def get_normal_vector_to_lattice_plane(self, ):
        """
        Calculate the normal vectors to the lattice planes.

        Returns:
        list: A list containing the normal vectors to the lattice planes.
        """
        a, b, c = self.latticeVectors
        return [np.cross(b, c), np.cross(a, c), np.cross(a, b)]

    def get_distance_between_lattice_plane(self, ):
        """
        Calculate the distances between two parallel lattice planes.

        Returns:
        list: A list of distances from the origin to each lattice plane.
        """
        normal_vectors = self.get_normal_vector_to_lattice_plane()
        a, b, c = self.latticeVectors
        return [np.dot(lattice_vector, normal) / np.dot(normal, normal) * normal for normal, lattice_vector in zip(normal_vectors, [a, b, c])]

    def get_distance_to_lattice_plane(self, r):
        """
        Calculate the distances from a point to the lattice planes.

        Parameters:
        r (array_like): The coordinates of the point.

        Returns:
        ndarray: An array of distances from the point to each lattice plane.
        """
        normal_vectors = self.get_normal_vector_to_lattice_plane()
        real_r = self.get_real_coordinates(r)
        distance_planes = get_distance_between_lattice_plane()

        real_r_proj =  [np.dot(real_r, normal_vectors[i]) / np.dot(normal_vectors[i], normal_vectors[i]) * normal_vectors[i] for i in range(3)]

        real_r_proj_s0 = [linalg.norm(real_r_proj_i) for real_r_proj_i in real_r_proj ]
        real_r_proj_s1 = [np.linalg.norm(distance_planes[i] - real_r_proj_i) for real_r_proj_i in real_r_proj ]

        return np.concatenate(real_r_proj_s0, real_r_proj_s1)

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

    def get_volume(self,):
        return self.cellVolumen


    def to_fractional_coordinates(self, cart_coords):
        inv_lattice_matrix = np.linalg.inv(self.latticeVectors)
        return np.dot(inv_lattice_matrix, cart_coords.T).T
    
    def to_cartesian_coordinates(self, frac_coords):
        frac_coords = np.array(frac_coords, np.float64)
        return np.dot(self.latticeVectors.T, frac_coords.T).T
    
    def wrap(self, ):
        self.pack_to_unit_cell()
        
    def pack_to_unit_cell(self, ):
        # Apply minimum image convention
        self._atomPositions_fractional = self.atomPositions_fractional%1.0
        
        # Convert back to Cartesian coordinates
        self._atomPositions = np.dot(self.atomPositions_fractional, self.latticeVectors)

    def minimum_image_interpolation(self, r1, r2, n:int=2, n_max=1):
        """

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
        self._latticeVectors *= np.array(repeat)[:, np.newaxis]
        self._atomPositions_fractional = None
        self._atomCount = None
        self._atomCountByType = None
        self._fullAtomLabelString = None

        return True

    def stack(self, AtomPositionManager:object, direction:str='Z'):
        '''
        add AtomPositionManager atoms at the end of the self cell in a given direction
        '''
        index = {'X':0, 'Y':1, 'Z':2}[direction.upper()]
        displacement_vector = self.latticeVectors[index]
        atom_positions = np.vstack([np.array(self.atomPositions), AtomPositionManager.atomPositions+displacement_vector])

        atomicConstraints = np.vstack([self.atomicConstraints, AtomPositionManager.atomicConstraints])
        atomLabelsList = np.concatenate([self.atomLabelsList, AtomPositionManager.atomLabelsList])

        latticeVectors = np.where(np.arange(3)[:, None] == index, self.latticeVectors + AtomPositionManager.latticeVectors, np.maximum(self.latticeVectors, AtomPositionManager.latticeVectors))

        self._atomLabelsList = atomLabelsList
        self._atomicConstraints = atomicConstraints
        self._atomPositions = atom_positions
        self._latticeVectors = latticeVectors

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

    # ======== SURFACE CODE ======== # # ======== SURFACE CODE ======== # # ======== SURFACE CODE ======== # # ======== SURFACE CODE ======== # 
    def get_vacuum_box(self, tolerance:float=0.0):
        '''
        '''
        tolerance /= np.linalg.norm( self.latticeVectors[2,:] )

        max_position = np.max( self.atomPositions_fractional, axis=0 )[2]
        min_position = np.min( self.atomPositions_fractional, axis=0 )[2]

        vacuum_box = np.array([
                    self.latticeVectors[0,:], 
                    self.latticeVectors[1,:], 
                    self.to_cartesian_coordinates([0,0,(1-max_position)-tolerance + min_position-tolerance])] )

        return vacuum_box, self.to_cartesian_coordinates([0,0,max_position+tolerance]) # vacuum, initial position of vacum box

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
    # ======== SURFACE CODE ======== # # ======== SURFACE CODE ======== # # ======== SURFACE CODE ======== # # ======== SURFACE CODE ======== # 
        
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