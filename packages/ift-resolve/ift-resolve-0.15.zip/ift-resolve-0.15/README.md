# resolve

Documentation:
[http://ift.pages.mpcdf.de/resolve](http://ift.pages.mpcdf.de/resolve)

Resolve aims to be a general radio aperature synthesis algorithm.  It is based
on Bayesian principles and formulated in the language of information field
theory.  Its features include single-frequency imaging with either only a
diffuse or a diffuse+point-like sky model as prior, single-channel antenna-based
calibration with a regularization in temporal domain and w-stacking.

Resolve is in beta stage: You are more than welcome to test it and help to make
it applicable.  In the likely case that you encounter bugs, please contact me
via [email](mailto:roth@mpa-garching.mpg.de).

## Requirements

For running the installation script:

- Python version 3.10 or later.
- C++17 capable compiler, e.g. g++ 7 or later.
- pybind11>=2.6
- setuptools

Automatically installed by installation script:

- ducc0
- nifty8
- numpy

Optional dependencies:

- astropy
- pytest, pytest-cov (for testing)
- mpi4py
- python-casacore (for reading measurement sets)
- h5py
- matplotlib
- dask-ms[xarray, zarr] (for reading pfb-clean xds files)
- [jax-finufft](https://github.com/flatironinstitute/jax-finufft) (for using the finufft in jax-resolve)
- [jaxlinop](https://gitlab.mpcdf.mpg.de/mtr/jax_linop) (for using ducc gridder in jax-resolve)

## Installation

For a blueprint how to install resolve, you may look at the [Dockerfile](./Dockerfile).

For installing resolve on a Linux machine, the following steps are necessary.
First install the necessary dependencies, for example via:

    pip3 install --upgrade pybind11 setuptools

Finally, clone the resolve repository and install resolve on your system:

    git clone --recursive https://gitlab.mpcdf.mpg.de/ift/resolve
    cd resolve
    pip install --user .

## Related publications
- Bayesian radio interferometric imaging with direction-dependent calibration ([doi](https://doi.org/10.1051/0004-6361/202346851), [arXiv](https://arxiv.org/abs/2305.05489)).
- Variable structures in M87* from space, time and frequency resolved interferometry ([doi](https://doi.org/10.1038/s41550-021-01548-0), [arXiv](https://arxiv.org/abs/2002.05218)).
- Comparison of classical and Bayesian imaging in radio interferometry ([doi](https://doi.org/10.1051/0004-6361/202039258), [arXiv](https://arxiv.org/abs/2008.11435)).
- Unified radio interferometric calibration and imaging with joint uncertainty quantification ([doi](https://doi.org/10.1051/0004-6361/201935555), [arXiv](https://arxiv.org/abs/1903.11169)).
- Radio imaging with information field theory ([doi](https://doi.org/10.23919/EUSIPCO.2018.8553533), [arXiv](https://arxiv.org/abs/1803.02174v1)).
