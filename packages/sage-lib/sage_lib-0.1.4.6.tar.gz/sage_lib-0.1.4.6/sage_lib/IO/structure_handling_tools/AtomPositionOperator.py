try:
    import numpy as np
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys

try:
    from scipy.spatial.distance import cdist 
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing scipy.spatial.KDTree: {str(e)}\n")
    del sys

try:
    import re
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing re: {str(e)}\n")
    del sys

try:
    from collections import Counter
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing collections: {str(e)}\n")
    del sys

class AtomPositionOperator:
    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        pass
        #super().__init__(name=name, file_location=file_location)
        
    #def distance(self, r1, r2): return np.linalg.norm(r1, r2)

    def move_atom(self, atom_index:int, displacement:np.array):
        """
        Moves an atom by a specified displacement.

        Args:
            atom_index (int): The index of the atom to move.
            displacement (np.array): A NumPy array representing the displacement vector.

        This method modifies the position of the specified atom and invalidates any cached distance matrices.
        """
        self._atomPositions[atom_index,:] += displacement
        self._distance_matrix = None
        self._kdtree = None
        self._atomPositions_fractional = None

    def set_atomPositions(self, new_atomPositions:np.array):
        """
        Sets the atom positions to new values.

        Args:
            new_atomPositions (np.array): A NumPy array of new atom positions.

        This method updates the atom positions and invalidates any cached distance matrices and fractional positions.
        """
        self._atomPositions = new_atomPositions
        self._distance_matrix = None
        self._kdtree = None
        self._atomPositions_fractional = None

    def set_atomPositions_fractional(self, new_atomPositions:np.array):
        """
        Sets the fractional atom positions to new values.

        Args:
            new_atomPositions (np.array): A NumPy array of new fractional atom positions.

        This method updates the fractional atom positions and invalidates any cached distance matrices and absolute positions.
        """
        self._atomPositions_fractional = new_atomPositions
        self._distance_matrix = None
        self._kdtree = None
        self._atomPositions = None

    def set_latticeVectors(self, new_latticeVectors:np.array, edit_positions:bool=True):
        """
        Sets the lattice vectors to new values and optionally adjusts atom positions.

        Args:
            new_latticeVectors (np.array): A NumPy array of new lattice vectors.
            edit_positions (bool): If True, atom positions will be reset; otherwise, they will be retained.

        This method updates the lattice vectors and invalidates any cached inverse lattice vectors and distance matrices.
        """
        self._latticeVectors = new_latticeVectors
        self._latticeVectors_inv = None

        self._atomPositions = None if edit_positions else self._atomPositions
        self._distance_matrix = None if edit_positions else self._distance_matrix
        self._kdtree = None if edit_positions else self._kdtree

        self._atomPositions_fractional = None if not edit_positions else self._atomPositions_fractional
 
    def remove_atom(self, atom_index:np.array):
        """
        Removes one or more atoms from the molecule.

        Args:
            atom_index (np.array): An array of indices of atoms to remove.

        This method updates various properties of the molecule, including atomic constraints, positions, labels, charges, magnetization, and forces. It also adjusts the count of atoms and recalculates any necessary properties.
        """
        atom_index = np.array(atom_index, dtype=np.int64)
        """Remove an atom at the given index."""
        self._atomicConstraints = np.delete(self.atomicConstraints, atom_index, axis=0)
        self._atomPositions = np.delete(self.atomPositions, atom_index, axis=0)
        self._atomPositions_fractional = np.delete(self.atomPositions_fractional, atom_index, axis=0)
        self._atomLabelsList = np.delete(self.atomLabelsList, atom_index)
        self._total_charge = np.delete(self.total_charge, atom_index,  axis=0) if self._total_charge is not None else self._total_charge
        self._magnetization = np.delete(self.magnetization, atom_index,  axis=0) if self._magnetization is not None else self._magnetization
        self._total_force = np.delete(self.total_force, atom_index,  axis=0) if self._total_force is not None else self._total_force
        
        self._atomCount -= atom_index.shape[0]
        self._atomCountByType = None
        self._fullAtomLabelString = None
        self._uniqueAtomLabels = None

        if self._distance_matrix is not None:
            self._distance_matrix = np.delete(self._distance_matrix, var, axis=0)  # Eliminar fila
            self._distance_matrix = np.delete(self._distance_matrix, var, axis=1)  # Eliminar columna
        self._kdtree = None

    def add_atom(self, atomLabels: str, atomPosition: np.array, atomicConstraints: np.array = None) -> bool:
        """
        Adds an atom to the AtomContainer.

        :param atomLabels: Label for the new atom.
        :param atomPosition: Position of the new atom as a numpy array.
        :param atomicConstraints: Atomic constraints as a numpy array (defaults to [1,1,1]).
        """
        atomLabels = np.array([atomLabels]) if isinstance(atomLabels, str) else np.array(atomLabels)
        atomicConstraints = np.ones_like(atomPosition) if atomicConstraints is None else atomicConstraints  

        self._atomPositions = np.atleast_2d(atomPosition) if self.atomPositions is None else np.vstack([self.atomPositions, atomPosition])
        self._atomLabelsList = np.array(atomLabels) if self.atomLabelsList is None else np.concatenate([self.atomLabelsList, atomLabels])
        self._atomicConstraints = np.vstack([self.atomicConstraints, atomicConstraints]) if self.atomicConstraints is not None else np.atleast_2d(atomicConstraints)
        self._atomCount = atomLabels.shape[0] if self._atomCount is None else self._atomCount + atomLabels.shape[0]
        self._reset_dependent_attributes()
        self.group_elements_and_positions()
        return True

    def move_atom(self, atom_index:int, displacement:np.array):
        new_position = self.atomPositions[atom_index,:] + displacement
        self._atomPositions[atom_index,:] = new_position
        self._atomPositions_fractional = None
        self._distance_matrix = None
        self._kdtree = None

    def change_ID(self, atom_ID:str, new_atom_ID:str) -> bool:
        """
        Changes the identifier (ID) of atoms in the structure.

        This method searches for all atoms with a specific ID and replaces it with a new ID. It is useful when modifying
        the atomic structure, for instance, to represent different isotopes or substitutional defects.

        Parameters:
            ID (str): The current ID of the atoms to be changed.
            new_atom_ID (str): The new ID to assign to the atoms.

        Returns:
            bool: True if the operation is successful, False otherwise.

        Note:
            This method also resets related attributes that depend on atom IDs, such as the full atom label string,
            atom count by type, and unique atom labels, to ensure consistency in the data structure.
        """
        # Replace all occurrences of ID with new_atom_ID in the atom labels list
        self.atomLabelsList
        self._atomLabelsList[ self.atomLabelsList==atom_ID ] = new_atom_ID
        
        # Reset related attributes to nullify any previous computations
        self._fullAtomLabelString= None
        self._atomCountByType = None
        self._uniqueAtomLabels = None

    def set_ID(self, atom_index:int, ID:str) -> bool:
        """
        Sets a new identifier (ID) for a specific atom in the structure.

        This method assigns a new ID to the atom at a specified index. It is particularly useful for labeling or re-labeling
        individual atoms, for example, in cases of studying impurities or localized defects.

        Parameters:
            atom_index (int): The index of the atom whose ID is to be changed.
            ID (str): The new ID to assign to the atom.

        Returns:
            bool: True if the operation is successful, False otherwise.

        Note:
            Similar to change_ID, this method also resets attributes like the full atom label string,
            atom count by type, and unique atom labels, to maintain data integrity.
        """
        # Set the new ID for the atom at the specified index
        self._atomLabelsList[atom_index] = ID

        # Reset related attributes to nullify any previous computations
        self._fullAtomLabelString= None
        self._atomCountByType = None
        self._uniqueAtomLabels = None

    def has(self, ID:str):
        """
        Checks if the specified atom ID exists in the atom labels list.

        This method provides a simple way to verify the presence of an atom ID
        within the object's list of atom labels.

        Args:
            ID (str): The atom ID to check for.

        Returns:
            bool: True if the ID exists at least once; otherwise, False.
        """
        # Delegate to has_atom_ID with default minimum and maximum amounts
        return self.has_atom_ID(ID=ID, amount_min=1, amoun_max=np.inf)

    def has_atom_ID(self, ID:str, amount_min:int=1, amoun_max:int=np.inf):
        """
        Checks if the specified atom ID exists within a specified range of occurrences.

        This method determines whether the count of a specific atom ID in the atom labels
        list falls within the given minimum and maximum range.

        Args:
            ID (str): The atom ID to check for.
            amount_min (int, optional): The minimum acceptable number of occurrences. Defaults to 1.
            amount_max (int, optional): The maximum acceptable number of occurrences. Defaults to infinity.

        Returns:
            bool: True if the count of the ID falls within the specified range; otherwise, False.
        """
        count_ID = self.ID_amount(ID=ID)
        return count_ID >= amount_min and count_ID <= amoun_max

    def atom_ID_amount(self, ID:str):
        """
        Counts the number of times the specified atom ID appears in the atom labels list.

        This method provides a count of how many times a given atom ID occurs
        in the object's list of atom labels.

        Args:
            ID (str): The atom ID to count.

        Returns:
            int: The number of occurrences of the atom ID.
        """
        # Count the occurrences of the specified ID in the atom labels list
        return np.count_nonzero(self.atomLabelsList == ID)

    def _reset_dependent_attributes(self):
        """
        Resets dependent attributes to None.
        """
        attributes_to_reset = ['_total_charge', '_magnetization', '_total_force', '_atomPositions_fractional', 
                               '_atomCountByType', '_fullAtomLabelString', '_uniqueAtomLabels', '_distance_matrix', '_kdtree']
        for attr in attributes_to_reset:
            setattr(self, attr, None)

    # =========== NEIGHBORS =========== # # =========== NEIGHBORS =========== # # =========== NEIGHBORS =========== # # =========== NEIGHBORS =========== # 
    def distance(self, r1, r2, periodic:bool=None):
        periodic = not type(self.latticeVectors) is None if periodic is None else periodic
     
        if periodic:
            return self.minimum_image_distance(r1, r2)
        else:
            return self.distance_direct(r1, r2)

    def distance_ID(self, ID1, ID2, distance_matrix:bool=True, periodic:bool=None):
        periodic = not type(self.latticeVectors) is None if periodic is None else periodic
     
        if periodic:
            if distance_matrix:
                return self.distance_matrix[ID1, ID2]
            else:
                return self.minimum_image_distance( self.atomPositions(ID1), self.atomPositions(ID2) )
        else:
            return self.distance_direct( self.atomPositions(ID1), self.atomPositions(ID2) )

    def distance_direct(self, r1, r2): 
        return np.linalg.norm(r1 - r2)

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

    def distance_matrix_calculator(self, first_periodic_img_aprox:bool=True, periodic:bool=None):
        """
        Calculate the distance matrix for a set of atomic positions, considering periodic boundary conditions.

        Parameters:
        first_periodic_img_aprox (bool): If True, uses the first periodic image approximation for distance calculation.
        periodic (bool): If True, enables the consideration of periodic boundary conditions. If None, it is 
                         determined based on whether lattice vectors are defined.

        Returns:
        numpy.ndarray: A distance matrix of shape (atomCount, atomCount).
        """

        # Determine if the system is periodic based on the presence of lattice vectors
        # if 'periodic' is not explicitly provided.
        periodic = not isinstance(self.latticeVectors, type(None)) if periodic is None else periodic

        if periodic: # for periodic 
            return self._calculate_periodic_distance_matrix(first_periodic_img_aprox)
        else:
            return cdist(self._atomPositions, self._atomPositions, 'euclidean')

    def _calculate_periodic_distance_matrix(self, first_periodic_img_aprox: bool):
        """ Helper method to calculate the distance matrix for periodic systems. """
        if first_periodic_img_aprox:
            images = self._generate_periodic_images()
            return cdist(self.atomPositions, images, 'euclidean')
        else:
            return self._calculate_direct_minimum_image_distances()

    def _generate_periodic_images(self):
        """ Generate periodic images of the atoms within the specified range without using itertools. """
        periodic_image_range = range(-1, 2)  # Equivalent to periodic_image = 1
        images = self.atomPositions.copy()

        for x_offset in periodic_image_range:
            for y_offset in periodic_image_range:
                for z_offset in periodic_image_range:
                    if (x_offset, y_offset, z_offset) != (0, 0, 0):
                        offset = np.dot([x_offset, y_offset, z_offset], self.latticeVectors)
                        images = np.vstack([images, self.atomPositions + offset])

        return images

    def _calculate_direct_minimum_image_distances(self):
        """ Calculate distances using the minimum image convention. """
        distance_matrix = np.zeros((self.atomCount, self.atomCount))
        for atom_index_i in range(self.atomCount):
            for atom_index_j in range(atom_index_i, self.atomCount):
                distance_matrix[atom_index_i, atom_index_j] = self.minimum_image_distance(
                    self.atomPositions[atom_index_i], self.atomPositions[atom_index_j])

        return distance_matrix

    # ====== KDTREE ======
    def count_neighbors(self, other, r, p=2.):
        """
        Count the number of neighbors each point in 'other' has within distance 'r'.

        Parameters:
        other: PeriodicCKDTree or cKDTree
            The tree containing points for which neighbors are to be counted.
        r: float
            The radius within which to count neighbors.
        p: float, optional (default=2)
            Which Minkowski p-norm to use.

        Returns:
        numpy.ndarray:
            An array of the same length as the number of points in 'other', 
            where each element is the count of neighbors within distance 'r'.
        """
        return self.kdtree.count_neighbors(other=other.kdtree, r=r, p=p)

    def find_closest_neighbors(self, r, kdtree:bool=True):
        if kdtree:
            return None
        else:
            return self.find_closest_neighbors_distance(r)

    def find_closest_neighbors_distance(self, r, ):
        # 
        #ree = KDTree( self.atomPositions )

        #
        #dist, index = tree.query(r)
        index_min, distance_min = -1, np.inf
        for index, atom_position in enumerate(self.atomPositions):
            distance_index = self.distance(atom_position, r)
            if distance_index < distance_min:
                distance_min = distance_index
                index_min = index

        return distance_min, index_min

    def find_ID_neighbors(self, other, r, p=2., eps=0):
        """
        Find all points in 'other' tree within distance 'r' of each point in this tree.

        Parameters:
        other: PeriodicCKDTree or cKDTree
            The tree containing points to compare against the current tree.
        r: float
            The radius within which to search for neighboring points.
        p: float, optional (default=2)
            Which Minkowski p-norm to use. 
        eps: float, optional (default=0)
            Approximate search. The tree is not explored for branches that are 
            further than r/(1+eps) away from the target point.

        Returns:
        list of lists:
            For each point in this tree, a list of indices of neighboring points 
            in 'other' tree is returned.
        """
        return self.kdtree.query_ball_tree(other=other, r=r, p=p, eps=eps)

    def find_all_neighbors_radius(self, x, r, p=2., eps=0):
        """
        Find all points within distance r of point(s) x.

        Parameters
        ----------
        x : array_like, shape tuple + (self.m,)
            The point or points to search for neighbors of.
        r : positive float
            The radius of points to return.
        p : float, optional
            Which Minkowski p-norm to use.  Should be in the range [1, inf].
        eps : nonnegative float, optional
            Approximate search. Branches of the tree are not explored if their
            nearest points are further than ``r / (1 + eps)``, and branches are
            added in bulk if their furthest points are nearer than
            ``r * (1 + eps)``.

        Returns
        -------
        results : list or array of lists
            If `x` is a single point, returns a list of the indices of the
            neighbors of `x`. If `x` is an array of points, returns an object
            array of shape tuple containing lists of neighbors.

        Notes
        -----
        If you have many points whose neighbors you want to find, you may
        save substantial amounts of time by putting them in a
        PeriodicCKDTree and using query_ball_tree.
        """
        return self.kdtree.query_ball_point(x, r, p=2., eps=0)

    def find_n_closest_neighbors(self, r, n:int, kdtree:bool=True, eps:int=0, p:int=2, distance_upper_bound:float=np.inf):
        if kdtree:
            return self.kdtree.query(x=r, k=n, eps=eps, p=p, distance_upper_bound=distance_upper_bound.inf)
        else:
            return self.find_n_closest_neighbors_distance(r, n)

    def find_n_closest_neighbors_distance(self, r, n):
        """Find the n closest neighbors to a given atom."""
        #distance_matrix = self.distanceamtrix
        #distances = distance_matrix[atom_index]
        
        # Sort the distances and get the indices of the n closest neighbors.
        # We exclude the first index because it's the atom itself (distance=0).
        distances = [self.distance( r, a) for a in self.atomPositions ]
        closest_indices = np.argsort( distances )[:n]
        
        # Get the labels and positions of the closest neighbors.
        closest_labels = [self._atomLabelsList[i] for i in closest_indices]
        closest_distance = [ distances[i] for i in closest_indices]
        
        return closest_distance, closest_indices 

    def get_molecular_graph(self, metric:str='kdtree', sigma:float=1.2, ID_filter:bool=False):
        '''
        '''
        n_atoms = self.atomCount
        visited = np.zeros(n_atoms, dtype=bool)
        graph_representation = []
        r_max = np.max( [self.covalent_radii[a] for a in self.uniqueAtomLabels] )

        def dfs(atomo, grupo_actual):
            """Recorrido en profundidad para encontrar átomos relacionados."""
            max_bond_lenth = (self.covalent_radii[self.atomLabelsList[atomo]]+r_max)*sigma
            neighbors = self.find_all_neighbors_radius(self.atomPositions[atomo], max_bond_lenth )
            for neighbor in neighbors:
                if self.distance( self.atomPositions[atomo], self.atomPositions[neighbor]) < (self.covalent_radii[self.atomLabelsList[atomo]]+self.covalent_radii[self.atomLabelsList[neighbor]])*sigma and not visited[neighbor]:
                    if ID_filter:
                        if self.atomLabelsList[atomo] == self.atomLabelsList[neighbor]:
                            visited[neighbor] = True
                            grupo_actual.add(neighbor)
                            dfs(neighbor, grupo_actual)
                    else:
                        visited[neighbor] = True
                        grupo_actual.add(neighbor)
                        dfs(neighbor, grupo_actual)  

        for atomo in range(n_atoms):
            if not visited[atomo]:
                visited[atomo] = True
                grupo_actual = {atomo}
                dfs(atomo, grupo_actual)
                graph_representation.append(grupo_actual)

        self._graph_representation = graph_representation
        return self._graph_representation

    def count_species(self, sigma:float=1.2):
        self.get_molecular_graph(sigma=sigma)

        count_dict = {}
        for n in self.graph_representation:

            label_list = sorted([self.atomLabelsList[l] for l in n ])
            
            key = ''.join(f"{elem}{count}" for elem, count in Counter(label_list).items())
            if key in count_dict:
                count_dict[key] += 1
            else:
                count_dict[key] = 1

        return count_dict

    def get_max_bond_lenth(self, metric='covalent_radii', specie:str=None  ):
        if metric.upper() == 'COVALENT_RADII':
            if type(specie) == str:
                return np.max( [self.covalent_radii[a] for a in self.uniqueAtomLabels] ) + self.covalent_radii[specie]
            else:
                return np.max( [self.covalent_radii[a] for a in self.uniqueAtomLabels] ) * 2

        return None

    # =========== NEIGHBORS =========== # # =========== NEIGHBORS =========== # # =========== NEIGHBORS =========== # # =========== NEIGHBORS =========== # 

    # =========== OPERATIONS =========== # # =========== OPERATIONS =========== # # =========== OPERATIONS =========== # # =========== OPERATIONS =========== # 
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

    def generate_random_rotation_matrix(self, ):
        """
        Generate a random rotation matrix in 3D space.

        Returns:
            numpy array: Rotation matrix (3x3).
        """
        # Random rotation angles for each axis
        theta_x, theta_y, theta_z = np.random.uniform(0, 2*np.pi, 3)

        # Rotation matrices around each axis
        Rx = np.array([[1, 0, 0],
                       [0, np.cos(theta_x), -np.sin(theta_x)],
                       [0, np.sin(theta_x),  np.cos(theta_x)]])
        
        Ry = np.array([[np.cos(theta_y), 0, np.sin(theta_y)],
                       [0, 1, 0],
                       [-np.sin(theta_y), 0, np.cos(theta_y)]])
        
        Rz = np.array([[np.cos(theta_z), -np.sin(theta_z), 0],
                       [np.sin(theta_z),  np.cos(theta_z), 0],
                       [0, 0, 1]])

        # Combined rotation
        R = np.dot(Rz, np.dot(Ry, Rx))
        return R

    def generate_uniform_translation_from_fractional(self, fractional_interval:np.array=np.array([[0,1],[0,1],[0,1]],dtype=np.float64), latticeVectors:np.array=None):
        """
        Generate a uniform translation vector.

        Args:
            interval (list of tuples): [(min_x, max_x), (min_y, max_y), (min_z, max_z)]

        Returns:
            numpy array: Translation vector.
        """
        latticeVectors = latticeVectors if latticeVectors is not None else self.latticeVectors
        return np.dot( np.array([np.random.uniform(low, high) for low, high in fractional_interval]) , latticeVectors)
    # =========== OPERATIONS =========== # # =========== OPERATIONS =========== # # =========== OPERATIONS =========== # # =========== OPERATIONS =========== # 

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
        self.set_atomPositions(np.array(atomPositions_new))

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


    def compress(self, compress_factor: list = None, verbose: bool = False):
        """
        Compresses the atomic positions by a specified factor along each dimension.

        This method scales the atomic positions stored in the class by the given compress factors. 
        It is designed to handle a 3-dimensional space, thus expecting three compress factors.

        Parameters:
        - compress_factor (list or numpy.ndarray): A list or numpy array of three elements 
          representing the compress factors for each dimension.
        - verbose (bool): Flag for verbose output.

        Raises:
        - ValueError: If compress_factor is not a list or numpy.ndarray, or if it does not 
          contain exactly three elements.

        Returns:
        None
        """

        # Convert the compress_factor to a numpy array if it is a list
        compress_factor = np.array(compress_factor, dtype=np.float64) if isinstance(compress_factor, list) else compress_factor

        # Check if compress_factor is a numpy array with exactly three elements
        if isinstance(compress_factor, np.ndarray) and compress_factor.shape[0] != 3:
            raise ValueError("Compress factors must be a tuple or list of three elements.")

        if self.latticeVectors is not None:
            # 
            self.set_latticeVectors(self.latticeVectors * compress_factor, edit_positions=True)
        else:
            # 
            self.set_atomPositions(self.atomPositions * compress_factor)

        # Optional verbose output
        if verbose:
            print("Atom positions compressed successfully.")

    # =========== DEFECTS =========== # # =========== DEFECTS =========== # # =========== DEFECTS =========== # # =========== DEFECTS =========== # 
    def introduce_vacancy(self, atom_index: int, tolerance_z=4, verbosity:bool=False):
        """
        Introduce a vacancy by removing an atom.
        """
        # Remove the atom at the specified index
        removed_atom_position = self.atomPositions[atom_index]
        removed_atom_label = self.atomLabelsList[atom_index]
        self.remove_atom(atom_index)

        if self.is_surface:
            opposite_atom_index = self.find_opposite_atom(removed_atom_position, removed_atom_label, tolerance_z=tolerance_z)
            if opposite_atom_index is not None:
                self.remove_atom(opposite_atom_index)

        if verbosity: print( f'Vacancy {removed_atom_label} generated.')

    def introduce_interstitial(self, new_atom_label:str, new_atom_position:np.array, verbosity:bool=False):
        """
        Introduce a self-interstitial defect.
        
        A self-interstitial is a type of point defect where an extra atom is added to an interstitial site.
        This method adds an atom to a specified interstitial position and updates the associated metadata.
        """ 
        self.add_atom(atomLabels=new_atom_label, atomPosition=new_atom_position)

        if verbosity: print( f'Interstitial {new_atom_label} at {removed_atom_position}.')

    def introduce_substitutional_impurity(self, atom_index:int, new_atom_label: str, verbosity:bool=False):
        """
        Introduce a substitutional impurity.
        
        A substitutional impurity is a type of point defect where an atom is replaced by an atom of a different type.
        This method modifies the type of atom at the specified index to a new type.
        """
        # Remove the atom at the specified index
        removed_atom_position = self.atomPositions[atom_index]
        removed_atom_label = self.atomLabelsList[atom_index]
        self.remove_atom(atom_index)
        self.add_atom(atomLabels=new_atom_label, atomPosition=removed_atom_position)

        if verbosity: print( f'Substitution {removed_atom_label} >> {new_atom_label} at {removed_atom_position}.')
        # Update _atomCountByType here similar to introduce_vacancy
    # =========== DEFECTS =========== # # =========== DEFECTS =========== # # =========== DEFECTS =========== # # =========== DEFECTS =========== # 

    def summary(self, verbosity=0):
        """
        Generates a textual summary of the AtomPositionOperator's properties.

        Args:
            verbosity (int): The level of detail for the summary. Higher values mean more details.

        Returns:
            str: A string summarizing the key properties of the AtomPositionOperator.
        """
        text_str = "AtomPositionOperator Summary:\n"
        text_str += "-" * 30 + "\n"

        # Lattice vectors
        if self._latticeVectors is not None:
            text_str += f"Lattice Vectors:\n{self._latticeVectors}\n"
        else:
            text_str += "Lattice Vectors: Not defined\n"

        # Atom positions
        if self._atomPositions is not None:
            text_str += f"Number of Atom Positions: {len(self._atomPositions)}\n"
        else:
            text_str += "Atom Positions: Not defined\n"

        # Atom positions fractional
        if self._atomPositions_fractional is not None:
            text_str += f"Number of Fractional Atom Positions: {len(self._atomPositions_fractional)}\n"
        else:
            text_str += "Fractional Atom Positions: Not defined\n"

        # Atom count and types
        if hasattr(self, '_atomCount'):
            text_str += f"Total Number of Atoms: {self._atomCount}\n"
        if hasattr(self, '_uniqueAtomLabels'):
            text_str += f"Unique Atom Types: {', '.join(self._uniqueAtomLabels)}\n"

        # Atom Labels List
        if self._atomLabelsList is not None:
            extended_text_str += f"Number of Atom Labels: {len(self._atomLabelsList)}\n"
        else:
            extended_text_str += "Atom Labels List: Not defined\n"

        # Atomic Constraints
        if hasattr(self, '_atomicConstraints') and self._atomicConstraints is not None:
            extended_text_str += "Atomic Constraints: Defined\n"
        else:
            extended_text_str += "Atomic Constraints: Not defined\n"

        # Additional details based on verbosity
        if verbosity > 0:
            # Include more detailed information
            # e.g., reciprocal lattice vectors, distance matrix, etc.
            if hasattr(self, '_distance_matrix') and self._distance_matrix is not None:
                text_str += f"Distance Matrix: Available\n"
            else:
                text_str += "Distance Matrix: Not calculated\n"
            if hasattr(self, '_total_charge'):
                extended_text_str += "Total Charge: Available\n" if self._total_charge is not None else "Total Charge: Not defined\n"
            if hasattr(self, '_magnetization'):
                extended_text_str += "Magnetization: Available\n" if self._magnetization is not None else "Magnetization: Not defined\n"
            if hasattr(self, '_total_force'):
                extended_text_str += "Total Force: Available\n" if self._total_force is not None else "Total Force: Not defined\n"
            # Additional properties can be added here as needed

        return text_str