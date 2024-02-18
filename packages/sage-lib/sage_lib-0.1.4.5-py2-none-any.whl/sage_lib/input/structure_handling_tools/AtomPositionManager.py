try:
    from sage_lib.input.structure_handling_tools.AtomPositionLoader import AtomPositionLoader
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing sage_lib.Input.structure_handling_tools.AtomPositionLoader: {str(e)}\n")
    del sys

try:
    from sage_lib.input.structure_handling_tools.AtomPositionOperator import AtomPositionOperator
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing sage_lib.Input.structure_handling_tools.AtomPositionOperator: {str(e)}\n")
    del sys

try:
    from sage_lib.input.structure_handling_tools.AtomPositionMaker import AtomPositionMaker
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing sage_lib.Input.structure_handling_tools.AtomPositionMaker: {str(e)}\n")
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

class AtomPositionManager(AtomPositionOperator, AtomPositionLoader, AtomPositionMaker):
    """
    Manages atomic position information, integrating functionalities from AtomPositionOperator and AtomPositionLoader.

    This class is responsible for handling and manipulating atomic positions and related properties
    for a given set of atoms. It allows for loading, processing, and analyzing atomic position data
    from various sources.
    """

    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        """
        Initializes the AtomPositionManager instance.

        Args:
            file_location (str, optional): Location of the file containing atomic data.
            name (str, optional): Name identifier for the atomic data.
            kwargs: Additional keyword arguments.
        """

        # Initialize base classes with provided arguments
        AtomPositionOperator.__init__(self, name=name, file_location=file_location)
        AtomPositionLoader.__init__(self, name=name, file_location=file_location)
        AtomPositionMaker.__init__(self, name=name, file_location=file_location)


        # Attributes initialization with descriptions
        self._comment = None  # Placeholder for comments. Type: str or None. Example: "Sample comment about the atomic structure"
        '''
        self._comment:

        Description: A placeholder for any comments associated with the atomic data.
        Type: str or None
        Example: "Sample comment about the atomic structure"
        Size: Variable length string.
        Additional Information: Used to store descriptive or explanatory text related to the atomic data.
        self._atomCount:
        '''
        self._atomCount = None  # Total number of atoms. Type: int or None. Example: 100
        '''
        Description: The total number of atoms in the structure.
        Type: int or None
        Example: 100 (indicating 100 atoms)
        Size: Single integer value.
        Additional Information: Represents the count of all atoms regardless of their type.
        self._scaleFactor:
        '''
        self._scaleFactor = None  # Scale factor for atomic positions. Type: float, int, list, np.array, or None. Example: 1.0 or [1.0, 1.0, 1.0]
        '''
        Description: A scale factor applied to the atomic positions.
        Type: float, int, list, np.array, or None
        Example: 1.0 or [1.0, 1.0, 1.0]
        Size: Single value or an array of up to three elements.
        Additional Information: Used in scaling the atomic positions, often for unit conversion or normalization.
        self._uniqueAtomLabels:
        '''
        self._uniqueAtomLabels = None  # Unique labels of atom types. Type: list of str or None. Example: ["Fe", "N", "C", "H"]
        '''
        Description: A list of unique labels representing different types of atoms.
        Type: list of str or None
        Example: ["Fe", "N", "C", "H"]
        Size: Number of unique atom types.
        Additional Information: Useful for identifying the distinct elements or molecules in the structure.
        self._atomCountByType:
        '''
        self._atomCountByType = None  # Count of atoms for each type. Type: list of int or None. Example: [4, 10, 6, 2]
        '''
        Description: A list indicating the count of atoms for each unique type.
        Type: list of int or None
        Example: [4, 10, 6, 2] corresponding to ["Fe", "N", "C", "H"]
        Size: Same as the number of unique atom types.
        Additional Information: Provides a count of each atom type, useful for composition analysis.
        self._selectiveDynamics:
        '''
        self._selectiveDynamics = None  # Indicates if selective dynamics are used. Type: bool or None. Example: True
        '''
        Description: A boolean indicating if selective dynamics are used (allowing certain atoms to move while others are fixed).
        Type: bool or None
        Example: True (indicating selective dynamics are used)
        Size: Single boolean value.
        Additional Information: Relevant in simulations where only a subset of atoms are allowed to participate in dynamics.
        self._atomPositions:
        '''
        self._atomPositions = None  # Array of atomic positions. Type: np.array(N, 3) or None. Example: np.array([[0, 0, 0], [1.5, 1.5, 1.5]])
        '''
        Description: A NumPy array containing the positions of each atom.
        Type: np.array with shape (N, 3) or None
        Example: np.array([[0, 0, 0], [1.5, 1.5, 1.5]]) for two atoms
        Size: N rows and 3 columns, where N is the number of atoms.
        Additional Information: The positions are typically in Cartesian coordinates (x, y, z).
        self._atomicConstraints:
        '''
        self._atomicConstraints = None # Atomic constraints. Type: np.array(N, 3) or None. Example: np.array([[1, 1, 1], [0, 1, 0]])
        '''
        Description: An array indicating constraints applied to each atom, often used in simulations to control atomic movement.
        Type: np.array with shape (N, 3) or None
        Example: np.array([[1, 1, 1], [0, 1, 0]]) (1s and 0s indicate constrained and unconstrained directions respectively)
        Size: N rows and 3 columns, mirroring the size of _atomPositions.
        Additional Information: Constraints are useful in simulations where certain atomic motions are restricted.
        self._atomLabelsList:
        '''
        
        self._atomLabelsList = None  # List of atom labels for all atoms. Type: list of str or None. Example: ["Fe", "N", "N", "N", "N", "C", "C", "C", "C", "H"]
        '''
        Description: A list of labels for all atoms, in the order they appear.
        Type: list of str or None
        Example: ["Fe", "N",  "N", "N", "N", "N", "C", "C", "C"] (for a structure with these atoms in sequence)
        Size: Length equal to the total number of atoms.
        Additional Information: Provides a straightforward way to identify each atom's type.
        self._fullAtomLabelString:
        '''
        self._fullAtomLabelString = None  # Concatenated string of all atom labels. Type: str or None. Example: "FeFeFeNNNNNNNCCCCCCCCCCCCCCCHHHHHHHHHHHHHHHH"
        self._atomPositions_tolerance = 1e-2  # Tolerance for position comparison. Type: float
        self._distance_matrix = None  # Distance matrix between atoms. Type: np.array or None
        
        # Properties related to atomic calculations
        self._total_charge = None  # Total charge. Type: float or None
        self._magnetization = None  # Magnetization. Type: float or None
        self._total_force = None  # Total force. Type: np.array or None
        self._E = None  # Total energy. Type: float or None
        self._Edisp = None  # Dispersion energy. Type: float or None
        self._IRdisplacement = None  # IR displacement. Type: np.array or None

        self._mass = None # 
        self._mass_list = None # 

    @property
    def distance_matrix(self):
        """
        Calculates and returns the distance matrix between atoms.

        The distance matrix is calculated using Euclidean distances. It is computed only if not already available.

        Returns:
            np.array: A matrix of distances between each pair of atoms.
        """
        if self._distance_matrix is not None:
            return self._distance_matrix
        elif self.atomPositions is not None:
            from scipy.spatial.distance import cdist 
            self._distance_matrix = cdist(self._atomPositions, self._atomPositions, 'euclidean')
            return self._distance_matrix
        elif'_atomPositions' not in self.__dict__:
            raise AttributeError("Attribute atomPositions must be initialized before accessing atomLabelsList.")
        else:
            return None


    @property
    def scaleFactor(self):
        """
        Ensures the scale factor is returned as a numpy array.

        If the scale factor is not set, it initializes it to a default value.

        Returns:
            np.array: The scale factor as a numpy array.
        """
        # Convert and return scaleFactor to numpy array
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
        """
        Returns the total count of atoms.

        If the atom count has not been directly set, it is inferred from the shape of `_atomPositions` 
        or the length of `_atomLabelsList`. This property ensures that the atom count is always synchronized 
        with the underlying atomic data.

        Returns:
            int: The total number of atoms.
        """
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
            return 0

    @property
    def uniqueAtomLabels(self):
        """
        Provides a list of unique atom labels.

        If not set, it is derived from `_atomLabelsList` by identifying the unique labels. This property is 
        useful for identifying the different types of atoms present in the structure.

        Returns:
            np.array: Array of unique atom labels.
        """
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
        """
        Returns the count of atoms for each unique atom type.

        If not set, it calculates the count based on `_atomLabelsList`. This property is useful for 
        quantitative analysis of the composition of the atomic structure.

        Returns:
            np.array: Array of atom counts for each type.
        """
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
        """
        Constructs and returns a list of all atom labels.

        If not set, it is derived from `_atomCountByType` and `_uniqueAtomLabels`. This property provides a 
        comprehensive list of labels for each atom in the structure.

        Returns:
            np.array: Array of atom labels.
        """
        if '_atomCountByType' not in self.__dict__ or '_uniqueAtomLabels' not in self.__dict__:
            raise AttributeError("Attributes _atomCountByType and _uniqueAtomLabels must be initialized before accessing atomLabelsList.")
        elif self._atomLabelsList is None and not self._atomCountByType is None and not self._uniqueAtomLabels is None: 
            self._atomLabelsList = np.array([label for count, label in zip(self._atomCountByType, self._uniqueAtomLabels) for _ in range(count)])
            return self._atomLabelsList
        else:
            return  self._atomLabelsList 

    @property
    def fullAtomLabelString(self):
        """
        Returns a concatenated string of all atom labels.

        If not set, it is constructed from `_atomCountByType` and `_uniqueAtomLabels`. This property provides 
        a quick textual representation of the entire atomic composition.

        Returns:
            str: Concatenated string of all atom labels.
        """
        if '_atomCountByType' not in self.__dict__ or '_uniqueAtomLabels' not in self.__dict__:
            raise AttributeError("Attributes _atomCountByType and _uniqueAtomLabels must be initialized before accessing fullAtomLabelString.")
        elif self._fullAtomLabelString is None and not self._atomCountByType is None and not self._uniqueAtomLabels is None: 
            self._fullAtomLabelString = ''.join([label*count for count, label in zip(self._atomCountByType, self._uniqueAtomLabels)])
            return self._fullAtomLabelString
        else:
            return  self._fullAtomLabelString 

    @property
    def atomPositions(self):
        """
        Provides the positions of atoms.

        If the positions are set as a list, they are converted to a NumPy array for consistency. If not set, 
        an empty array is returned.

        Returns:
            np.array: Array of atom positions.
        """
        if self._atomPositions is list:
            return np.array(self._atomPositions)
        elif self._atomPositions is None:
            return np.array([]).reshape(0, 3) 
        else:
            return self._atomPositions

    @property
    def atomicConstraints(self):
        """
        Returns the constraints applied to atoms.

        If not set, and if atom positions are available, it initializes the constraints as an array of ones 
        (indicating no constraints). Otherwise, it returns the set constraints.

        Returns:
            np.array: Array of atomic constraints.
        """
        if self._atomicConstraints is list:
            return np.array(self._atomicConstraints)
        elif self._atomPositions is not None:
            self._atomicConstraints = np.ones_like(self._atomPositions) 
            return self._atomicConstraints
        else:
            return self._atomicConstraints

    @property
    def mass_list(self):
        """

        """
        if self._mass_list is list:
            return np.array(self._mass_list)
        else:
            self._mass_list = np.array([ float(self.atomic_mass[atom_label]) for atom_label in self.atomLabelsList], np.float64)
            return self._mass_list

    @property
    def mass(self):
        """

        """
        if self._mass is float:
            return self._mass
        else:
            self._mass = np.sum(self.mass_list)
            return self._mass

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
