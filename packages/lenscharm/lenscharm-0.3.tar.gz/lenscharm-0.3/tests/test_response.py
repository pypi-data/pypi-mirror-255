from charm_lensing.utils import from_random, full

from charm_lensing.response import (
    build_integration_operator, build_zero_flux)
from charm_lensing.spaces import Space

import numpy as np


def test_integration_operator():
    domain = Space((256, 256), (1, 1))
    target_distances = (2, 2)

    integration_operator = build_integration_operator(
        domain,
        target_distances,
        oversampling=2
    )
    from jax import jit
    j_integration_operator = jit(integration_operator)

    f = np.full(domain.shape, 1.)
    h = j_integration_operator(f)

    assert np.allclose(np.full((128, 128), 4), h)


def test_zero_flux():
    p = {
        'zero_flux': {
            'mean': {
                'distribution': 'normal',
                'mean': 0.1,
                'sigma': 0.01}
        },
        'randim': {
            'distribution': 'uniform',
            'min': 0,
            'max': 1
        }
    }

    ZeroFlux = build_zero_flux('l1', p)
    pos = full(ZeroFlux.domain, 0.0)
    out = ZeroFlux(pos)

    assert np.allclose(out, 0.1)
