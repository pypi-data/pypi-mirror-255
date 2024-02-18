from setuptools import setup, Extension
from glob import glob
import os
import numpy as np
import MPGrid

if os.name == 'nt':
    setup(
        ext_modules=[
            Extension(
                name='MPGLGrid.MPGLGrid',
                sources=glob("libgl/*.c"),
                include_dirs=[MPGrid.get_include(), np.get_include()],
                define_macros=[('MP_PYTHON_LIB', None), ('WIN32', None)],
                libraries=['opengl32', 'glu32']
            )
        ]
    )
else:
    setup(
        ext_modules=[
            Extension(
                name='MPGLGrid.MPGLGrid',
                sources=glob("libgl/*.c"),
                include_dirs=[MPGrid.get_include(), np.get_include()],
                define_macros=[('MP_PYTHON_LIB', None)],
                libraries=['GL', 'GLU']
            )
        ]
    )

