"""""" # start delvewheel patch
def _delvewheel_patch_1_5_2():
    import os
    libs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'pillow_jxl_plugin.libs'))
    if os.path.isdir(libs_dir):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_5_2()
del _delvewheel_patch_1_5_2
# end delvewheel patch

from .pillow_jxl import *
from pillow_jxl import JpegXLImagePlugin

__doc__ = pillow_jxl.__doc__
if hasattr(pillow_jxl, "__all__"):
    __all__ = pillow_jxl.__all__
