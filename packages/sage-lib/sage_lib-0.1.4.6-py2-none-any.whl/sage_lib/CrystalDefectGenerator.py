# En __init__.py del paquete que contiene AtomPositionManager
try:
    from sage_lib.PeriodicSystem import PeriodicSystem
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing PeriodicSystem: {str(e)}\n")
    del sys

try:
    from scipy.spatial import Voronoi
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing scipy.spatial.Voronoi: {str(e)}\n")
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

class CrystalDefectGenerator(PeriodicSystem):
    def __init__(self, file_location:str=None, name:str=None, Periodic_Object:object=None, **kwargs):
        if Periodic_Object is not None:
            self.__dict__.update(Periodic_Object.__dict__)
        else:
            super().__init__(name=name, file_location=file_location)
        
        self._Vacancy = None 

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

    # ------------------------------------------------------------------------------------#
    def _generate_defect_configurations(self, defect_introducer, configurations:list=None):
        """
        General method to generate defect configurations.

        Parameters:
        - defect_introducer (function): Function that introduces the specific defect.
        - positions (list or None): Positions to introduce defects.
        - labels (list or None): Labels of atoms to introduce defects.

        Returns:
        - tuple: Two lists containing defect configurations and corresponding labels.
        """
        all_configs = []
        all_labels = []

        for config in configurations:
            temp_manager = copy.deepcopy(self)
            method = getattr(temp_manager, defect_introducer, None)

            if callable(method):
                method(**config)
            else:
                print(f"ERROR '{defect_introducer}' does not exist.")

            if not self._is_redundant(all_configs, temp_manager):
                all_configs.append(temp_manager)
                all_labels.append( '_'.join([str(c) for c in config.values()]) )

        return all_configs, all_labels

    def _is_redundant(self, configurations, new_config):
        """
        Checks if the new configuration is redundant within the existing configurations.

        Parameters:
        - configurations (list): List of existing configurations.
        - new_config (object): New configuration to check.

        Returns:
        - bool: True if redundant, False otherwise.
        """
        return any(np.array_equal(config.atomPositions, new_config.atomPositions) for config in configurations)

    # ------------------------------------------------------------------------------------#
    def generate_all_vacancies(self, atomlabel=None):
        """
        Generate all possible vacancy configurations for the system.

        Parameters:
        - atomlabel (list or None): Specifies the type of atom for which vacancies should be generated.

        Returns:
        - tuple: Two lists containing vacancy configurations and corresponding labels.
        """
        # Parameters:
        atomlabel = list(atomlabel) if atomlabel is str else atomlabel

        # Determine the indices at which vacancies should be introduced
        if atomlabel:   indices = [i for i, label in enumerate(self.atomLabelsList) if label in atomlabel]
        else:           indices = np.array(range(self._atomCount), dtype=np.int64)

        configurations = [ {'atom_index':i} for i in indices  ]
        return self._generate_defect_configurations('introduce_vacancy', configurations)
    
    def generate_all_interstitial(self, atomlabel:list, new_atom_position:np.array=None):
        """

        """
        # Parameters: 
        new_atom_position = new_atom_position if new_atom_position is not None else self._find_volumes_center()
        new_atom_position = [nap for nap in new_atom_position if self.is_point_inside_unit_cell(nap) ] 

        # Determine the indices at which vacancies should be introduced
        if atomlabel:   indices = [i for i, label in enumerate(self.atomLabelsList) if label in atomlabel]
        else:           indices = np.array(range(self._atomCount), dtype=np.int64)

        configurations = [ {'new_atom_label':al, 'new_atom_position':nap } for al in atomlabel for nap in new_atom_position ]
        return self._generate_defect_configurations('introduce_interstitial', configurations)
    
    def generate_all_self_interstitial(self, atomlabel:list, new_atom_position:np.array=None):
        """

        """
        return self.generate_all_interstitial(atomlabel=self.uniqueAtomLabels, new_atom_position=None)
    
    def generate_all_substitutional_impurity(self, new_atom_label:list, atomlabel:list=None):
        """

        """
        # Parameters: 
        atomlabel = atomlabel if atomlabel is not None else self.uniqueAtomLabels
        new_atom_label = list(new_atom_label) if new_atom_label is list else new_atom_label
        # Determine the indices at which vacancies should be introduced
        if atomlabel:   indices = [i for i, label in enumerate(self.atomLabelsList) if label in atomlabel]
        else:           indices = np.array(range(self._atomCount), dtype=np.int64)
        print(indices)

        configurations = [ {'atom_index':i, 'new_atom_label':nal } for i in indices for nal in new_atom_label ]
        return self._generate_defect_configurations('introduce_substitutional_impurity', configurations)

    def _find_volumes_center(self, atomPositions:np.array=None):
        """
        Finds potential volumes for new atoms in a structure.

        Args:
            atom_coordinates (list of list of floats): List of existing atom coordinates.

        Returns:
            list of Voronoi region vertices: List of vertices of the Voronoi regions.
        """
        # Convert coordinates to a NumPy array.
        atomPositions = atomPositions if atomPositions is not None else self.atomPositions

        # Calculate the Voronoi decomposition.
        vor = Voronoi(atomPositions)

        return vor.vertices


'''
path = '/home/akaris/Documents/code/Physics/VASP/v6.1/files/dataset/CoFeNiOOH_jingzhu/surf_CoFe_2H_4OH/vacancy'
ap = CrystalDefectGenerator(file_location=path+'/POSCAR')
ap.readPOSCAR()
all_configs, all_labels = ap.generate_all_substitutional_impurity( 'V') # generate_all_vacancies generate_all_substitutional_impurity generate_all_interstitial


for a, b in zip(all_configs, all_labels):
    print(a.atomCountByType, b)
sadfsafd



path = '/home/akaris/Documents/code/Physics/VASP/v6.1/files/POSCAR/Cristals/NiOOH/*OH surface for pure NiOOH'
ap = CrystalDefectGenerator(file_location=path+'/SUPERCELL')
ap.readSIFile()
ap.is_surface = True
print( ap.latticeType )
#ap.introduce_vacancy(atom_index=10)
res,_ = ap.generate_all_vacancies()

ap.exportAsPOSCAR(path+'/POSCAR_d1')
for i, n in enumerate(res):
    n.exportAsPOSCAR(path+f'/POSCAR_d{i}')
'''
