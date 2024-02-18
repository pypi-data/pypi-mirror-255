# SPDX-License-Identifier: GPL-2.0+ OR BSD-2-Clause
# Author: Jakob Roth

from numpy import full
import nifty8.re as jft
import jax
from jax import numpy as jnp


from ..sky_model import _spatial_dom
from ..sky_model import sky_model_points as rve_sky_pts

def build_cf(prefix, conf, shape, dist):
    zmo = conf.getfloat(f"{prefix} zero mode offset")
    zmm = conf.getfloat(f"{prefix} zero mode mean")
    zms = conf.getfloat(f"{prefix} zero mode stddev")
    flum = conf.getfloat(f"{prefix} fluctuations mean")
    flus = conf.getfloat(f"{prefix} fluctuations stddev")
    llam = conf.getfloat(f"{prefix} loglogavgslope mean")
    llas = conf.getfloat(f"{prefix} loglogavgslope stddev")
    flem = conf.getfloat(f"{prefix} flexibility mean")
    fles = conf.getfloat(f"{prefix} flexibility stddev")
    aspm = conf.getfloat(f"{prefix} asperity mean")
    asps = conf.getfloat(f"{prefix} asperity stddev")

    cf_zm = {"offset_mean": zmo, "offset_std": (zmm, zms)}
    cf_fl = {
        "fluctuations": (flum, flus),
        "loglogavgslope": (llam, llas),
        "flexibility": (flem, fles),
        "asperity": (aspm, asps),
        "harmonic_type": "Fourier",
    }
    cfm = jft.CorrelatedFieldMaker(prefix)
    cfm.set_amplitude_total_offset(**cf_zm)
    cfm.add_fluctuations(
        shape, distances=dist, **cf_fl, prefix="", non_parametric_kind='power'
    )
    amps = cfm.get_normalized_amplitudes()
    cfm = cfm.finalize()
    additional = {f"ampliuted of {prefix}": amps}
    return cfm, additional




def sky_model_diffuse(cfg):
    if not cfg["freq mode"] == "single":
        raise NotImplementedError("FIXME: only implemented for single frequency")
    if not cfg["polarization"] == "I":
        raise NotImplementedError("FIXME: only implemented for stokes I")
    sky_dom = _spatial_dom(cfg)
    bg_shape = sky_dom.shape
    bg_distances = sky_dom.distances
    bg_log_diff, additional = build_cf('stokesI diffuse space i0', cfg, bg_shape, bg_distances)
    full_shape = (1,1,1)+bg_shape


    def bg_diffuse(x):
        return jnp.broadcast_to(
            jnp.exp(bg_log_diff(x['stokesI diffuse space i0'])), full_shape
        )


    bg_diffuse_model = jft.Model(
        bg_diffuse,
        domain={'stokesI diffuse space i0': bg_log_diff.domain}
        )

    return bg_diffuse_model, additional

def get_pts_postions(cfg):
    rsp, _ = rve_sky_pts(cfg)
    return rsp._ops[0]._inds[0], rsp._ops[0]._inds[1]

def get_inv_gamma(cfg):
    rsp, _ = rve_sky_pts(cfg)
    return rsp._ops[1].jax_expr

def jax_insert(x, ptsx, ptsy, bg):
    bg = bg.at[:, :, :, ptsx, ptsy].set(x)
    return bg

def sky_model_points(cfg, bg=None):
    if not cfg["freq mode"] == "single":
        raise NotImplementedError("FIXME: only implemented for single frequency")
    if not cfg["polarization"] == "I":
        raise NotImplementedError("FIXME: only implemented for stokes I")

    if not cfg["point sources mode"] == "single":
        raise NotImplementedError(
            "FIXME: point sources only implemented for mode single"
            )
    else:
        sky_dom = _spatial_dom(cfg)
        shp = sky_dom.shape
        full_shp = (1,1,1)+shp
        ptsx, ptsy = get_pts_postions(cfg)
        inv_gamma = get_inv_gamma(cfg)
        pts_shp = (len(ptsx),)
        dom = {'points': jax.ShapeDtypeStruct(pts_shp, dtype=jnp.float64)}
        if bg is None:
            bg = jnp.zeros(full_shp)
            pts_func = lambda x: jax_insert(inv_gamma(x['points']), ptsx=ptsx, ptsy=ptsy, bg=bg)
        else:
            pts_func = lambda x: jax_insert(inv_gamma(x['points']), ptsx=ptsx, ptsy=ptsy, bg=bg(x))
            dom = {**dom, **bg.domain}
    pts_model = jft.Model(pts_func, domain=dom)
    additional = {}
    return pts_model, additional



def sky_model(cfg):
    bg_model, additional_diffuse = sky_model_diffuse(cfg)
    full_sky_model, additional_pts = sky_model_points(cfg, bg_model)
    additional = {**additional_diffuse, **additional_pts}
    return full_sky_model, additional
