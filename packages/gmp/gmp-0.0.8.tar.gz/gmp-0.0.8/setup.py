from setuptools import setup, find_packages

VERSION = '0.0.8' 
DESCRIPTION = 'A little package for GMP'
LONG_DESCRIPTION = 'This is just a little package I made for my GMP teacher.'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="gmp", 
        version=VERSION,
        author="Oz Abramovich",
        author_email="oz@abramovich.net",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=['string-color', 're'], # add any additional packages that 
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