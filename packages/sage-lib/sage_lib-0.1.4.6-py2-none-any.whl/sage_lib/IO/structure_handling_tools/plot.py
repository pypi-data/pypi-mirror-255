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
    sys.stderr.write(f"An error occurred while importing scipy.spatial.distance.cdist: {str(e)}\n")
    del sys

try:
    import matplotlib.pyplot as plt
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing matplotlib.pyplot: {str(e)}\n")
    del sys

class plot:
    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        super().__init__(name=name, file_location=file_location)
        self._comment = None
        self._atomCount = None 
        self._RBF = None

    def get_RBF_cdist(self, periodic_image:int=0, cutoff:float=6.0, number_of_bins:int=100, 
                bin_volume_normalize:bool=True, number_of_atoms_normalize:bool=True, density_normalize:bool=True, ):

        number_of_bins = int(number_of_bins)

        # Process each frame in the trajectory
        cell = self.latticeVectors
        positions = self.atomPositions

        # Crear imágenes en las fronteras (ejemplo simple para una imagen en cada dirección)
        if periodic_image == 0:
            periodic_image = cutoff/np.max( np.linalg.norm(self.latticeVectors,axis=0) )
        periodic_image = int( np.round(periodic_image) )

        images = positions.copy()
        for i in range(-periodic_image, periodic_image+1):
            for j in range(-periodic_image, periodic_image+1):
                for k in range(-periodic_image, periodic_image+1):
                    if (i, j, k) != (0, 0, 0):
                        offset = np.dot( [i, j, k], cell )
                        images = np.vstack([images, positions + offset])

        distance_matrix = cdist(positions, images, 'euclidean')

        label_list_unit_cell = self.atomLabelsList
        label_list_expand_cell = np.tile(self.atomLabelsList, (periodic_image*2+1)**3)

        distance_matrix_dict = {a_label:{b_label:[] for b_index, b_label in enumerate(self.uniqueAtomLabels) if a_index >= b_index } for a_index, a_label in enumerate(self.uniqueAtomLabels) }

        uniqueAtomLabels_dict = {a_label:a_index for a_index, a_label in enumerate(self.uniqueAtomLabels) }
        for a_index, a_label in enumerate(label_list_unit_cell):
            for b_index, b_label in enumerate(label_list_expand_cell):
                if uniqueAtomLabels_dict[a_label] > uniqueAtomLabels_dict[b_label]:
                    distance_matrix_dict[a_label][b_label].append( distance_matrix[a_index, b_index] ) 
                else:
                    distance_matrix_dict[b_label][a_label].append( distance_matrix[a_index, b_index] ) 

        rbf = { a_label:{} for a_index, a_label in enumerate(self.uniqueAtomLabels) }
        for a_index, a_label in enumerate(self.uniqueAtomLabels):
            for b_index, b_label in enumerate(self.uniqueAtomLabels):

                distances = np.array(distance_matrix_dict[a_label][b_label]) if a_index >= b_index else np.array(distance_matrix_dict[b_label][a_label])
                distances = distances[ distances>0.1 ]

                rbf_a, bin_edges = np.histogram(distances, bins=number_of_bins, range=(0, cutoff))

                bin_centers = (bin_edges[1:]+bin_edges[:-1])/2

                # Normalize by bin volume and total number of atoms
                if bin_volume_normalize:
                    rbf_a = rbf_a/(4*np.pi/3 * (bin_edges[1:]**3-bin_edges[:-1]**3))

                if number_of_atoms_normalize:
                    rbf_a /= positions.shape[0]

                # Normalize by density
                if density_normalize:
                    rbf_a /= len(positions)/self.get_volume()

                rbf[a_label][b_label] = [bin_centers, rbf_a]

        return rbf

    def get_RBF(self, cutoff:float=6.0, number_of_bins:int=100, 
                bin_volume_normalize:bool=True, number_of_atoms_normalize:bool=True, density_normalize:bool=True,):

        number_of_bins = int(number_of_bins)

        # Process each frame in the trajectory
        cell = self.latticeVectors
        positions = self.atomPositions
        atom_Labels_List = self.atomLabelsList
        uniqueAtomLabels_dict = { ual:i for i, ual in enumerate(self.uniqueAtomLabels) }

        distance_matrix_dict = {a_label:{b_label:[] for b_index, b_label in enumerate(self.uniqueAtomLabels) if a_index >= b_index } for a_index, a_label in enumerate(self.uniqueAtomLabels) }
        ID_neighbors = self.find_ID_neighbors( other=self.kdtree, r=cutoff )

        for ID_a, ID_neighbors_a in enumerate(ID_neighbors):
            label_a = atom_Labels_List[ID_a]
            position_a = positions[ID_a]

            for ID_b in ID_neighbors_a: 
                label_b = atom_Labels_List[ID_b]
                position_b = positions[ID_b]

                if ID_a > ID_b:
                    if uniqueAtomLabels_dict[label_a] >= uniqueAtomLabels_dict[label_b]:
                        distance_matrix_dict[label_a][label_b].append( np.linalg.norm( position_a-position_b ) )
                    else:
                        distance_matrix_dict[label_b][label_a].append( np.linalg.norm( position_a-position_b ) )


        rbf = { a_label:{} for a_index, a_label in enumerate(self.uniqueAtomLabels) }
        for a_index, a_label in enumerate(self.uniqueAtomLabels):
            for b_index, b_label in enumerate(self.uniqueAtomLabels):

                distances = np.array(distance_matrix_dict[a_label][b_label]) if a_index >= b_index else np.array(distance_matrix_dict[b_label][a_label])
                distances = distances[ distances>0.1 ]

                rbf_a, bin_edges = np.histogram(distances, bins=number_of_bins, range=(0, cutoff))

                bin_centers = (bin_edges[1:]+bin_edges[:-1])/2

                # Normalize by bin volume and total number of atoms
                if bin_volume_normalize:
                    rbf_a = rbf_a/(4*np.pi/3 * (bin_edges[1:]**3-bin_edges[:-1]**3))

                if number_of_atoms_normalize:
                    rbf_a /= positions.shape[0]

                # Normalize by density
                if density_normalize:
                    rbf_a /= len(positions)/self.get_volume()

                rbf[a_label][b_label] = [bin_centers, rbf_a]

        return rbf

    def plot_RBF(self, periodic_image:int=0, cutoff:float=6.0, number_of_bins:int=100, partial_rbf:bool=True,
                output_path:str=None, save:bool=True, kdtree:bool=True, 
                bin_volume_normalize:bool=True, number_of_atoms_normalize:bool=True, density_normalize:bool=True, ):
        
        def _save(ax, name):
            plt.tight_layout()
            plt.savefig(name)  
            plt.clf()

        def _make_ax(a_label):
            fig, ax = plt.subplots()

            ax.set_xlabel('Distance (Angstrom)')
            ax.set_ylabel('g(r)')
            ax.set_title(f'Radial Distribution Function {a_label} ')

            return fig, ax 

        self.wrap()
        number_of_bins = int(number_of_bins)

        if kdtree:
            rbf = self.get_RBF( cutoff=cutoff, number_of_bins=number_of_bins,  
                                bin_volume_normalize=bin_volume_normalize, number_of_atoms_normalize=number_of_atoms_normalize, density_normalize=density_normalize)
        else:
            rbf = self.get_RBF_cdist(periodic_image=periodic_image, cutoff=cutoff, number_of_bins=number_of_bins,  
                                bin_volume_normalize=bin_volume_normalize, number_of_atoms_normalize=number_of_atoms_normalize, density_normalize=density_normalize)

        if partial_rbf:

            for a_index, a_label in enumerate(self.uniqueAtomLabels):
                fig, ax = _make_ax(a_label) 

                for b_index, b_label in enumerate(self.uniqueAtomLabels):
                    bin_centers, rbf_a = rbf[a_label][b_label]
                    color = self.element_colors[b_label] 

                    ax.plot(bin_centers, rbf_a, 'x-', alpha=0.8, color=color, label=f'd({a_label}-{b_label})' )
                    ax.fill_between(bin_centers, rbf_a, alpha=0.1, color=color )  # Rellena debajo de la línea con transparencia

                ax.legend()
                if save: _save(ax, f"{output_path}/RBF_{a_label}.png")
                plt.close(fig)

        rbf_total = np.sum([ rbf[a_label][b_label][1] for a_index, a_label in enumerate(self.uniqueAtomLabels) for b_index, b_label in enumerate(self.uniqueAtomLabels)], axis=0)
        fig, ax = _make_ax(a_label) 

        ax.plot(bin_centers, rbf_total, 'x-', color=(0.3, 0.3, 0.3))
        ax.fill_between(bin_centers, rbf_total, alpha=0.3, color=(0.3, 0.3, 0.3))  # Rellena debajo de la línea con transparencia

        if save: _save(ax, f"{output_path}/RBF_total.png")
        plt.close(fig)


    def count_species(self,  specie:list, sigma:float=1.4 ):

        # Process each frame in the trajectory
        positions = self.atomPositions
        atom_Labels_List = self.atomLabelsList
        uniqueAtomLabels_dict = { ual:i for i, ual in enumerate(self.uniqueAtomLabels) }
        self.wrap()

        cutoff = np.max([self.covalent_radii[label_a]+self.covalent_radii[label_b] for label_a in self.uniqueAtomLabels for label_b in self.uniqueAtomLabels])
        ans = {}
        #if specie.upper() in ['H2O', 'WATER']:
        for n in self.uniqueAtomLabels:
            ans = { }
            ID_specie = np.arange(self.atomCount)[self.atomLabelsList==n]
            for ID in ID_specie:



                ID_neighbors = self.find_all_neighbors_radius( x=self.atomPositions[ID], r=cutoff )
                embedding = sorted([ self.atomLabelsList[i] for i in ID_neighbors if self.covalent_radii[self.atomLabelsList[i]]+self.covalent_radii[n]*sigma > self.distance(positions[ID], positions[i]) and  i != ID ])
                if ''.join(embedding) in ans:
                    ans[''.join(embedding)] += 1
                else:
                    ans[''.join(embedding)] = 1

            for m in ans:
                print(n, ans[m], m)


