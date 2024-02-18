# En __init__.py del paquete que contiene AtomPositionManager
try:
    from sage_lib.partition.PartitionManager import PartitionManager
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing PartitionManager: {str(e)}\n")
    del syss

try:
    from sage_lib.IO.structure_handling_tools.AtomPosition import AtomPosition
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing AtomPosition: {str(e)}\n")
    del sys
    
try:
    import numpy as np
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys

try:
    import copy
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing copy: {str(e)}\n")
    del sys

class MoleculeCluster_builder(PartitionManager):
    """
    MoleculeCluster_builder is a class for building molecular clusters, particularly useful in simulations involving molecular systems.

    This class extends the functionality of PartitionManager to provide specific methods for creating and managing clusters of molecules. It includes methods for calculating cluster volumes, determining the number of molecules for a given density, adding individual molecules or solvents, and handling complex molecular cluster setups.

    Attributes:
        _molecule_template (dict): A dictionary to store molecule templates.
        _density (float): Density of the cluster.
        _cluster_lattice_vectors (np.array): Lattice vectors defining the cluster's boundaries.

    Methods:
        get_cluster_volume(shape, cluster_lattice_vectors): Calculates the volume of the cluster.
        get_molecules_number_for_target_density(density, cluster_volume, molecules): Calculates the number of molecules needed for a target density.
        add_molecule_template(name, atoms): Adds a molecule template to the builder.
        add_molecule(container, molecule, shape, cluster_lattice_vectors, translation, distribution, tolerance, max_iteration): Adds a molecule to the cluster.
        add_solvent(container, shape, cluster_lattice_vectors, translation, distribution, molecules, density, max_iteration): Adds solvent molecules to the cluster.
        handleCLUSTER(container, values, container_index, file_location): Handles the creation of a molecular cluster within a specified container.

    Parameters:
        file_location (str, optional): The initial file location for the cluster data.
        name (str, optional): The initial name of the molecule cluster.

    Examples:
        # Create a MoleculeCluster_builder instance
        cluster_builder = MoleculeCluster_builder(name="WaterCluster", file_location="/path/to/cluster")

        # Add a molecule template
        cluster_builder.add_molecule_template(name="H2O", atoms=water_atoms)

        # Add molecules to the cluster
        cluster_builder.add_molecule(container, water_molecule, shape='box')
    """
    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        """
        Constructor method for initializing the MoleculeCluster_builder instance.
        """
        super().__init__(name=name, file_location=file_location)

        self._molecule_template = {}
        self._density = None
        self._cluster_lattice_vectors = None

    def get_cluster_volume(self, shape:str='box', cluster_lattice_vectors:np.array=None ):
        """
        Calculates the volume of the molecular cluster based on its shape and lattice vectors.

        Parameters:
            shape (str): The shape of the cluster, default is 'box'.
            cluster_lattice_vectors (np.array): The lattice vectors defining the cluster boundaries.

        Returns:
            float: The volume of the cluster in cubic angstroms.
        """
        cluster_lattice_vectors = cluster_lattice_vectors if cluster_lattice_vectors is not None else self.cluster_lattice_vectors 
        
        if shape.lower() == 'box':
            return np.abs(np.linalg.det(cluster_lattice_vectors)) * 10**-24
        else:
            print('Undefine shape')

        return volume

    def get_molecules_number_for_target_density(self, density:float=1.0, cluster_volume:float=None, molecules:dict={'H2O':1.0} ) -> dict:
        """
        Calculates the number of molecules needed to achieve a target density in the cluster.

        Parameters:
            density (float): The target density in g/cm^3.
            cluster_volume (float): The volume of the cluster in cubic angstroms.
            molecules (dict): A dictionary of molecule types and their fractional composition.

        Returns:
            dict: A dictionary with molecule names as keys and the number of molecules as values.
        """
        mass_suma = np.sum( [ self._molecule_template[m_name].mass * m_fraction for m_name, m_fraction in molecules.items()] ) 
        factor = density * self.NA * cluster_volume / mass_suma
        return { m_name: int(np.round(factor*m_fraction)) for m_name, m_fraction in molecules.items() }

    def add_molecule_template(self, name:str, atoms:object, ) -> bool:
        """
        Adds a molecule template to the builder.

        Parameters:
            name (str): The name of the molecule.
            atoms (object): The atom object representing the molecule.

        Returns:
            bool: True if the molecule template was added successfully.
        """
        self._molecule_template[name] = atoms
        return True

    def add_molecule(self, container, molecule, 
                        shape:str='box', cluster_lattice_vectors:np.array=np.array([[10, 0, 0], [0,10, 0], [0, 0, 10]]), translation:np.array=None, distribution:str='random', 
                        tolerance:float=1.6, max_iteration:int=2000):
        """
        Adds a single molecule to the cluster.

        Parameters:
            container: The container to which the molecule is added.
            molecule: The molecule to be added.
            shape (str): The shape of the cluster.
            cluster_lattice_vectors (np.array): The lattice vectors of the cluster.
            translation (np.array): The translation vector for placing the molecule.
            distribution (str): The distribution method for placing the molecule.
            tolerance (float): The minimum allowable distance between molecules.
            max_iteration (int): The maximum number of iterations for placing the molecule.

        Returns:
            bool: True if the molecule was added successfully, False otherwise.
        """
        translation = translation if translation is not None else np.array([0,0,0], dtype=np.float64)
        iteration = 0

        molecule_copy = copy.deepcopy(molecule) 
        while True:
            if shape.lower() == 'box':
                if distribution.lower() == 'random':
                    displacement = translation + molecule_copy.generate_uniform_translation_from_fractional(latticeVectors=cluster_lattice_vectors )
            atomPositions = np.dot(molecule.atomPositions, molecule.generate_random_rotation_matrix().T) + displacement
            molecule_copy.set_atomPositions(new_atomPositions=atomPositions) 
            molecule_copy.latticeVectors = container.AtomPositionManager.latticeVectors
        
            if np.sum( container.AtomPositionManager.count_neighbors( molecule_copy, r=tolerance) ) == 0:   
                container.AtomPositionManager.add_atom( atomLabels=molecule_copy.atomLabelsList, atomPosition=molecule_copy.atomPositions, atomicConstraints=molecule_copy.atomicConstraints )
                return True
            else:
                iteration += 1

            if iteration > max_iteration:
                print('Can not set cluster, try lower density')
                return False

    def add_solvent(self, container, 
                        shape:str='box', cluster_lattice_vectors:np.array=np.array([[10, 0, 0], [0,10, 0], [0, 0, 10]]), translation:np.array=np.array([0,0,0]), distribution:str='random', tolerance:float=1.6, 
                        molecules:dict={'H2O':1.0}, density:float=1.0, max_iteration:int=2000, verbosity:bool=True):
        """
        Adds solvent molecules to the cluster.

        Parameters:
            container: The container to which the solvent is added.
            shape (str): The shape of the cluster.
            cluster_lattice_vectors (np.array): The lattice vectors of the cluster.
            translation (np.array): The translation vector for placing the solvent molecules.
            distribution (str): The distribution method for placing the solvent molecules.
            molecules (dict): The solvent molecules and their proportions.
            density (float): The target density for the solvent.
            max_iteration (int): The maximum number of iterations for placing the solvent molecules.

        Returns:
            None
        """
        cluster_volume = self.get_cluster_volume(shape=shape, cluster_lattice_vectors=cluster_lattice_vectors)
        molecules_number = self.get_molecules_number_for_target_density(density=density, cluster_volume=cluster_volume, molecules=molecules)

        for molecule_name, molecule_number in molecules_number.items():
            for mn in range(molecule_number):
                if verbosity: print(f'adding solvent: {int(mn/molecule_number*100)} %')
                if not self.add_molecule( container=container, molecule=self.molecule_template[molecule_name], translation=translation, tolerance=tolerance,
                                        shape=shape, cluster_lattice_vectors=cluster_lattice_vectors, distribution=distribution, max_iteration=max_iteration ):
                    print('Can not set cluster, try lower density. ')
                    break
        
    def handleCLUSTER(self, container:object, values:list, container_index:int,  file_location:str=None):
        """
        Handles the creation and management of a molecular cluster within a specified container.

        Parameters:
            container (object): The container in which the cluster is built.
            values (list): A list of parameters defining the cluster properties.
            container_index (int): The index of the container.
            file_location (str, optional): The file location for storing cluster data.

        Returns:
            list: A list of containers with the created clusters.
        """
        sub_directories, containers = [], []
 
        for v in values:
            # Copy and update container for each set of k-point values
            container_copy = self.copy_and_update_container(container, f'/solvent/', file_location)
            
            for s in v['solvent']:
                molecule = AtomPosition()
                molecule.build(s)
                self.add_molecule_template(s, molecule)
            
            if v['slab']:
                vacuum_box, vacuum_start = container_copy.AtomPositionManager.get_vacuum_box(tolerance=v['vacuum_tolerance']) 
                shape = 'box'
                distribution = 'random'
            else:
                vacuum_box, vacuum_start = v['size'], v['translation']
                shape = v['shape']
                distribution = v['distribution']

            tolerance = v['colition_tolerance']
            density = v['density']

            self.add_solvent(container=container_copy, shape=shape, cluster_lattice_vectors=vacuum_box, 
                        translation=vacuum_start, distribution=distribution, density=density, tolerance=tolerance)

            if v['wrap']:
                container_copy.AtomPositionManager.pack_to_unit_cell()

            concatenate_solvent = '-'.join(v['solvent'])
            sub_directories.append(f'{density}_{concatenate_solvent}')
            containers.append(container_copy)

        # Generate execution script for each updated container
        #self.generate_execution_script_for_each_container(sub_directories, container.file_location + '/solvent')
        return containers

