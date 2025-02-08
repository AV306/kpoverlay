from setuptools import setup
from Cython.Build import cythonize

# Call this with python setup.py build_ext --inplace

setup(
    ext_modules=cythonize(
        "history_overlay.py"
    )
)