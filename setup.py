from setuptools import setup, find_packages

# def read_version():
#     with open('gempy/__init__.py', 'r', encoding='utf-8') as f:
#         for line in f:
#             if line.startswith('__version__'):
#                 return line.split('=')[1].strip().strip("'").strip('"')
# 
# 
# version = read_version()


def read_requirements(file_name):
    with open(file_name, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines()]


setup(
    name='gempy_viewer',
    # version=version,
    packages=find_packages(),
    url='',
    license='EUPL',
    author='Miguel de la Varga', 
    author_email="miguel@terranigma-solutions.com",
    description='Viewer for the geological modeling package GemPy',
    install_requires=read_requirements("requirements.txt"),
    extras_require={
        "opt": read_requirements("optional_requirements.txt"),
        "dev": read_requirements("dev-requirements.txt"),
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Scientific/Engineering :: GIS',
        'Programming Language :: Python :: 3.10'
    ],
    python_requires='>=3.10',
    setup_requires=['setuptools_scm'],
    use_scm_version=True,
)
