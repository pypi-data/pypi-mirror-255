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

try:
    import os
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing os: {str(e)}\n")
    del sys

try:
    import imageio
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing imageio: {str(e)}\n")
    del sys

try:
    from concurrent.futures import ProcessPoolExecutor
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing imageio: {str(e)}\n")
    del sys
    
try:
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing matplotlib.pyplot: {str(e)}\n")
    del sys
    
try:
    import seaborn as sns
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while seaborn: {str(e)}\n")
    del sys

try:
    from itertools import cycle
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing itertools: {str(e)}\n")
    del sys
try:
    from sage_lib.descriptor import MBTR
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing sage_lib.IO.descriptor.MBTR: {str(e)}\n")
    del sys


class MolecularDynamic_builder(PartitionManager):
    """
    Class for building and managing molecular dynamic simulations.
    
    Inherits from PartitionManager and integrates additional functionalities
    specific to molecular dynamics, such as calculating displacement and plotting.

    Attributes:
        _molecule_template (dict): A template for the molecule structure.
        _density (float): Density value of the molecule.
        _cluster_lattice_vectors (numpy.ndarray): Lattice vectors of the cluster.
    """

    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        """
        Initialize the MolecularDynamicBuilder object.

        Args:
            file_location (str, optional): File location of the input data.
            name (str, optional): Name of the simulation.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(name=name, file_location=file_location)

        self._molecule_template = {}
        self._density = None
        self._cluster_lattice_vectors = None

    def get_count_species(self,):
        """
        """
        count_species = []
        for container_i, container in enumerate(self.containers):
            count_species.append( container.AtomPositionManager.count_species() )

        return count_species

    def get_displacement(self, reference:str=None):
        """
        Calculate the displacement of atoms based on a reference point.

        Args:
            reference (str, optional): Reference axis or lattice vector ('a', 'b', 'c', 'x', 'y', 'z').

        Returns:
            numpy.ndarray: Array of displacement values for each atom.
        """

        data_displacement = []
        for container_i, container in enumerate(self.containers):

            if container_i == 0:
                displacement_reference_values = container.AtomPositionManager.atomPositions
                reference_values = self._calculate_reference_values(container, reference)

            displacement = np.linalg.norm(displacement_reference_values - container.AtomPositionManager.atomPositions, axis=1)
            data_displacement.append(displacement + reference_values)

        return np.array(data_displacement, dtype=np.float64 )
        
    def get_evaluation(self, ff_energy_tag:str='ff-energy', ff_forces_tag:str='ff-forces', ):
        """
        Collects and organizes energy and force data for training and validation.

        This method compiles energies and forces from the AtomPositionManager instances
        associated with each container in the current EvaluationManager. It organizes
        this data into a structured format suitable for comparison and further analysis.

        Parameters
        ----------
        ff_energy_tag : str, optional
            The tag used to identify force field energy data within the AtomPositionManager.
            Defaults to 'ff-energy'.
        ff_forces_tag : str, optional
            The tag used to identify force field forces data within the AtomPositionManager.
            Defaults to 'ff-forces'.

        Returns
        -------
        dict
            A dictionary containing structured energy and force data for training and
            validation purposes. The data includes reference and FF-calculated values
            for energies and forces, segregated by atomic species.

        Notes
        -----
        The method assumes that each container's AtomPositionManager has attributes
        for energies and forces tagged according to `ff_energy_tag` and `ff_forces_tag`.
        The energies and forces are expected to be accessible as numpy arrays.
        """

        # Validate input parameters
        ff_energy_tag = ff_energy_tag if isinstance(ff_energy_tag, str) else 'ff-energy'
        ff_forces_tag = ff_forces_tag if isinstance(ff_forces_tag, str) else 'ff-forces'

        # Initialize the data structure for collecting evaluation data
        N = len(self.containers)
        data = {
            'E': {'train': np.zeros(N), 'validation': np.zeros(N)},
            'N': {'train': np.zeros(N), 'validation': np.zeros(N)},
            'F': {'train': {}, 'validation': {}}
        }

        # Iterate over each container to populate the data structure
        for c_i, c in enumerate(self.containers):
            # Energy data
            data['E']['train'][c_i] = c.AtomPositionManager.E
            data['E']['validation'][c_i] = getattr(c.AtomPositionManager, ff_energy_tag, None)

            # Atom count data
            data['N']['train'][c_i] = c.AtomPositionManager.atomCount
            data['N']['validation'][c_i] = c.AtomPositionManager.atomCount

            # Forces data, organized by unique atomic labels
            for ul in c.AtomPositionManager.uniqueAtomLabels:
                # Training forces
                if ul in data['F']['train']:
                    data['F']['train'][ul] = np.vstack((data['F']['train'][ul], c.AtomPositionManager.total_force[c.AtomPositionManager.atomLabelsList == ul]))
                else:
                    data['F']['train'][ul] = c.AtomPositionManager.total_force[c.AtomPositionManager.atomLabelsList == ul]

                # Validation forces
                if ul in data['F']['validation']:
                    data['F']['validation'][ul] = np.vstack((data['F']['validation'][ul], getattr(c.AtomPositionManager, ff_forces_tag, None)[c.AtomPositionManager.atomLabelsList == ul]))
                else:
                    data['F']['validation'][ul] = getattr(c.AtomPositionManager, ff_forces_tag, None)[c.AtomPositionManager.atomLabelsList == ul]

        # Ensure all force data is converted to numpy arrays for consistent handling
        for key, item in data['F']['validation'].items():
            data['F']['validation'][key] = np.array(item, np.float64 )
        for key, item in data['F']['train'].items():
            data['F']['train'][key] = np.array(item, np.float64 )

        data['E']['train'] = np.array( data['E']['train'], np.float64 )
        data['E']['validation'] = np.array( data['E']['validation'], np.float64 )

        data['N']['train'] = np.array( data['E']['train'], np.float64 )
        data['N']['validation'] = np.array( data['E']['validation'], np.float64 )

        return data

    def get_bond_tracking(self, sigma:float=1.2, reference:str='Z', verbose:bool=True):
        '''
        '''
        if verbose: print(sigma)
        sigma = sigma if type(sigma) in [int, float] else 1.2
        initial_bonds = []
        c0 = self.containers[0].AtomPositionManager
        r_max = np.max( [c0.covalent_radii[a] for a in c0.uniqueAtomLabels] )
        for atomo_i, atomo in enumerate(c0.atomPositions):
            max_bond_lenth = (c0.covalent_radii[c0.atomLabelsList[atomo_i]]+r_max)*sigma
            neighbors = c0.find_all_neighbors_radius(x=atomo, r=max_bond_lenth)
            for neighbor in neighbors:
                distance = c0.distance( c0.atomPositions[atomo_i], c0.atomPositions[neighbor])
                if distance < (c0.covalent_radii[c0.atomLabelsList[atomo_i]]+c0.covalent_radii[c0.atomLabelsList[neighbor]])*sigma and distance > 0.4:
                    initial_bonds.append( [atomo_i, neighbor] )

        initial_bonds = np.array(initial_bonds, np.int64)
        data = np.zeros( (len(self.containers), initial_bonds.shape[0], 2) )

        for c_i, c in enumerate(self.containers):
            reference_pos = self._calculate_reference_values(c, reference='Z')
            for n_i, n in enumerate(initial_bonds):
                data[c_i, n_i, 0] = reference_pos[n[0]]
                data[c_i, n_i, 1] = c.AtomPositionManager.distance( c.AtomPositionManager.atomPositions[n[0]], c.AtomPositionManager.atomPositions[n[1]] )

        return {'initial_bonds_index':initial_bonds, 'bonds_data':data}

    def _plot_RBF_for_container(self, container, container_i, output_path, verbose:bool=True):
        """
        Función para trazar RBF para un contenedor específico.
        """
        if verbose: print(f'Plot container {container_i}')
        output_path_container = os.path.join(output_path, f'MD_RBF/{container_i}')
        self.create_directories_for_path(output_path_container)
        container.AtomPositionManager.plot_RBF(output_path=output_path_container, save=True)

    def plot_RBF(self, output_path:str=None):
        """

        """
        output_path = output_path if output_path is not None else '.' 
        data_displacement = []

        # Usar ProcessPoolExecutor para paralelizar
        with ProcessPoolExecutor() as executor:
            futures = [executor.submit(self._plot_RBF_for_container, container, container_i, output_path)
                       for container_i, container in enumerate(self.containers)]

            for future in futures:
                # Aquí puedes manejar los resultados o excepciones si es necesario
                result = future.result()

        return data_displacement

    def _calculate_reference_values(self, container, reference):
        """
        Calculate reference values based on the specified reference type.

        Args:
            container: The container holding atom positions and lattice vectors.
            reference (str): The reference type ('a', 'b', 'c', 'x', 'y', 'z').

        Returns:
            numpy.ndarray: Calculated reference values.
        """
        if type(reference) is str and reference.upper() in ['A', 'B', 'C']:
            lv_index = {'A': 0, 'B': 1, 'C': 2}[reference.upper()]
            lv = container.AtomPositionManager.latticeVectors[:, lv_index]
            return np.dot(container.AtomPositionManager.atomPositions, lv / np.linalg.norm(lv))
        
        if type(reference) is str and reference.upper() in ['X', 'Y', 'Z']:
            return container.AtomPositionManager.atomPositions[:, {'X': 0, 'Y': 1, 'Z': 2}[reference.upper()]]
    
        return np.zeros(container.AtomPositionManager.atomCount)

    def plot_displacement(self, data_displacement, output_path:str=None, save:bool=True, verbose:bool=True):
        """
        Plot the displacement of atoms.

        Args:
            data_displacement (numpy.ndarray): Displacement data to plot.
            save (bool, optional): Whether to save the plot as an image. Defaults to True.
            verbose (bool, optional): Enable verbose output. Defaults to True.
        """
        for u in self.containers[0].AtomPositionManager.uniqueAtomLabels:
            mask = self.containers[0].AtomPositionManager.atomLabelsList == u

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
            color = self.containers[0].AtomPositionManager.element_colors[u]

            ax1.plot(data_displacement[:, mask], color=color, alpha=0.3, lw=0.5)
            self.setup_subplot(ax1, 'Time', 'Displacements', f'Displacements for {u}')

            avg_displacement = np.mean(data_displacement[:, mask], axis=0)
            var_displacement = np.var(data_displacement[:, mask], axis=0)
            avg_displacement = self._calculate_reference_values(self.containers[0], 'c')[mask]
            ax2.plot(var_displacement, avg_displacement, 'o', label='Average', color=color)
            self.setup_subplot(ax2, 'Variance', 'Average', f'Average and Variance for {u}')

            plt.tight_layout()
            if save:
                plt.savefig(f'{output_path}/displacements_{u}.png', dpi=100)

            plt.clf()

            if verbose:
                print(f' >> Plot :: displacements ({u}) - data shape {data_displacement.shape}')

    def plot_count(self, count_dict, output_path:str=None, save:bool=True, verbose:bool=True ):
        diferent_species = set()
        for c in count_dict:
            for specie in c:
                diferent_species.add(specie) 
        diferent_species = list(diferent_species)

        frames = len(count_dict)
        num_specie = len(diferent_species)

        specie_count_frame = np.zeros( (frames, num_specie) )
        for j, c in enumerate(count_dict):

            for i, n in enumerate(diferent_species):
                specie_count_frame[j][i] = c.get(n, 0)

        specie_count_frame = np.array(specie_count_frame, np.int32)

        # Apply a predefined style
        plt.style.use('seaborn-darkgrid')  # Try 'ggplot', 'seaborn', etc. for different styles

        # Set up cycles for line styles and colors
        line_styles = cycle(['-', '--', '-.', ':'])  # Example line styles
        colors = cycle(['blue', 'green', 'red', 'purple', 'brown', 'black'])  # Example colors

        # Plotting each line with customized styles
        for line, label in zip(specie_count_frame.T, diferent_species):
            plt.plot(line, label=label, linestyle=next(line_styles), color=next(colors), linewidth=2)

        # Adding title and axis labels with customized fonts
        plt.title('Counting Independent Graphs', fontsize=14, fontweight='bold')
        plt.xlabel('Frame', fontsize=12)
        plt.ylabel('Count', fontsize=12)

        # Enhancing the legend
        plt.legend(loc='upper left', frameon=True, framealpha=0.9, facecolor='white')

        # Adding gridlines
        plt.grid(True, linestyle='--', alpha=0.7)

        # Fine-tuning axes
        plt.xticks(fontsize=10)
        plt.yticks(fontsize=10)
        plt.xlim([0, len(specie_count_frame[0]) - 1])  # Adjust according to your data
        plt.ylim([0, np.max(specie_count_frame) + 1])  # Adjust according to your data

        plt.tight_layout()
        if save:
            plt.savefig(f'{output_path}/count_plot.png', dpi=100)
        plt.clf()

        if verbose:
            data_shape = specie_count_frame.shape
            print(f' >> Plot :: Counting Independent Graphs - data shape {data_shape}')

    def plot_evaluation(self, data, output_path:str=None, save:bool=True, verbose:bool=False):
        """
        Generates and optionally saves plots comparing training and validation data, along with error distributions.

        Parameters:
        - data (dict): A nested dictionary containing 'train' and 'validation' keys, each associated with another dictionary
                       where keys correspond to atom types and values are Nx3 arrays of forces.
        - output_path (str): The directory path where the plots should be saved. Required if save is True.
        - save (bool): If True, saves the generated plots to the specified output_path. Default is True.
        - verbose (bool): If True, prints additional information about the plotting process. Default is False.

        The function creates scatter plots comparing training and validation data for each atom type, accompanied by
        histograms and density plots of the data distributions. Additionally, it generates histograms of the root mean
        square error between training and validation data sets for each atom type.
        """
        for n in data['F']['train']:
            fig = plt.figure(figsize=(8, 8))
            grid = plt.GridSpec(4, 4, hspace=0.5, wspace=0.5)

            # Extracting data for the current atom type and filtering based on specified conditions.
            data_x = np.linalg.norm(data['F']['train'][n],axis=1)#data['F']['train'][n][:,0]
            data_y = np.linalg.norm(data['F']['validation'][n],axis=1)#data['F']['validation'][n][:,0]
            data_y = data_y[np.abs(data_x) < 10]
            data_x = data_x[np.abs(data_x) < 10]

            # Main scatter plot of training vs. validation data.
            main_ax = fig.add_subplot(grid[:-1, 1:])
            main_ax.scatter(data_x, data_y, edgecolor=None, alpha=0.4, s=10, color=self.element_colors[n])
            main_ax.set(xlabel=f'Train {n}', ylabel=f'Validation {n}', xlim=(-0, 10), ylim=(-0, 10))

            # Density histogram (vertical) for validation data.
            right_ax = fig.add_subplot(grid[:-1, 0], xticklabels=[], sharey=main_ax)
            right_ax.hist(data_y, bins=20, orientation='horizontal', color='darkblue', density=True)
            right_ax.set(xlabel='Density')
            right_ax.yaxis.tick_right()

            # Adding density curve for the histogram on the right.
            density_validation, bins = np.histogram(data_y, bins=20, density=True)
            bin_centers_validation = 0.5 * (bins[:-1] + bins[1:])
            right_ax.plot(density_validation, bin_centers_validation, '-', color='grey')

            # Density histogram (horizontal) for training data.
            bottom_ax = fig.add_subplot(grid[-1, 1:], yticklabels=[], sharex=main_ax)
            bottom_ax.hist(data_x, bins=20, color='darkred', density=True)
            bottom_ax.set(ylabel='Density')

            # Adding density curve for the histogram below.
            density_train, bins = np.histogram(data_x, bins=20, density=True)
            bin_centers_train = 0.5 * (bins[:-1] + bins[1:])
            bottom_ax.plot(bin_centers_train, density_train, '-', color='grey')

            if save:
                plt.savefig(f'{output_path}/evaluation_{n}_plot.png', dpi=100)
            plt.clf()

            if verbose:
                print(f' >> Plot :: Evaluation {n} - data shape: {data["F"]["train"][n].shape}')

            # Error distribution plot for the current atom type.
            fig_error = plt.figure(figsize=(6, 4))
            error = np.sqrt((data_x - data_y) ** 2)
            error = error[error < 1]

            ax_error = fig_error.add_subplot(1, 1, 1)
            ax_error.hist(error, bins=100, color=self.element_colors[n], density=True)
            ax_error.set(title=f'Error Distribution specie {n}', xlabel='Error', ylabel='Density', xlim=(0, 0.7))

            # Adding density curve for the error distribution.
            density_error, bins_error = np.histogram(error, bins=100, density=True)
            bin_centers_error = 0.5 * (bins_error[:-1] + bins_error[1:])
            ax_error.plot(bin_centers_error, density_error, '-', color='darkgreen')

            plt.tight_layout()
            if save:
                plt.savefig(f'{output_path}/evaluation_error_{n}_plot.png', dpi=100)
            plt.clf()

            if verbose:
                print(f' >> Plot :: Error Distribution {n} - data shape: {error.shape}')


    def animated_RBF(self, output_path:str=None, duration:float=0.1, save:bool=True, verbose:bool=True):
        """

        """

        for u in self.containers[0].AtomPositionManager.uniqueAtomLabels:
            images = []
            #for file_name in sorted(os.listdir(file_location)):
                #if file_name.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            for container_i, container in enumerate(self.containers):
                file_path = f'MD_RBF/{container_i}/RBF_{u}.png'
                images.append(imageio.imread(file_path))
        
            if save:
                imageio.mimsave( f'MD_RBF{u}.gif', images, duration=duration)

    @staticmethod
    def setup_subplot(ax, xlabel, ylabel, title):
        """
        Set up the subplot with labels and title.

        Args:
            ax (matplotlib.axes.Axes): The axes object to setup.
            xlabel (str): Label for the x-axis.
            ylabel (str): Label for the y-axis.
            title (str): Title of the subplot.
        """
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        #ax.legend(loc='upper right')

    def plot_bond_tracking(self, bond_tracking_dict, output_path:str=None, window_size:float=None, save:bool=True, verbose:bool=True):
        
        def moving_average_std(x_values, z_value, mean_x, window_size):
            """Calculate moving average and moving standard deviation."""
            # Create bins based on the range of X values and the desired window size
            bins = np.arange(min(mean_x)-window_size/2, max(mean_x) + window_size, window_size)
            bin_indices = np.digitize(mean_x, bins)  # Assign each x to a bin

            bin_averages = {}
            bin_std = {}

            for i, b in enumerate(bins[1:]):
                bin_index = i+1
                #bin_index = 
                if bin_index not in bin_averages:
                    bin_averages[bin_index] = []
                if bin_index not in bin_std:
                    bin_std[bin_index] = []

                bin_averages[bin_index].append( x_values[bin_indices==bin_index] )
                bin_std[bin_index].append( z_value[bin_indices==bin_index] )
                
            mean_y = np.array([np.mean(n) for n in bin_averages.values()])
            std_y = np.array([np.mean(n) for n in bin_std.values()])
            x = (bins[1:]+bins[:-1])/2

            return x, mean_y, std_y

        label = np.array([[self.containers[0].AtomPositionManager.atomLabelsList[m] for m in n] for n in bond_tracking_dict['initial_bonds_index']])

        window_size = window_size if type(window_size) in [float, int] else 8.0  

        # Prepare to collect all y values and their std deviations
        all_y_values = []
        all_std_y = []

        for n in self.containers[0].AtomPositionManager.uniqueAtomLabels:

            # Improved plot aesthetics
            plt.figure(figsize=(10, 6))  # Set figure size
            plt.xlabel('X Axis Label')  # Set X axis label
            plt.ylabel('Y Axis Label')  # Set Y axis label
            plt.title(f'Distance from ({n})')  # Set title
            plt.grid(True)  # Add grid

            for m in self.containers[0].AtomPositionManager.uniqueAtomLabels:

                filter_ID = (label[:,0] == n) & (label[:,1] == m) 

                if np.sum(filter_ID) > 1:
                    # Calculate mean and standard deviation for x and y
                    mean_x = np.mean(bond_tracking_dict['bonds_data'], axis=0)[filter_ID, 0]
                    std_x = np.std(bond_tracking_dict['bonds_data'], axis=0)[filter_ID, 0]
                    mean_y = np.mean(bond_tracking_dict['bonds_data'], axis=0)[filter_ID, 1]
                    std_y = np.std(bond_tracking_dict['bonds_data'], axis=0)[filter_ID, 1]

                    # Collect y values and their std deviations
                    ma_y, ma_mean_y, ma_std_y = moving_average_std(mean_y, std_y, mean_x, window_size)

                    # Plotting the moving average line and shaded area
                    plt.fill_between( ma_y, ma_mean_y - ma_std_y, ma_mean_y + ma_std_y, color=self.element_colors[m], alpha=0.4)  # Shaded area for std deviation

                    # Plot with error bars
                    plt.errorbar(mean_x, mean_y, xerr=std_x, yerr=std_y, fmt='o', color=self.element_colors[m], alpha=0.5, label=f'd({n}-{m})', capsize=5) 
                    
            # Legend
            plt.legend()

            #Show plot
            if save:
                plt.savefig(f'{output_path}/bond_tracking_{n}_plot.png', dpi=100)

    def handleMDAnalysis(self, values:list, file_location:str=None):
        """
        Handle molecular dynamics analysis based on specified values.

        Args:
            values (list): List of analysis types to perform.
            file_location (str, optional): File location for output data.
        """
        MDA_data = {}

        for plot in values:
            if plot.upper() == 'displacements':
                MDA_data['displacement'] = self.get_displacement(reference=values[plot].get('reference', None))
                self.plot_displacement( data_displacement=MDA_data['displacement'], output_path=values[plot].get('output_path', '.'), verbose=values[plot].get('verbose', False) )

            if plot.upper() == 'RBF':
                MDA_data['RBF'] = self.plot_RBF()
                self.animated_RBF( output_path=values[plot].get('output_path', '.'), duration=0.1, save=True, verbose=values[plot].get('verbose', False) )

            if plot.upper() == 'COUNT':
                MDA_data['count'] = self.get_count_species()
                self.plot_count( count_dict=MDA_data['count'], output_path=values[plot].get('output_path', '.'), save=True, verbose=values[plot].get('verbose', False) )

            if plot.upper() == 'EVALUATE_FF':
                MDA_data['evaluation'] = self.get_evaluation(
                                                    ff_energy_tag=values[plot].get('ff_energy_tag', 'ff-energy'),
                                                    ff_forces_tag=values[plot].get('ff_forces_tag', 'ff-forces'),
                                                            )
                self.plot_evaluation(data=MDA_data['evaluation'], output_path=values[plot].get('output_path', '.'), save=True, verbose=values[plot].get('verbose', False) )

            if plot.upper() == 'BOND_TRACKING':
                MDA_data['bond_tracking'] = self.get_bond_tracking(sigma=values[plot].get('sigma', None), reference=values[plot].get('reference', None))
                self.plot_bond_tracking( bond_tracking_dict=MDA_data['bond_tracking'], output_path=values[plot].get('output_path', '.'), save=True, verbose=values[plot].get('verbose', False) )

                #self.plot_count( count_dict=MDA_data['count'], output_path=values[plot].get('output_path', '.'), save=True, verbose=values[plot].get('verbose', False) )



'''
import numpy as np
import ase.io
from ase.build import bulk
from dscribe.descriptors import LMBTR

# Lets create iron in BCC phase
n_z = 8
n_xy_bcc = 10
a_bcc = 2.866
bcc = bulk("Fe", "bcc", a=a_bcc, cubic=True) * [n_xy_bcc, n_xy_bcc, n_z]

# Lets create iron in FCC phase
a_fcc = 3.5825
n_xy_fcc = 8
fcc = bulk("Fe", "fcc", a=a_fcc, cubic=True) * [n_xy_fcc, n_xy_fcc, n_z]

# Setting up the descriptor
descriptor = LMBTR(
    grid={"min": 0, "max": 12, "sigma": 0.1, "n": 200},
    geometry={"function": "distance"},
    weighting={"function": "exp", "scale": 0.5, "threshold": 1e-3},
    species=["Fe"],
    periodic=True,
)

# Calculate feature references
bcc_features = descriptor.create(bcc, [0])
fcc_features = descriptor.create(fcc, [0])

# Combine into one large grain boundary system with some added noise
bcc.translate([0, 0, n_z * a_fcc])
combined = bcc + fcc
combined.set_cell([
    n_xy_bcc * a_bcc,
    n_xy_bcc * a_bcc,
    n_z * (a_bcc + a_fcc)
])
combined.rattle(0.1, seed=7)

# Create a measure of of how similar the atoms are to the reference. Euclidean
# distance is used and the values are scaled between 0 and 1 from least similar
# to identical with reference.
def metric(values, reference):
    dist = np.linalg.norm(values - reference, axis=1)
    dist_max = np.max(dist)
    return  1 - (dist / dist_max)

# Create the features and metrics for all atoms in the sample.
combined_features = descriptor.create(combined)
fcc_metric = metric(combined_features, fcc_features)
bcc_metric = metric(combined_features, bcc_features)

# Write an image with the atoms coloured corresponding to their similarity with
# BCC and FCC: BCC = blue, FCC = red
n_atoms = len(combined)
colors = np.zeros((n_atoms, 3))
for i in range(n_atoms):
    colors[i] = [fcc_metric[i], 0, bcc_metric[i]]
ase.io.write(
    f'coloured.png',
    combined,
    rotation='90x,20y,20x',
    colors=colors,
    show_unit_cell=1,
    maxwidth=2000,
)


asdf

import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt




def aplicar_pca_y_clasificar(datos, n_componentes=2):
    """
    Aplica PCA a los datos proporcionados y clasifica en el número especificado de componentes principales.

    :param datos: Array de numpy con los datos (espectros de potencia).
    :param n_componentes: Número de componentes principales para clasificar.
    :return: Datos transformados y modelo PCA.
    """

    # Crear una instancia de PCA
    pca = PCA(n_components=n_componentes)

    # Ajustar y transformar los datos
    datos_transformados = pca.fit_transform(datos)

    # Opcional: Visualizar los resultados
    plt.figure(figsize=(8, 6))
    if n_componentes == 2:
        plt.scatter(datos_transformados[:, 0], datos_transformados[:, 1])
        plt.xlabel('Componente Principal 1')
        plt.ylabel('Componente Principal 2')
    elif n_componentes > 2:
        from mpl_toolkits.mplot3d import Axes3D
        ax = plt.figure().gca(projection='3d')
        ax.scatter(datos_transformados[:, 0], datos_transformados[:, 1], datos_transformados[:, 2])
        ax.set_xlabel('Componente Principal 1')
        ax.set_ylabel('Componente Principal 2')
        ax.set_zlabel('Componente Principal 3')
    plt.title('PCA de los Espectros de Potencia')
    plt.show()

    return datos_transformados, pca


# Supongamos que tienes tus datos en un array de numpy, donde cada fila es una observación (p. ej., posición de un átomo 'O' en un instante)
# y cada columna es una característica (p. ej., coordenadas x, y, z).
datos = np.random.rand(100,10)  # Reemplaza esto con tus datos reales
aplicar_pca_y_clasificar(datos)

# Definir el número de clusters
n_clusters = 3  # Ajusta esto según tus necesidades

# Aplicar k-means
kmeans = KMeans(n_clusters=n_clusters)
kmeans.fit(datos)

# Etiquetas de los clusters
etiquetas = kmeans.labels_

# Centroides de los clusters (pueden ser útiles para entender qué caracteriza a cada cluster)
centroides = kmeans.cluster_centers_

# Visualizar los resultados (opcional, pero útil)
plt.scatter(datos[:, 0], datos[:, 1], c=etiquetas, cmap='viridis')
plt.scatter(centroides[:, 0], centroides[:, 1], c='red', marker='X')
plt.title('Clustering de datos de dinámica molecular')
plt.xlabel('Coordenada X')
plt.ylabel('Coordenada Y')
plt.show()
'''