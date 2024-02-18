try:
    from sage_lib.single_run.SingleRunDFT import SingleRunDFT
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing SingleRunDFT: {str(e)}\n")
    del sys
    
try:
    import numpy as np
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys

class SingleRun(SingleRunDFT): # el nombre no deberia incluir la palabra DFT tieneu qe ser ma general
    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        super().__init__(name=name, file_location=file_location)

        self._loaded = {}
        self._AtomPositionManager = None
        self._Out_AtomPositionManager = None
        self._InputFileManager = None
        self._KPointsManager = None
        self._PotentialManager = None
        self._BashScriptManager = None
        self._vdw_kernel_Handler = None
        self._OutFileManager = None
        self._WaveFileManager = None
        self._ChargeFileManager = None

    def read_structure(self, file_location, source, *args, **kwargs):
        """

        """
        try:
            self.AtomPositionManager = self.AtomPositionManager_constructor(file_location)
            self.AtomPositionManager.read(source=source, file_location=file_location)
        except Exception as e:
            print(f"Failed to read {file_location} as {source}: {e}")

    def export_structure(self, file_location, source, *args, **kwargs):
        """

        """
        try:
            self.AtomPositionManager = self.AtomPositionManager_constructor(file_location)
            self.AtomPositionManager.export(source=source, file_location=file_location)

        except Exception as e:
            print(f"Failed to export {file_location} as {source}: {e}")
