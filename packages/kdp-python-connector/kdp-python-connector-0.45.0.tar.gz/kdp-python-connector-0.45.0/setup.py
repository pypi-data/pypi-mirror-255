import sys

from setuptools import setup, find_packages

version = '0.0.1'
if '--version' in sys.argv:
    index = sys.argv.index('--version')
    sys.argv.pop(index)
    version = sys.argv.pop(index)

name = 'kdp-python-connector'
if '--name' in sys.argv:
    index = sys.argv.index('--name')
    sys.argv.pop(index)
    name = sys.argv.pop(index)

DESCRIPTION = 'Python Connector for KDP Platform'
LONG_DESCRIPTION = 'Python Connector For Interacting with KDP Platform for various ingestion and retrieval tasks'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name=name,
        version=version,
        author="Koverse development team",
        author_email="developer@koverse.com",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=['pandas~=1.3.5', 'numpy~=1.21.6', 'kdp-api-python-client==4.114.0'],  # add any additional packages that
        # needs to be installed along with your package. Eg: 'caer'

        keywords=['python', 'kdp'],
        # classifiers= [
        #     "Development Status :: 3 - Alpha",
        #     "Intended Audience :: Science/Research",
        #     "Intended Audience :: Developers",
        #     "Programming Language :: Python :: 3.8",
        #     "Operating System :: MacOS :: MacOS X",
        # ]
)
