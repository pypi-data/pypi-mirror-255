try:
    from sage_lib.FileManager import FileManager
except ImportError as e:
    import sys
    sys.stderr.write(f"Error importing FileManager: {e}\n")
    sys.exit(1)  # Exit if the FileManager is essential for DOSManager

class DOSManager(FileManager):
    def __init__(self, file_location: str = None, name: str = None, **kwargs):
        """
        Initialize DOSManager with optional file location and name.

        :param file_location: Path to the file containing DOS data.
        :param name: Descriptive name for the DOS data set.
        :param kwargs: Additional keyword arguments for base FileManager.
        """
        super().__init__(name=name, file_location=file_location)
        self._spin_polarized = None  # To be determined based on DOS data
        self._dos_total = None  # Total DOS data
        self._dos_ion = []  # Partial DOS data for each atom
        self._fermi = None
        self._E_fermi = None

    @property
    def E_fermi(self):
        if self._E_fermi is not None:
            return self._E_fermi
        elif self._fermi is not None:
            self._E_fermi = self._fermi
            return self._E_fermi
        else:
            return None

    def _read_total_dos(self, lines):
        """
        Read and parse total DOS data from given lines of a file.

        :param lines: List of string lines containing total DOS data.
        :return: Dictionary with total DOS and integrated DOS data.
        """
        dos_total = {'energies': [], 'dos_up': [], 'dos_down': [],
                     'integrated_dos_up': [], 'integrated_dos_down': []}

        for line in lines:
            values = list(map(float, line.split()))
            if len(values) == 5:
                self.spin_polarized = True 
                dos_total['energies'].append(values[0])
                dos_total['dos_up'].append(values[1])
                dos_total['dos_down'].append(values[2])
                dos_total['integrated_dos_up'].append(values[3])
                dos_total['integrated_dos_down'].append(values[4])
            elif len(values) == 3:
                self.spin_polarized = False
                dos_total['energies'].append(values[0])
                dos_total['dos_up'].append(values[1])  # Assuming 'dos_up' holds total DOS for non-spin-polarized case
                dos_total['integrated_dos_up'].append(values[2])  # Assuming 'integrated_dos_up' holds integrated DOS

        return dos_total

    def _read_ion_dos(self, lines):
        """
        Read and parse partial DOS data for a single ion from given lines of a file.

        :param lines: List of string lines containing partial DOS data for an ion.
        :return: Dictionary with partial DOS data for an ion.
        """
        dos_ion_template = {
            'energies': [],
            's_down': [], 's_up': [],
            'p_x_down': [], 'p_x_up': [],'p_y_down': [], 'p_y_up': [], 'p_z_down': [], 'p_z_up': [],
            'd_xy_down': [], 'd_xy_up': [], 'd_yz_down': [], 'd_yz_up': [], 
            'd_z2r2_down': [], 'd_z2r2_up': [], 'd_xz_down': [], 'd_xz_up': [],
            'd_x2y2_down': [], 'd_x2y2_up': [],
        } if self.spin_polarized else {
            'energies': [],
            's': [],
            'p_x': [], 'p_y': [],'p_z': [],
            'd_xy': [], 'd_yz': [], 'd_z2r2': [], 'd_xz': [], 'd_x2y2': [],
        } 

        dos_ion = {k: [] for k in dos_ion_template}  # Create a dictionary with lists for each orbital
        dos_ion['E_min'], dos_ion['E_max'], dos_ion['NEDOS'], dos_ion['fermi'], _ = list(map(float, lines[0].split()))

        for line in lines[1:]:  # Skip the first line which is header
            values = list(map(float, line.split()))
            if self.spin_polarized:
                for key, value in zip(dos_ion_template, values):
                    dos_ion[key].append(value)
            else:
                for key in dos_ion_template.keys():
                    # If not spin polarized, only every second key should be filled (assuming only 'up' keys are used)
                    dos_ion[key].extend(values[i:i+2] for i in range(0, len(values), 2))

        return dos_ion

    def _read_ions_dos(self, lines):
        """
        Read and parse partial DOS data for all ions from given lines of a file.

        :param lines: List of string lines containing partial DOS data for all ions.
        :return: List of dictionaries with partial DOS data for each ion.
        """
        for n in range(self._atomCount):
            start = (self._NEDOS + 1) * n
            end = start + self._NEDOS + 1
            self.dos_ion.append(self._read_ion_dos(lines[start:end]))

    def _read_header(self, lines):
        """
        Read and parse header information from the file.

        :param lines: First six lines from the file containing header information.
        """
        self._atomCount_spheres, self._atomCount, self._partial_DOS, self._NCDIJ = map(int, lines[0].split())
        self._Volume, self._a, self._b, self._c, self._POTIM = map(float, lines[1].split())
        self._TEBEG = float(lines[2].strip())
        self._name = lines[4].strip()
        self._E_min, self._E_max, self._NEDOS, self._fermi, _ = map(float, lines[5].split())
        self._NEDOS = int(self._NEDOS)

    def read_DOSCAR(self, file_location: str = None) -> bool:
        """
        Load DOS data from a file specified by the file location.

        This method reads the file, extracting header information, total DOS,
        and if available, partial DOS for each ion.

        :param file_location: Path to the file to load. Defaults to initialized file location.
        :return: True if loading succeeds, False otherwise.
        """
        file_location = file_location if type(file_location) == str else self._file_location

        lines = [n for n in self.read_file() ]        
        # Number of Ions (including empty spheres), Number of Ions, 0 (no partial DOS) or 1 (incl. partial DOS), NCDIJ (currently not used)     
        self._read_header(lines[:6])
        self.dos_total = self._read_total_dos(lines[6:6+self._NEDOS])
        self._read_ions_dos(lines[6+self._NEDOS:])

        return True

'''
path = '/home/akaris/Documents/code/Physics/VASP/v6.1/files/DOSCAR/surf_NiFeKOH/surf_NiFe_4H_4OH'
DM = DOSManager(path + "/DOSCAR")
DM.load()
print( DM.fermi )
'''