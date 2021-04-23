import setuptools
import configparser
import os
import pathlib

parser = configparser.ConfigParser()

path = os.path.join(str(pathlib.Path(__file__).parent.absolute()), 'setup.cfg')
parser.read(path)


del parser['metadata']['long_description'] # We need to read the long description ourselves
with open('README.md', 'r') as fh:
    long_description = fh.read()

del parser['options']['package_dir']
package_dir = {'': 'metareserve'}
del parser['options']['packages']
packages=setuptools.find_packages(where='metareserve')

readopts = parser['metadata']
readopts.update(parser['options'])
setuptools.setup(long_description=long_description, package_dir=package_dir, packages=packages, **readopts)
# setuptools.setup(
#     name='metareserve',
#     version='0.1.0',
#     author='Sebastiaan Alvarez Rodriguez',
#     author_email='a@b.c',
#     description='A package providing a unified reservation interface',
#     long_description=long_description,
#     long_description_content_type='text/markdown',
#     url='https://github.com/Sebastiaan-Alvarez-Rodriguez/metareserve',
#     packages=setuptools.find_packages(),
#     classifiers=(
#         'Programming Language :: Python :: 3',
#         'License :: OSI Approved :: MIT License',
#         'Operating System :: OS Independent',
#     ),
# )