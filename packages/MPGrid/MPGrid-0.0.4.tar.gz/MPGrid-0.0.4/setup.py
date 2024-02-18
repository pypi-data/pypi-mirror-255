from setuptools import setup, Extension
from glob import glob
import os

print()

if os.name == 'nt':
    setup(
        ext_modules=[
            Extension(
                name="MPGrid.MPGrid",
                sources=glob("lib/*.c"),
                define_macros=[('MP_PYTHON_LIB', None),],
                include_dirs=['zlib/include'],
                library_dirs=['zlib/lib/x64'],
                libraries=['zlibstat']
            )
        ]
    )
else:
   setup(
       ext_modules = [
           Extension(
               name="MPGrid.MPGrid",
               sources=glob("lib/*.c"),
               define_macros=[('MP_PYTHON_LIB', None),]
           )
       ]
   )
