from setuptools import setup, find_packages
from pathlib import Path

VERSION = '0.0.12' 
DESCRIPTION = 'A little package for GMP'
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="gmp", 
        version=VERSION,
        author="Oz Abramovich",
        author_email="oz@abramovich.net",
        description=DESCRIPTION,
        long_description=long_description,
        long_description_content_type='text/markdown',
        packages=find_packages(),
        install_requires=['string-color'], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'

        keywords=['python', 'first package'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)