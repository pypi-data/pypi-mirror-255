try:
    from sage_lib.StatesGeneratorManager import StatesGeneratorManager
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing StatesGeneratorManager: {str(e)}\n")
    del sys

try:
    from sage_lib.NonPeriodicSystem import NonPeriodicSystem
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing NonPeriodicSystem: {str(e)}\n")
    del sys

try:
    from sage_lib.DFTSingleRun import DFTSingleRun
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing DFTSingleRun: {str(e)}\n")
    del sys

try:
    import numpy as np
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys

class VacuumStatesGenerator(StatesGeneratorManager):
    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        super().__init__(name=name, file_location=file_location)
        

    def generate_dimers(self, AtomLabels:list=None, bond_lengths:dict=None, steps:int=10, file_location=None) -> list:
        containers = []
        sub_directories = []
        # parameter = parameter.upper().strip()

        # Assuming self.containers is already defined and AtomLabels is initially None or an empty set
        AtomLabels = AtomLabels or list(set().union(*(container.AtomPositionManager.uniqueAtomLabels for container in self.containers)))

        for atomlabel_A_index, atomlabel_A in enumerate(AtomLabels):
            for atomlabel_B_index, atomlabel_B in enumerate(AtomLabels[atomlabel_A_index:] ):
                container_copy = self.copy_and_update_container(self.containers[0], '', file_location) if len(self.containers) > 0 else DFTSingleRun()
                container_copy.AtomPositionManager = NonPeriodicSystem(file_location)
                
                if bond_lengths is None:
                    c, s = self.handle_dimers(container_copy, steps, atomlabel_A, atomlabel_B, file_location=file_location)
                else:
                    c, s = self.handle_dimers(container_copy, steps, atomlabel_A, atomlabel_B, bond_lengths['initial_distance'], bond_lengths['final_distance'], file_location)

                containers += c
                sub_directories += s

        self.generate_execution_script_for_each_container(sub_directories, self.file_location + '/generate_dimers')
        self.containers = containers

        return containers

    def handle_dimers(self, container, steps:int=None, atomlabel_A:str=None, atomlabel_B:str=None, initial_distance:float=None, final_distance:float=None, file_location:str=None):
        
        initial_distance = initial_distance if initial_distance is not None else (self.covalent_radii[atomlabel_A]+self.covalent_radii[atomlabel_B])*0.85
        final_distance = final_distance if final_distance is not None else 5
        delta_distance =  (final_distance-initial_distance)/steps
        sub_directories, containers = [], []

        for s in range(steps):
            distance = initial_distance + delta_distance*float(s)
            container_copy = self.copy_and_update_container(container, f'/generate_dimers/{atomlabel_A}_{atomlabel_B}_{s}', file_location)
            container_copy.AtomPositionManager._comment = f'handle_dimers {atomlabel_A}-{atomlabel_B} d:{distance}'
            container_copy.AtomPositionManager._scaleFactor = [1.0] # scale factor
            container_copy.AtomPositionManager._selectiveDynamics = True  # bool 
            container_copy.AtomPositionManager.add_atom(atomLabels=atomlabel_A, 
                                                        atomPosition=[0,0,0], )
            container_copy.AtomPositionManager.add_atom(atomLabels=atomlabel_B, 
                                                        atomPosition=[distance,0,0], )
            print(container_copy.file_location)
            print(container_copy.AtomPositionManager.atomCount)
            print(container_copy.file_location)

            containers.append( container_copy )
            sub_directories.append(f'/generate_dimers/{atomlabel_A}_{atomlabel_B}_{s}')
            
        return containers, sub_directories


'''
path = '/home/akaris/Documents/code/Physics/VASP/v6.1/files/OUTCAR'
path = '/home/akaris/Documents/code/Physics/VASP/v6.1/files/dataset/CoFeNiOOH_jingzhu/surf_CoFe_4H_4OH/MAG'
VSG = VacuumStatesGenerator(path)

VSG.readVASPFolder(v=False)
VSG.generate_dimers( AtomLabels=['Ni','C','N'] )
VSG.NonPeriodic_2_Periodic( [[18,0,0],[0,18,0],[0,0,18]] )
asdf
VSG.exportVaspPartition()


asd



print(DP.containers[0].AtomPositionManager.pbc)
DP.generateDFTVariants('band_structure', values=[20])
DP.exportVaspPartition()
'''

