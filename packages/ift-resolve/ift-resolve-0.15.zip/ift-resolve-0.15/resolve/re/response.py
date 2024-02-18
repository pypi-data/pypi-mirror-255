import numpy as np
from jax import numpy as jnp
import nifty8 as ift
from functools import partial


def InterferometryResponse(
    observation, domain, do_wgridding, epsilon, verbosity=0, nthreads=1
):
    import jax_linop
    from ..response import InterferometryResponse

    R_old = InterferometryResponse(
        observation, domain, do_wgridding, epsilon, verbosity, nthreads
    )

    def R(inp, out, state):
        inp = ift.makeField(R_old.domain, inp)
        out[()] = R_old(inp).val

    def Re_T(inp, out, state):
        inp = ift.makeField(R_old.target, inp.conj())
        out[()] = R_old.adjoint(inp).val.conj()

    def R_abstract(shape, dtype, state):
        return R_old.target.shape, np.dtype(np.complex128)

    def R_abstract_T(shape, dtype, state):
        return R_old.domain.shape, np.dtype(np.float64)

    R_jax = jax_linop.get_linear_call(R, Re_T, R_abstract, R_abstract_T)
    return lambda x: R_jax(x)[0]


def InterferometryResponseDucc(
    observation,
    npix_x,
    npix_y,
    pixsizex,
    pixsizey,
    do_wgridding,
    epsilon,
    nthreads=1,
    verbosity=0,
):
    from ducc0.wgridder.experimental import dirty2vis, vis2dirty
    import jax_linop

    vol = pixsizex * pixsizey
    nvis = observation.vis.shape[1]
    _args = {
        "uvw": observation.uvw,
        "freq": observation.freq,
        "pixsize_x": pixsizex,
        "pixsize_y": pixsizey,
        "epsilon": epsilon,
        "do_wgridding": do_wgridding,
        "nthreads": nthreads,
        "flip_v": True,
        "verbosity": verbosity,
    }

    def R(inp, out, state):
        out[()] = dirty2vis(dirty=inp, **_args)

    def Re_T(inp, out, state):
        out[()] = vis2dirty(vis=inp.conj(), npix_x=npix_x, npix_y=npix_y, **_args)

    def R_abstract(shape, dtype, state):
        return (nvis, 1), np.dtype(np.complex128)

    def R_abstract_T(shape, dtype, state):
        return (npix_x, npix_y), np.dtype(np.float64)

    R_jax = jax_linop.get_linear_call(R, Re_T, R_abstract, R_abstract_T)
    return lambda x: vol * jnp.expand_dims(R_jax(x)[0], 0)


def InterferometryResponseFinuFFT(observation, pixsizex, pixsizey, epsilon):
    from jax_finufft import nufft2

    freq = observation.freq
    uvw = observation.uvw
    vol = pixsizex * pixsizey
    speedoflight = 299792458.0

    uvw = np.transpose((uvw[..., None] * freq / speedoflight), (0, 2, 1)).reshape(-1, 3)
    u, v, w = uvw.T

    u_finu = (2 * np.pi * u * pixsizex) % (2 * np.pi)
    v_finu = (-2 * np.pi * v * pixsizey) % (2 * np.pi)

    def apply_finufft(inp, u, v, eps):
        res = vol * nufft2(inp.astype(np.complex128), u, v, eps=eps)
        return jnp.expand_dims(res.reshape(-1, len(freq)), 0)

    R = partial(apply_finufft, u=u_finu, v=v_finu, eps=epsilon)
    return R
