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

try:
    import random
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing random: {str(e)}\n")
    del sys

class Config_builder(PartitionManager):
    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        super().__init__(name=name, file_location=file_location)
        
    def handleKPoints(self, container:object, values:list, container_index:int,  file_location:str=None):
        """
        Handles the configuration for KPoints.

        This method creates container copies for each set of k-points values, updates the 
        subdivisions, and generates execution scripts for each container.

        Parameters:
        container (object): The container to be copied and updated.
        values (list): List of k-points values.
        container_index (int): Index of the container.
        file_location (str): File location for the container copy.

        Returns:
        list: A list of container copies with updated k-points configurations.
        """
        sub_directories, containers = [], []

        for v in values:
            # Copy and update container for each set of k-point values
            container_copy = self.copy_and_update_container(container, f'/KPOINTConvergence/{v[0]}_{v[1]}_{v[2]}', file_location)
            container_copy.KPointsManager.subdivisions = [v[0], v[1], v[2]]
            sub_directories.append(f'{v[0]}_{v[1]}_{v[2]}')
            containers.append(container_copy)

        # Generate execution script for each updated container
        self.generate_execution_script_for_each_container(sub_directories, container.file_location + '/KPOINTConvergence')
        return containers

    def handleInputFile(self, container:object, values:list, container_index:int, file_location:str=None):
        """
        Handles the configuration for input files.

        This method updates the parameters of the input file for each value in the provided list
        and generates execution scripts for each container.

        Parameters:
        container (object): The container to be copied and updated.
        values (list): List of parameter values for input file configuration.
        container_index (int): Index of the container.
        file_location (str): File location for the container copy.

        Returns:
        list: A list of container copies with updated input file configurations.
        """
        sub_directories, containers = [], []

        for v in values:
            # Copy and update container for each parameter value
            container_copy = self.copy_and_update_container(container, f'/{parameter}_analysis/{v}', file_location)
            container_copy.InputFileManager.parameters[parameter.upper()] = ' '.join(v) if v is list else v 
            sub_directories.append('_'.join(map(str, v)) if isinstance(v, list) else str(v))
            containers.append(container_copy)

        # Generate execution script for each updated container
        self.generate_execution_script_for_each_container(sub_directories, container.file_location + f'/{parameter}_analysis')
        return containers

    def handleAtomIDChange(self, container: object, values: dict, container_index: int, file_location: str = None):
        """
        Handles the configuration for changing atom IDs in a container.

        This method creates copies of the given container and updates the atom IDs based on the provided 'values' dictionary. 
        It is useful for simulations where different atom types need to be substituted and analyzed.

        Parameters:
        - container (object): The container whose atom IDs are to be modified. This container is not altered; instead, copies are made and modified.
        - values (dict): A dictionary specifying the parameters for atom ID change. It should have the following keys:
            - 'N' (int): The number of times the atom ID change should be applied, resulting in N different containers.
            - 'atom_ID' (list of str): List of current atom IDs to be changed. For example, ['H', 'O'].
            - 'new_atom_ID' (list of str): List of new atom IDs to replace the old ones. For example, ['He', 'N'].
            - 'new_atom_weights' (list of float): Weights corresponding to each new atom ID in 'new_atom_ID', 
            used to randomly select the new IDs with specified probabilities.
        - container_index (int): Index of the container, used for tracking or identification purposes.
        - file_location (str, optional): The file location where the container copy with updated atom IDs will be saved.

        Returns:
        - list: A list of container copies, each with updated atom IDs according to the 'values' specification.

        Each container copy is updated by replacing the specified 'atom_ID' with a new ID selected from 'new_atom_ID', 
        based on the weights provided in 'new_atom_weights'. This process is repeated 'N' times to generate multiple container copies.
        """
        sub_directories, containers = [], []

        for v in range(values['N']):
            # Create a copy of the container with a unique sub-directory name based on atom ID changes
            atom_ID, new_atom_ID = values['atom_ID'], values['new_atom_ID']
            container_copy = self.copy_and_update_container(container, f'/AtomIDChange_{v}', file_location)
    
            # Select atoms in the container that match the specified atom IDs to be changed
            selected_atomLabels = np.isin(container_copy.AtomPositionManager.atomLabelsList, atom_ID)
            # Choose new atom IDs based on the specified weights
            new_atomLabels = random.choices(new_atom_ID, values['weights'], k=np.sum(selected_atomLabels) )

            # Update the atom IDs in the container copy
            container_copy.AtomPositionManager.set_ID(atom_index=selected_atomLabels, ID=new_atomLabels)

            selected_atomLabels_None = np.where(container_copy.AtomPositionManager.atomLabelsList =='X')[0]
            
            container_copy.AtomPositionManager.remove_atom( atom_index=selected_atomLabels_None )

            sub_directories.append(f'/AtomIDChange_{v}')

            # Add the updated container to the list
            containers.append(container_copy)

        return containers


