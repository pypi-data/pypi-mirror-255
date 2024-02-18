try:
    from sage_lib.partition.PartitionManager import PartitionManager
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing PartitionManager: {str(e)}\n")
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

try:
    from sage_lib.descriptor import MBTR
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing sage_lib.IO.descriptor.MBTR: {str(e)}\n")
    del sys

class CrystalDefect_builder(PartitionManager):
    def __init__(self, file_location:str=None, name:str=None, Periodic_Object:object=None, **kwargs):
        if Periodic_Object is not None:
            self.__dict__.update(Periodic_Object.__dict__)
        else:
            super().__init__(name=name, file_location=file_location)
        
        self._Vacancy = None 

    def handleVacancy(self, container, values, container_index, file_location=None):
        sub_directories, containers = [], []

        container_copy = self.copy_and_update_container(container, '/Vacancy', file_location)
        container_copy.AtomPositionManager = CrystalDefectGenerator(Periodic_Object=container_copy.AtomPositionManager)
        all_vacancy_configs, all_vacancy_label = container_copy.AtomPositionManager.generate_all_vacancies()

        for cv_i, (vacancy_configs, vacancy_label) in enumerate(zip(all_vacancy_configs, all_vacancy_label)):
            container_copy2 = copy.deepcopy(container_copy)
            container_copy2.AtomPositionManager = vacancy_configs
            container_copy2.file_location = f'{container_copy.file_location}/{cv_i}_{vacancy_label}'
            sub_directories.append(f'{cv_i}_{vacancy_label}')
            containers.append(container_copy2)
        
        self.generate_execution_script_for_each_container(sub_directories, container.file_location + '/Vacancy')
        return containers

    def handleDefect(self, container, values, container_index, file_location):

        for v in values:
            if v['defect'].upper() == 'SUBSTITUTION':
                self.generate_all_substitutional_impurity( container=container, species=v['species'], new_species=v['new_species'], weights=v['weights'] )

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
    
    def generate_one_substitutional_impurity(self, container, species:list, new_species:list):
        '''
        md = MBTR.MDTR(lattice_vectors=container.AtomPositionManager.latticeVectors, 
                    atomLabelsList=container.AtomPositionManager.atomLabelsList, 
                    atomPositions=container.AtomPositionManager.atomPositions, )

        rep, rep_div = md.get_mdtr()
        similarity_matrix = md.get_selfsimilarity_matrix( np.sum( np.abs( rep_div[0,:,:,:]), axis=2).T) 

        groups = md.find_related_atoms_groups(similarity_matrix, threshold=0.82)
        '''
        ans = []
        for i, ID in enumerate(container.AtomPositionManager.atomLabelsList):
            if ID in species:
                for ID2 in new_species:
                    container_copy = copy.deepcopy(container)
                    container_copy.AtomPositionManager.set_ID( atom_index=i, ID=ID2 )
                    ans.append(container_copy)

                    md = MBTR.MDTR(lattice_vectors=container_copy.AtomPositionManager.latticeVectors, 
                                atomLabelsList=container_copy.AtomPositionManager.atomLabelsList, 
                                atomPositions=container_copy.AtomPositionManager.atomPositions, )

                    rep, rep_div = md.get_mdtr()
                    #similarity_matrix = md.get_selfsimilarity_matrix( np.sum( np.abs( rep_div[0,:,:,:]), axis=2).T) 

                    #groups = md.find_related_atoms_groups(similarity_matrix, threshold=0.82)
                    print( i, rep.shape)
                    ans1.append( np.abs(rep[0,:]) )
                    plt.plot( np.abs(rep[0,:]) )
                    

        print( len(ans) )
        plt.show()
        asdfsfd

    def generate_all_substitutional_impurity(self, container, species:list, new_species:list, ):
        """

        """
        nes = self.generate_one_substitutional_impurity(container=container, species=species, new_species=new_species)

        '''
        md = MBTR.MDTR(lattice_vectors=self.containers[0].AtomPositionManager.latticeVectors, 
                    atomLabelsList=self.containers[0].AtomPositionManager.atomLabelsList, 
                    atomPositions=self.containers[0].AtomPositionManager.atomPositions, )

        rep, rep_div = md.get_mdtr()
        similarity_matrix = md.get_selfsimilarity_matrix( np.sum( np.abs( rep_div[0,:,:,:]), axis=2).T) 

        groups = md.find_related_atoms_groups(similarity_matrix, threshold=0.82)
        print(groups)
        print( self.containers[0].AtomPositionManager.atomPositions[4,:] )
        print( self.containers[0].AtomPositionManager.atomPositions[5,:] )
        print( self.containers[0].AtomPositionManager.atomPositions[10,:] )
        print(rep.shape , rep_div.shape) 
        print('dif', np.sum( (np.abs(rep_div[0,:,13,0].T) - np.abs(rep_div[0,:,17,0].T))**2 )**0.5 )
        print('dif', np.sum( (np.abs(rep_div[0,:,0,0].T) - np.abs(rep_div[0,:,1,0].T))**2 )**0.5 )
        print('dif', np.sum( (np.abs(rep_div[0,:,4,0].T) - np.abs(rep_div[0,:,5,0].T))**2 )**0.5 )
        print('dif', np.sum( (np.abs(rep_div[0,:,12,0].T) - np.abs(rep_div[0,:,13,0].T))**2 )**0.5 )
        mask = self.containers[0].AtomPositionManager.atomLabelsList == 'Ni'
                
        plt.plot( np.abs(rep_div[0,:,4,1].T) )
        plt.plot( np.abs(rep_div[0,:,5,1].T) )
        plt.plot( np.abs(rep_div[0,:,10,2].T) )
        #similarity_matrix[similarity_matrix>0.8] = 1
        #similarity_matrix[similarity_matrix<=0.8] = 0
        plt.matshow( similarity_matrix )

        plt.show()
        print(a.shape, b.shape)

        asdf
        '''
        '''
        # Parameters: 
        atomlabel = atomlabel if atomlabel is not None else self.uniqueAtomLabels
        new_atom_label = list(new_atom_label) if new_atom_label is list else new_atom_label
        # Determine the indices at which vacancies should be introduced
        if atomlabel:   indices = [i for i, label in enumerate(self.atomLabelsList) if label in atomlabel]
        else:           indices = np.array(range(self._atomCount), dtype=np.int64)
        print(indices)

        configurations = [ {'atom_index':i, 'new_atom_label':nal } for i in indices for nal in new_atom_label ]
        return self._generate_defect_configurations('introduce_substitutional_impurity', configurations)

        '''

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
