import setuptools
import os


def read(fname):
    path = os.path.join(os.path.dirname(__file__), fname)
    f = open(path)
    return f.read()

install_requires = [x for x in read('requirements.txt').strip().split('\n') if x]

setuptools.setup(
    name='metareserve',
    version='0.1.0',
    author='Sebastiaan Alvarez Rodriguez',
    author_email='a@b.c',
    description='A package providing a unified reservation interface',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/Sebastiaan-Alvarez-Rodriguez/metareserve',
    packages=setuptools.find_packages(),
    package_dir={'': '.'},
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=install_requires,
)