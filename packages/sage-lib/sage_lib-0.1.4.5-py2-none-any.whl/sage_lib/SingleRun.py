try:
    from sage_lib.KPointsManager import KPointsManager
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing KPointsManager: {str(e)}\n")
    del sys

try:
    from sage_lib.InputDFT import InputDFT
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing InputDFT: {str(e)}\n")
    del sys

try: 
    from sage_lib.PotentialManager import PotentialManager
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing PotentialManager: {str(e)}\n")
    del sys

try:
    from sage_lib.PeriodicSystem import PeriodicSystem
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing PeriodicSystem: {str(e)}\n")
    del sys

try:
    from sage_lib.NonPeriodicSystem import NonPeriodicSystem
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing NonPeriodicSystem: {str(e)}\n")
    del sys

try:
    from sage_lib.OutFileManager import OutFileManager
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing OutFileManager: {str(e)}\n")
    del sys

try:
    from sage_lib.BinaryDataHandler import BinaryDataHandler
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing BinaryDataHandler: {str(e)}\n")
    del sys

try:
    from sage_lib.WaveFileManager import WaveFileManager
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing WaveFileManager: {str(e)}\n")
    del sys

try:
    from sage_lib.ChargeFileManager import ChargeFileManager
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing ChargeFileManager: {str(e)}\n")
    del sys

try:
    from sage_lib.BashScriptManager import BashScriptManager
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing BashScriptManager: {str(e)}\n")
    del sys

try:
    from sage_lib.FileManager import FileManager
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


class SingleRun(FileManager): # el nombre no deberia incluir la palabra DFT tieneu qe ser ma general
    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        super().__init__(name=name, file_location=file_location)
        self._KPointsManager = None
        self._AtomPositionManager = None
        self._Out_AtomPositionManager = None
        self._PotentialManager = None
        self._InputFileManager = None
        self._BashScriptManager = None

        self._OutFileManager = None

    def NonPeriodic_2_Periodic(self, ):
        if self.AtomPositionManager is NonPeriodicSystem:
            PS = PeriodicSystem(**self.AtomPositionManager)
            self.atomPositions -= np.mean(self.atomPositions, axis=1) 

        return True
