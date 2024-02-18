/*
 *  This code is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  This code is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this code; if not, write to the Free Software
 *  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

/* Copyright (C) 2019-2022 Max-Planck-Society
   Author: Martin Reinecke */

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include "ducc0/bindings/pybind_utils.h"
#include "ducc0/nufft/nufft.h"

namespace ducc0 {

namespace detail_pymodule_nufft {

using namespace std;

namespace py = pybind11;

auto None = py::none();

template<typename Tgrid, typename Tcoord> py::array Py2_u2nu(const py::array &grid_,
  const py::array &coord_, bool forward, double epsilon, size_t nthreads,
  py::object &out__, size_t verbosity, double sigma_min, double sigma_max,
  double periodicity, bool fft_order)
  {
  using Tpoints = Tgrid;
  auto coord = to_cmav<Tcoord,2>(coord_);
  auto grid = to_cfmav<complex<Tgrid>>(grid_);
  auto out_ = get_optional_Pyarr<complex<Tpoints>>(out__, {coord.shape(0)});
  auto out = to_vmav<complex<Tpoints>,1>(out_);
  {
  py::gil_scoped_release release;
  u2nu<Tgrid,Tgrid>(coord,grid,forward,epsilon,nthreads,out,verbosity,
                    sigma_min,sigma_max, periodicity, fft_order);
  }
  return move(out_);
  }
py::array Py_u2nu(const py::array &grid,
  const py::array &coord, bool forward, double epsilon, size_t nthreads,
  py::object &out, size_t verbosity, double sigma_min, double sigma_max,
  double periodicity, bool fft_order)
  {
  if (isPyarr<double>(coord))
    {
    if (isPyarr<complex<double>>(grid))
      return Py2_u2nu<double, double>(grid, coord, forward, epsilon, nthreads,
        out, verbosity, sigma_min, sigma_max, periodicity, fft_order);
    else if (isPyarr<complex<float>>(grid))
      return Py2_u2nu<float, double>(grid, coord, forward, epsilon, nthreads,
        out, verbosity, sigma_min, sigma_max, periodicity, fft_order);
    }
  else if (isPyarr<float>(coord))
    {
    if (isPyarr<complex<double>>(grid))
      return Py2_u2nu<double, float>(grid, coord, forward, epsilon, nthreads,
        out, verbosity, sigma_min, sigma_max, periodicity, fft_order);
    else if (isPyarr<complex<float>>(grid))
      return Py2_u2nu<float, float>(grid, coord, forward, epsilon, nthreads,
        out, verbosity, sigma_min, sigma_max, periodicity, fft_order);
    }
  MR_fail("not yet supported");
  }

template<typename Tpoints, typename Tcoord> py::array Py2_nu2u(const py::array &points_,
  const py::array &coord_, bool forward, double epsilon, size_t nthreads,
  py::object &out__, size_t verbosity, double sigma_min, double sigma_max,
  double periodicity, bool fft_order)
  {
  using Tgrid = Tpoints;
  auto coord = to_cmav<Tcoord,2>(coord_);
  auto points = to_cmav<complex<Tpoints>,1>(points_);
  auto out = to_vfmav<complex<Tgrid>>(out__);
  {
  py::gil_scoped_release release;
  nu2u<Tgrid,Tgrid>(coord,points,forward,epsilon,nthreads,out,verbosity,
                    sigma_min,sigma_max, periodicity, fft_order);
  }
  return move(out__);
  }
py::array Py_nu2u(const py::array &points,
  const py::array &coord, bool forward, double epsilon, size_t nthreads,
  py::object &out, size_t verbosity, double sigma_min, double sigma_max,
  double periodicity, bool fft_order)
  {
  if (isPyarr<double>(coord))
    {
    if (isPyarr<complex<double>>(points))
      return Py2_nu2u<double, double>(points, coord, forward, epsilon, nthreads,
        out, verbosity, sigma_min, sigma_max, periodicity, fft_order);
    else if (isPyarr<complex<float>>(points))
      return Py2_nu2u<float, double>(points, coord, forward, epsilon, nthreads,
        out, verbosity, sigma_min, sigma_max, periodicity, fft_order);
    }
  else if (isPyarr<float>(coord))
    {
    if (isPyarr<complex<double>>(points))
      return Py2_nu2u<double, float>(points, coord, forward, epsilon, nthreads,
        out, verbosity, sigma_min, sigma_max, periodicity, fft_order);
    else if (isPyarr<complex<float>>(points))
      return Py2_nu2u<float, float>(points, coord, forward, epsilon, nthreads,
        out, verbosity, sigma_min, sigma_max, periodicity, fft_order);
    }
  MR_fail("not yet supported");
  }

constexpr const char *u2nu_DS = R"""(
Type 2 non-uniform FFT (uniform to non-uniform)

Parameters
----------
grid : numpy.ndarray(1D/2D/3D, dtype=complex)
    the grid of input data
coord : numpy.ndarray((npoints, ndim), dtype=numpy.float32 or numpy.float64)
    the coordinates of the npoints non-uniform points.
    ndim must be the same as grid.ndim
    2pi-periodicity is assumed; the coordinates don't have to lie inside a
    particular interval, but smaller absolute coordinate values help accuracy
forward : bool
    if True, perform the FFT with exponent -1, else +1.
epsilon : float
    desired accuracy
    for single precision inputs, this must be >1e-6, for double precision it
    must be >2e-13
nthreads : int >= 0
    the number of threads to use for the computation
    if 0, use as many threads as there are hardware threads available on the system
out : numpy.ndarray((npoints,), same data type as grid), optional
    if provided, this will be used to store the result
verbosity: int
    0: no console output
    1: some diagnostic console output
sigma_min, sigma_max: float
    minimum and maximum allowed oversampling factors
periodicity: float
    periodicity of the coordinates
fft_order: bool
    if False, grids start with the most negative Fourier node
    if True, grids start with the zero Fourier mode

Returns
-------
numpy.ndarray((npoints,), same data type as grid)
    the computed values at the specified non-uniform grid points.
    Identical to `out` if it was provided
)""";

constexpr const char *nu2u_DS = R"""(
Type 1 non-uniform FFT (non-uniform to uniform)

Parameters
----------
points : numpy.ndarray((npoints,), dtype=numpy.complex)
    The input values at the specified non-uniform grid points
coord : numpy.ndarray((npoints, ndim), dtype=numpy.float32 or numpy.float64)
    the coordinates of the npoints non-uniform points.
    ndim must be the same as out.ndim
    2pi-periodicity is assumed; the coordinates don't have to lie inside a
    particular interval, but smaller absolute coordinate values help accuracy
forward : bool
    if True, perform the FFT with exponent -1, else +1.
epsilon : float
    desired accuracy
    for single precision inputs, this must be >1e-6, for double precision it
    must be >2e-13
nthreads : int >= 0
    the number of threads to use for the computation
    if 0, use as many threads as there are hardware threads available on the system
out : numpy.ndarray(1D/2D/3D, same dtype as points)
    the grid of output data
    Note: this is a mandatory parameter, since its shape defines the grid dimensions!
verbosity: int
    0: no console output
    1: some diagnostic console output
sigma_min, sigma_max: float
    minimum and maximum allowed oversampling factors
    1.2 <= sigma_min < sigma_max <= 2.5
periodicity: float
    periodicity of the coordinates
fft_order: bool
    if False, grids start with the most negative Fourier node
    if True, grids start with the zero Fourier mode

Returns
-------
numpy.ndarray(1D/2D/3D, same dtype as points)
    the computed grid values.
    Identical to `out`.
)""";


void add_nufft(py::module_ &msup)
  {
  using namespace pybind11::literals;
  auto m = msup.def_submodule("nufft");

  m.def("u2nu", &Py_u2nu, u2nu_DS,  py::kw_only(), "grid"_a, "coord"_a,
        "forward"_a, "epsilon"_a, "nthreads"_a=1, "out"_a=None, "verbosity"_a=0,
        "sigma_min"_a=1.2, "sigma_max"_a=2.51, "periodicity"_a=2*pi,
        "fft_order"_a=false);
  m.def("nu2u", &Py_nu2u, nu2u_DS, py::kw_only(), "points"_a, "coord"_a,
        "forward"_a, "epsilon"_a, "nthreads"_a=1, "out"_a=None, "verbosity"_a=0,
        "sigma_min"_a=1.2, "sigma_max"_a=2.51, "periodicity"_a=2*pi,
        "fft_order"_a=false);
  }

}

using detail_pymodule_nufft::add_nufft;

}
