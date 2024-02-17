#
# @file __init__.py
# @author Markus Führer
# @date 5 May 2023
# @copyright Copyright © 2023 Bentham Instruments Ltd. All Rights Reserved.
#


# start delvewheel patch
def _delvewheel_patch_1_5_2():
    import os
    libs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'benanalysis.libs'))
    if os.path.isdir(libs_dir):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_5_2()
del _delvewheel_patch_1_5_2
# end delvewheel patch

from benanalysis._benpy_core import *
from benanalysis._benpy_core import colorimetry
from benanalysis._benpy_core import io
from benanalysis._benpy_core import monochromator
from benanalysis._benpy_core import physics
from benanalysis._benpy_core import utils
