try:
    from sage_lib.master.FileManager import FileManager
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing FileManager: {str(e)}\n")
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

class XYZ(FileManager):
    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        super().__init__(name=name, file_location=file_location)

    def export_as_xyz(self, file_location:str=None, save_to_file:str='w', verbose:bool=False,
                            species:bool=True, position:bool=True, energy:bool=True, forces:bool=True, charge:bool=True, magnetization:bool=True, lattice:bool=True, pbc:bool=True, time:bool=True,
                            position_tag:str='pos', forces_tag:str='forces', charge_tag:str='charge', magnetization_tag:str='magnetization', energy_tag:str='E',
                            time_tag:str='time', pbc_tag:str='pbc') -> str:
        """
        Export atomistic information in the XYZ format.

        Parameters:
            file_location (str): The location where the XYZ file will be saved. Ignored if save_to_file is False.
            save_to_file (bool): Flag to control whether to save the XYZ content to a file.
            verbose (bool): Flag to print additional information, if True.

        Returns:
            str: The generated XYZ content.
        """
        file_location  = file_location  if not file_location  is None else self.file_location+'config.xyz' if self.file_location is str else self.file_location
        self.group_elements_and_positions()

        # Ensuring no property is included if its value is None
        lattice = hasattr(self, 'latticeVectors') and self.latticeVectors is not None and lattice
        species = hasattr(self, 'atomLabelsList' ) and self.atomLabelsList is not None and species 
        position = hasattr(self, 'atomPositions') and self.atomPositions is not None and position
        forces = hasattr(self, 'total_force') and self.total_force is not None and forces
        charge = hasattr(self, 'total_charge') and self.total_charge is not None and charge
        magnetization = hasattr(self, 'magnetization') and self.magnetization is not None and magnetization
        energy = hasattr(self, 'E') and energy and self.E is not None and energy
        pbc = hasattr(self, 'latticeVectors') and self.latticeVectors is not None and pbc
        time = hasattr(self, 'time') and self.time is not None and time 

        # Constructing the header information dynamically
        properties_list = [
            f'Lattice="{ " ".join(map(str, self.latticeVectors.flatten())) }"' if lattice else '',
            f'Properties={":".join(filter(None, [f"species:S:1" if species else "", f"{position_tag}:R:3" if position else "", f"{forces_tag}:R:3" if forces else "", f"{charge_tag}:R:1" if charge else "", f"{magnetization_tag}:R:1" if magnetization else ""]))}',
            f'{energy_tag}={self.E}' if energy else '',
            f'{pbc_tag}="T T T"' if pbc else '',
            f'{time_tag}={self.time}' if time else ''
        ]
        properties_str = ' '.join(filter(None, properties_list))

        # Preparing atom data lines
        atom_lines = [
            f"{self.atomLabelsList[i]} {' '.join(map('{:12.6f}'.format, self.atomPositions[i])) if position else ''} {' '.join(map('{:14.6f}'.format, self.total_force[i])) if forces else ''}  {' '.join(map('{:14.6f}'.format, self.total_charge[i])) if charge else ''} {' '.join(map('{:14.6f}'.format, self.magnetization[i])) if magnetization else ''}"
            for i in range(self.atomCount)
        ] if position or forces else []

        # Combining header and atom data
        xyz_content = f"{self.atomCount}\n{properties_str}\n" + "\n".join(atom_lines)+ "\n"

        # Saving to file if required
        if file_location and save_to_file != 'none':
            with open(file_location, save_to_file) as f:
                f.write(xyz_content)
            if verbose:
                print(f"XYZ content saved to {file_location}")

        return xyz_content

    def read_XYZ(self, file_location: str = None, lines: list = None, tags:dict=None, verbose: bool = False) -> dict:
        """
        Reads and parses data from an XYZ configuration file used in molecular simulations.

        This method supports custom tags for various properties such as energy, masses, forces,
        positions, species, periodic boundary conditions (PBC), lattice information, and simulation time.

        Parameters:
            file_location (str, optional): Location of the XYZ file. Defaults to instance file location if None.
            lines (list, optional): List of lines from the file to be read directly if provided.
            tags (dict, optional): Dictionary of tags for custom property identification.
            verbose (bool, optional): Enables detailed logging if set to True.

        Returns:
            bool: True if the file is successfully read and parsed, False otherwise.
        """ 

        # Default tags for properties if not provided
        default_tags = {
            'energy': 'E',
            'mass': 'masses',
            'forces': 'forces',
            'position': 'pos',
            'species': 'species',
            'pbc': 'pbc',
            'time': 'time',
            'Lattice': 'Lattice',
            'Properties': 'Properties',
        }
        tags = {k: tags.get(k, v) for k, v in default_tags.items()} if tags else default_tags

        file_location = file_location if isinstance(file_location, str) else self.file_location

        # Regex pattern to match property keys and values
        pattern = r'(\w+)=("[^"]+"|\S+)'

        # Define mappings for data types
        dtype_map = {
            "R": np.float64,
            "S": np.object,  # Assuming np.array defaults for string type or custom logic if needed
            "I": np.int64,
        }

        # Mapping property keys to object attributes
        property_to_attr = {
            tags['forces']: "_total_force",
            tags['mass']: "_mass",
            tags['position']: "_atomPositions",
            tags['species']: "_atomLabelsList",
        }

        lines = lines or list(self.read_file(file_location, strip=False))
        read_header = False

        for i, line in enumerate(lines):
            if read_header:
                matches = re.findall(pattern, line)
                body = np.array([n.strip().split() for n in lines[i + 1:i + self._atomCount + 1]])
                for key, value in matches:
                    self._process_key_value(key, value, tags, dtype_map, property_to_attr, body)

                return True

            elif line.strip().isdigit():
                num_atoms = int(line.strip())
                if num_atoms > 0:
                    self._atomCount = num_atoms
                    read_header = True 

        return {
                'position':self.atomPositions,
                'atomCount':self._atomCount,
                'species':self.atomLabelsList, 
                }

    def _process_key_value(self, key, value, tags, dtype_map, property_to_attr, body):
        """
        Processes each key-value pair found in the XYZ file.

        Parameters:
            key (str): The key identified in the line.
            value (str): The value associated with the key.
            tags (dict): Dictionary of property tags.
            dtype_map (dict): Mapping of data types for properties.
            property_to_attr (dict): Mapping of property keys to object attributes.
            body (np.ndarray): Array containing the data extracted from the XYZ file.
        """
        if key == tags['Lattice']:
            self._latticeVectors = np.array([[float(value[1:-1].strip().split()[i * 3 + j]) for j in range(3)] for i in range(3)])
            self._atomCoordinateType = 'C'

        elif key == tags['Properties']:
            self._parse_properties(value, body, dtype_map, property_to_attr)

        elif key == tags['energy']:
            self._E = float(value)

        elif key == tags['pbc']:
            self._pbc = ['T' in v for v in value.split()]

        elif key == tags['time']:
            self._time = float(value)

        else:
            setattr(self, key, value)

    def _parse_properties(self, properties_str, body, dtype_map, property_to_attr):
        """
        Parses the 'Properties' string to extract and assign properties to their respective attributes.

        Parameters:
            properties_str (str): The properties string from the XYZ file.
            body (np.ndarray): The body of the section containing property values.
            dtype_map (dict): Mapping of data types for properties.
            property_to_attr (dict): Mapping of property keys to object attributes.
        """
        count_col = 0
        matches_Properties_list = [properties_str.split(':')[i:i + 3] for i in range(0, len(properties_str.split(':')), 3)]

        for pi, p in enumerate(matches_Properties_list):
            property_value = body[:, count_col:count_col + int(p[2])]

            # Convert dtype based on the type specification in p[1]
            property_value = np.array(property_value, dtype=dtype_map[p[1]]) if p[1] in dtype_map else property_value

            # Transform column vector to row vector if necessary, else leave matrices as is
            property_value = property_value.T[0] if property_value.shape[1] == 1 else property_value

            # Assign property_value to the respective attribute based on p[0]
            attr_name = property_to_attr.get(p[0], p[0])  # Fallback to p[0] if not in property_to_attr
            setattr(self, attr_name, property_value)

            count_col += int(p[2])

    def read_file(self, file_location, strip=True):
        """
        Reads the content of a file.

        Parameters:
            file_location (str): The location of the file to read.
            strip (bool, optional): Determines if lines should be stripped of whitespace.

        Yields:
            str: Lines from the file.
        """
        with open(file_location, 'r') as f:
            for line in f:
                yield line.strip() if strip else line



