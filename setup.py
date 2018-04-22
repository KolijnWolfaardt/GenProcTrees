from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='GenProcTrees',
    version='0.0.1.dev1',

    description='Procedurally generate semi-realistic trees',
    long_description=long_description,
    long_description_content_type='text/markdown',

    url='https://github.com/KolijnWolfaardt/GenProcTrees',

    author='Kolijn Wolfaardt',
    # author_email='',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Artistic Software',
        'Topic :: Multimedia :: Graphics :: 3D Modeling',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='procedural generation tree',
    packages=find_packages(exclude=['contrib', 'docs', 'tests', 'images']),
    install_requires=['numpy', 'scipy', 'Pillow'],
    # extras_require={  # Optional
    #     'dev': ['check-manifest'],
    #     'test': ['coverage'],
    # },
)
