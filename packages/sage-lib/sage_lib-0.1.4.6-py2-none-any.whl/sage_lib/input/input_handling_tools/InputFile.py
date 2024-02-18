try:
    from sage_lib.input.input_handling_tools.InputDFT import InputDFT
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing sage_lib.input.input_handling_tools.InputDFT: {str(e)}\n")
    del sys

try:
    from sage_lib.input.input_handling_tools.InputClassic import InputClassic
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing sage_lib.input.input_handling_tools.InputClassic: {str(e)}\n")
    del sys

try:
    import numpy as np
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys

class InputFile(InputDFT, InputClassic):
    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        super().__init__(name=name, file_location=file_location)
        self._comment = None

    def var_assing(self, var_name, var_value):
        if not var_name in self.attr_dic.keys():
            self.attr_dic[var_name] = var_value
            setattr(self, var_name, var_value)
        else:
            self.attr_dic[var_name] = var_value
            setattr(self, var_name, var_value)
            
