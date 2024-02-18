from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy as np

extensions = [
    Extension("qtape", ["src/qtape/qtape.pyx", "src/qtape/ctape.cpp"],
              extra_compile_args=["-march=native"],
              include_dirs=[np.get_include()],
              define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")]
    )
]

setup(
    ext_modules = cythonize(extensions, compiler_directives={"language_level" : "3"})
)
