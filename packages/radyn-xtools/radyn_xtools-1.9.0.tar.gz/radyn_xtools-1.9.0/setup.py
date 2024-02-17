from distutils.core import setup
from pathlib import Path

setup(
    name='radyn_xtools',
    version='1.9.0',
    author='A. F. Kowalski',
    author_email='adam.f.kowalski@colorado.edu',
    packages=['radyn_xtools',],
    package_data = {'':['*.ipynb','*.py', '*.md'],},
    description='some python analysis tools for RADYN grid output',
    long_description_content_type='text/markdown',
    long_description=open('radyn_xtools/README.md').read(),
    install_requires=['notebook','cdflib>=0.4.9',
                      'numpy>=1.25.0', 'plotly>=5.15.0', 'pandas>=2.0.3','astropy>=5.3.1','scipy>=1.11.1','matplotlib>=3.7.2',],
)

# conda create --name your_env_name python=3.11
# python setup.py sdist
# python -m twine upload --repository testpypi dist/*
# pip install -i https://test.pypi.org/simple/ speclab-imXam==3.1.2
# pip uninstall speclab-imXam==3.1.2
#  I neeeded to put the #! crap at the top of any of the scripts=
# put alias for imXam.py -f 

#https://test.pypi.org/project/SpecLab/3.1.3/
#https://test.pypi.org/project/SpecLab/3.1.12/
