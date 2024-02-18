<img src="https://gitlab.com/mmoresco/pylick/-/raw/master/docs/_static/pyLick_logoNB.png" alt="pyLick" width=300px>

**pyLick** is a Python tool designed to measure spectral features, such as Lick indices and D4000, in galaxy spectra. It currently supports over 80 features spanning the near-UV to the near-IR. New ones can be easily introduced. The uncertainties are evaluated using the signal-to-noise method proposed by <a href="https://aas.aanda.org/articles/aas/abs/1998/03/ds1395/ds1395.html">Cardiel et al. (1998)</a>. The code interpolates over bad pixels when a bad pixels mask is provided, allowing users to discard measurements above a specified Bad Pixel Fraction threshold. Additionally, the code includes convenient plotting routines.

[![GitLab](https://img.shields.io/badge/GitLab-mmoresco%2FpyLick-9e8ed7)](https://gitlab.com/mmoresco/pylick)
[![arxiv](https://img.shields.io/badge/arXiv-2106.14894-28bceb)](https://arxiv.org/abs/2106.14894)
[![Documentation Status](https://readthedocs.org/projects/pylick/badge/?version=latest)](https://pylick.readthedocs.io/en/latest/?badge=latest)
[![License](https://img.shields.io/badge/license-GPLv3-fb7e21)](https://gitlab.com/mmoresco/pylick/-/blob/master/LICENSE)
[![Version](https://img.shields.io/gitlab/v/release/14528131)](https://gitlab.com/mmoresco/pylick/-/tags)


## Installation

The code can be quikly installed from [Pypi](https://pypi.org/project/pylick/):

    pip install pylick

For more flexibility, clone the source repository into your working folder and install it locally:

    git clone https://gitlab.com/mmoresco/pylick.git
    cd pylick/
    pip install -e .

To test the installation, run the following command:

    python -c "import pylick; print(pylick.__version__)"


## Documentation 
Read the docs at <a href="https://pylick.readthedocs.io/">pylick.readthedocs.io</a>


## Citation
Please cite the following paper if you find this code useful in your research (<a href="https://ui.adsabs.harvard.edu/abs/2022ApJ...927..164B/abstract">ADS</a>, <a href="https://arxiv.org/abs/2106.14894">arXiv</a>, <a href="https://inspirehep.net/literature/1871797">INSPIRE</a>):

    @ARTICLE{Borghi2022a,
        author = {{Borghi}, Nicola and {Moresco}, Michele and {Cimatti}, Andrea and et al.},
         title = "{Toward a Better Understanding of Cosmic Chronometers: Stellar Population Properties of Passive Galaxies at Intermediate Redshift}",
       journal = {ApJ},
          year = 2022,
         month = mar,
        volume = {927},
         pages = {164},
           doi = {10.3847/1538-4357/ac3240},
        eprint = {2106.14894},
        adsurl = {https://ui.adsabs.harvard.edu/abs/2022ApJ...927..164B},
    }


## The team
+ Main developers:
  + Michele Moresco (michele.moresco@unibo.it)
  + Nicola Borghi (nicola.borghi6@unibo.it)
  + Salvatore Quai (squai@uvic.ca)
+ Contributors:
  + Alexandre Huchet
  + Lucia Pozzetti 
  + Andrea Cimatti
