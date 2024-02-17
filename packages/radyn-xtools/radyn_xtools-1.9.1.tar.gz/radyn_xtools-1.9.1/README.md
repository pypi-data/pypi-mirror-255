# radyn_xtools

**radyn-xtools** is a package with some bare-bones Python analysis routines for a grid of M dwarf flare models (Kowalski, Allred, & Carlsson, submitted Feb 2024) calculated with the RADYN code.  The `.fits` files (grid output) can be downloaded through Zenodo.

`conda create --name your_env_name python=3.11`

`pip install radyn-xtools`

(note that's a hyphen b/w radyn and xtools)

See `radyn_xtools_Demo.ipynb` for a demonstration on how to use the tools.  This should be downloaded into `your_env_name/site-packages/radyn_xtools/` folder.  to find it, start python and type:

`import radyn_xtools.radyn_xtools as radx`

`radx`

Note the package name in pip is radyn-xtools but the code is radyn_xtools (hyphen vs. underline)


