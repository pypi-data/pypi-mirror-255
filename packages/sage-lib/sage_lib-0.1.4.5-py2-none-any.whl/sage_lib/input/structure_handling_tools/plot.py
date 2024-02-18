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

    def get_distances_vector(self,):
        pass

    def plot_RBF(self, periodic_image:int=0, cutoff:float=6.0, number_of_bins:int=100, partial_rbf:bool=True,
                output_path:str=None,
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

        if partial_rbf:
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

            for a_index, a_label in enumerate(self.uniqueAtomLabels):
                fig, ax = plt.subplots()

                ax.set_xlabel('Distance (Angstrom)')
                ax.set_ylabel('g(r)')
                ax.set_title(f'Radial Distribution Function {a_label} ')
                for b_index, b_label in enumerate(self.uniqueAtomLabels):

                    distances = np.array(distance_matrix_dict[a_label][b_label]) if a_index >= b_index else np.array(distance_matrix_dict[b_label][a_label])
                    distances = distances[ distances>0.1 ]

                    rdf, bin_edges = np.histogram(distances, bins=number_of_bins, range=(0, cutoff))

                    # Normalize by bin volume and total number of atoms
                    if bin_volume_normalize:
                        rdf = rdf/(4*np.pi/3 * (bin_edges[1:]**3-bin_edges[:-1]**3))

                    if number_of_atoms_normalize:
                        rdf /= positions.shape[0]

                    # Normalize by density
                    if density_normalize:
                        rdf /= len(positions)/self.get_volume()

                    bin_centers = (bin_edges[1:]+bin_edges[:-1])/2

                    color = self.element_colors[b_label] 

                    ax.plot(bin_centers, rdf, 'x-', alpha=0.8, color=color, label=f'd({a_label}-{b_label})' )
                    ax.fill_between(bin_centers, rdf, alpha=0.1, color=color )  # Rellena debajo de la línea con transparencia

                ax.legend()
                plt.tight_layout()
                plt.savefig(f"{output_path}/RBF_{a_label}.png")  
                plt.clf()

        distances = distance_matrix.flatten()
        distances = distances[ distances>0.1 ]

        rdf, bin_edges = np.histogram(distances, bins=number_of_bins, range=(0, cutoff))

        # Normalize by bin volume and total number of atoms
        if bin_volume_normalize:
            rdf = rdf/(4*np.pi/3 * (bin_edges[1:]**3-bin_edges[:-1]**3))

        if number_of_atoms_normalize:
            rdf /= positions.shape[0]

        # Normalize by density
        if density_normalize:
            rdf /= len(positions)/self.get_volume()

        bin_centers = (bin_edges[1:]+bin_edges[:-1])/2

        fig, ax = plt.subplots()

        ax.plot(bin_centers, rdf, 'x-', color=(0.3, 0.3, 0.3))
        ax.fill_between(bin_centers, rdf, alpha=0.3, color=(0.3, 0.3, 0.3))  # Rellena debajo de la línea con transparencia

        ax.set_xlabel('Distance (Angstrom)')
        ax.set_ylabel('g(r)')
        ax.set_title('Radial Distribution Function')
        
        plt.tight_layout()
        plt.savefig(f"{output_path}/RBF_total.png")  
        plt.clf()
