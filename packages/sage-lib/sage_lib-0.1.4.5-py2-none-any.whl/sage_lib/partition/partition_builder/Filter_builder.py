try:
    from sage_lib.partition.PartitionManager import PartitionManager
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing PartitionManager: {str(e)}\n")
    del sys

try:
    import numpy as np
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys

class Filter_builder(PartitionManager):
    """
    A class for building filters related to simulations or theoretical calculations.

    This class extends PartitionManager and provides methods to filter containers
    based on various criteria.

    Inherits:
    All attributes and methods from PartitionManager.
    """
    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        """
        Initialize the Filter_builder with file location and name.

        Parameters:
        - file_location (str): Location of the file.
        - name (str): Name of the configuration.
        - **kwargs: Additional keyword arguments for the parent class.
        """
        super().__init__(name=name, file_location=file_location)
        


    def filter_conteiners(self, filter_class:str, filter_type:str=None, container_property:str=None, 
                value:float=None, selection_number:int=None, ID:str=None,
                temperature:float=None, traj:bool=False, verbosity:bool=False) -> bool:
        """
        Filters containers based on a specified criterion.

        Parameters:
        - filter_class (str): The class to filter by (e.g., 'fmax').
        - filter_type (str, optional): Type of filter (e.g., 'max', 'min').
        - container_property (str, optional): The property to filter by.
        - value (float, optional): The value to compare against.
        - selection_number (int, optional): The number of selections to make.
        - ID (str, optional): The identifier for filtering.
        - temperature (float, optional): The temperature for Boltzmann biasing in flat histogram selection.
        - traj (bool, optional): If True, applies trajectory-based filtering.
        - verbosity (bool, optional): If True, enables verbose output.

        Returns:
        - bool: True if filtering was successful.
        """
        # Generate a mask based on the specified filter criteria
        mask = self.get_mask(filter_class=filter_class, filter_type=filter_type, container_property=container_property, 
            value=value, selection_number=selection_number, ID=ID,
            temperature=temperature, traj=traj, verbosity=verbosity)

        # Apply the generated mask to filter containers
        if verbosity: print( f'Filter :: Class {filter_class} - Type {filter_type}: {len(self.containers)} >> {np.sum(mask)}')
        self.apply_filter_mask(mask)

        return True 

    def get_mask(self, filter_class:str, filter_type:str=None, container_property:str=None, 
                value:float=None, selection_number:int=None, ID:str=None,
                temperature:int=None, traj:bool=False, verbosity:bool=False) -> list:
        """
        Generates a mask based on specified filtering criteria.

        The function supports various filtering methods, including random selection, 
        flat histogram selection, and property-based filtering.

        Parameters:
        - filter_class (str): The class of filter to apply.
        - filter_type (str, optional): The type of filter within the class.
        - container_property (str, optional): The property of the container to use in filtering.
        - value (float, optional): A value used in comparisons for filtering.
        - selection_number (int, optional): The number of selections to make (used in random selection).
        - ID (str, optional): Identifier used in property-based filtering.
        - temperature (float, optional): Temperature for Boltzmann biasing (used in flat histogram selection).
        - traj (bool, optional): If True, apply trajectory-based filtering.
        - verbosity (bool, optional): If True, enables verbose output.

        Returns:
        - list: A mask indicating the selected containers.
        """
        # Initialize a default mask to avoid errors
        mask = np.ones_like(self.containers) # to avoid errors 

        # Apply different filtering techniques based on filter_class
        if filter_class.upper() == 'INDEX':
            mask = self.filter_by_index( filter_type=filter_type, selection_number=selection_number)

        if filter_class.upper() == 'RANDOM':
            mask = self.random_selection( value=value, filter_type=filter_type, selection_number=selection_number)

        if filter_class.upper() == 'FLAT_HISTOGRAM':
            mask = self.flat_histogram_selection( temperature=temperature, container_property=container_property, selection_number=selection_number )

        if filter_class.upper() == 'BINARY':
            mask = self.filter_by_property( container_property=container_property, filter_type=filter_type, value=value, ID=ID, verbosity=verbosity)
        
        if traj:
            first_zero_index = np.where(mask == 0)[0]
            if first_zero_index.size > 0:
                mask[first_zero_index[0]:] = 0

        return np.array(mask, dtype=np.int64)

    def filter_by_index(self, filter_type:str, selection_number:float=None, verbosity:bool=False):
        """
        Generate a boolean mask based on a specified filtering criterion and selection number.

        This method supports filtering by the minimum (`min`), maximum (`max`), and an equipartition
        method that selects indices based on a linear spacing across the range of the container.

        Parameters:
        - filter_type (str): Type of filter to apply. Valid options are 'min', 'max', and 'equipartition'.
        - selection_number (float, optional): The number of elements to select for the filter. This parameter's
          interpretation depends on the filter_type:
          - For 'min', it represents the number of elements from the end.
          - For 'max', it represents the number of elements from the start.
          - For 'equipartition', it represents the total number of elements to be evenly selected across the range.
        - verbosity (bool, optional): If True, additional information will be printed. (Currently not implemented)

        Returns:
        - np.ndarray: A boolean mask array where True indicates that the index has been selected based on the
          specified filtering criteria.

        Example:
        >>> container_length = 10  # Assume a hypothetical container length
        >>> self.containers = np.arange(container_length)  # Example container setup
        >>> mask = filter_by_index('max', 5)
        >>> print(mask)
        [True True True True True False False False False False]

        Note:
        - The function assumes that `self.containers` is an iterable with a definable length.
        - `selection_number` must be a positive integer less than or equal to the length of `self.containers`
          for 'min' and 'max' filter types. For 'equipartition', it should be able to divide the range into
          nearly equal parts.
        """
        
        # Initialize mask
        mask = None

        # Generate mask for filtering the last `selection_number` elements
        if filter_type == 'min':
            mask = np.arange(len(self.containers)) >= len(self.containers) - selection_number

        # Generate mask for filtering the first `selection_number` elements
        elif filter_type == 'max':
            mask = np.arange(len(self.containers)) < selection_number

        # Generate mask for selecting `selection_number` evenly spaced elements
        elif filter_type == 'equipartition':
            mask = np.isin(np.arange(len(self.containers)), np.round(np.linspace(0, len(self.containers) - 1, int(selection_number))).astype(int))
        
        return mask

    def filter_by_property(self, container_property:str, filter_type:str, value:float=None, ID:str=None, verbosity:bool=False):
        """
        Filters the containers based on a specified property and a filter criterion.

        Args:
            container_property (str): The property to filter by ('E' for energy, 'FORCES' for forces).
            filter_type (str): Type of filter ('max' or 'min').
            value (float): The threshold value for filtering.
            verbosity (bool): If True, enables verbose output.

        Returns:
            list: A mask indicating the containers that meet the filter criteria.
        """
        # Define the comparison function based on filter_type
        compare = {'max': lambda x: x <= value, 'min': lambda x: x >= value}[filter_type]

        # Create the filter mask
        if container_property.upper() == 'FORCES':
            # Calculate the magnitude of the total force for each container
            forces_magnitude = [np.linalg.norm(c.AtomPositionManager.total_force) for c in self.containers]
            mask = np.array([compare(force) for force in forces_magnitude], dtype=int)

        elif container_property.upper() == 'E':
            # Calculate the magnitude of the total force for each container
            energies = [ c.AtomPositionManager.E for c in self.containers ]
            mask = np.array([compare(energy) for energy in energies], dtype=int)

        elif container_property.upper() == 'HAS_ID':
            # 
            ID_amount = [ c.AtomPositionManager.atom_ID_amount(ID) for c in self.containers ]
            mask = np.array([ compare(ida) for ida in ID_amount], dtype=int)

        return mask

    def random_selection(self, selection_number:int=None, filter_type:str='tail', value:float=5):
        """
        Generates a selection mask for a list, where the probability of selection
        is higher for elements towards the end of the list with an exponential decay
        towards the start.

        This method is useful when there's a need to preferentially select items 
        from the latter part of a list, with decreasing likelihood towards the beginning.

        Args:
            selection_number (int, optional): Number of elements to select. Defaults to 1 if not specified or if the provided value is not an integer.

        Returns:
            list: A boolean mask where selected elements are marked True, and others False.
        """

        n = self.N  # Number of elements in the list or collection
            
        # Ensure that the 'selection_number' is an integer; default to 1 if not
        selection_number = selection_number if isinstance(selection_number, int) else min(selection_number, n)

        if filter_type.upper() == 'TAIL':
            # Generate exponentially decaying weights for selection probability
            weights = np.exp(np.linspace(0, value, n))  # Adjust the exponent range (0 to 5 here) to control decay rate
            weights /= np.sum(weights) # Normalize weights to sum to 1

        elif filter_type.upper() == 'UNIFORM':
            weights = np.ones(n)

        # Select 'selection_number' unique indices based on the weights
        #selected_indices = random.choices(range(n), weights=weights, k=selection_number)
        selected_indices = np.random.choice(range(n), p=weights/np.sum(weights), size=int(selection_number), replace=False)

        # Create a selection mask with True for selected indices
        mask = [i in selected_indices for i in range(n)]

        return mask


    def flat_histogram_selection(self, temperature=1.0, container_property:str='E', selection_number:int=None):
        """
        Selects 'm' configurations based on a Boltzmann-biased flat histogram of a given quantity,
        such as per-atom enthalpy.

        The selection probability is inversely proportional to the density of the histogram bin
        and multiplied by a Boltzmann biasing factor. This factor is exponential in the quantity
        relative to its lowest value, divided by a 'temperature'.

        Args:
            temperature (float): The 'temperature' used for the Boltzmann biasing factor, in the
            same units as the quantity.
            container_property (str): Type of selection to be made ('energy' or 'forces').
            m (int, optional): Number of configurations to select. If None, selects all configurations.

        Returns:
            list: A boolean mask where selected elements are marked True, and others False.
        """
        # Extract quantity for each configuration based on container_property
        S = [getattr(c.AtomPositionManager, container_property) for c in self.containers]

        # Construct a histogram of the selected quantity
        histogram, bin_edges = np.histogram(S, bins='auto', density=True)

        # Calculate the inverse density for each quantity value
        inverse_density = np.interp(S, bin_edges[:-1], 1 / histogram)

        # Calculate Boltzmann biasing factors
        S_min = min(S)
        boltzmann_factors = np.exp(-(np.array(S) - S_min) / temperature)

        # Calculate selection probability for each configuration
        selection_probabilities = inverse_density * boltzmann_factors
        selection_probabilities /= np.sum(selection_probabilities)

        # Determine number of selections
        selection_number = selection_number if isinstance(selection_number, int) else min(selection_number, len(S))

        # Select 'selection_number' indices based on probabilities
        selected_indices = set(random.choices(range(len(S)), weights=selection_probabilities, k=selection_number))

        # Create a selection mask
        mask = [i in selected_indices for i in range(len(S))]

        return mask

