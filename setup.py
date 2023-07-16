# setup.py for gempy_viewer. Requierements are numpy and matplotlib

from setuptools import setup, find_packages

setup(
    name='gempy_viewer',
    version='0.1',
    packages=find_packages(),
    url='',
    license='EUPL',
    author='Miguel de la Varga', 
    author_email='',
    description='Viewer for the geological modeling package GemPy',
    install_requires=['gempy>=2.2.9',
                      'numpy',
                      'matplotlib'
                      ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Scientific/Engineering :: GIS',
        'Programming Language :: Python :: 3.10'
    ],
    python_requires='>=3.10',
    include_package_data=True,
)
