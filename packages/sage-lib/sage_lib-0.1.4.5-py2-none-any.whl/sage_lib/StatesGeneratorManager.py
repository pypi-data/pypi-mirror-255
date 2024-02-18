try:
    from sage_lib.DFTPartition import DFTPartition
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing DFTPartition: {str(e)}\n")
    del sys

try:
    import numpy as np
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys

class StatesGeneratorManager(DFTPartition):
    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        super().__init__(name=name, file_location=file_location)




