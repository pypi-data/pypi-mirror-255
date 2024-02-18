import pytest

from charm_lensing.models.parametric_models.parametric_prior import (
    build_prior_operator,
    build_parametric_prior,
    shape_adjust,
)

from charm_lensing.models.parametric_models import read_parametric_model


def test_build_prior_operator():
    build_prior_operator('test_01',
                         {'distribution': 'normal',
                          'mean': 1,
                          'sigma': 2}
                         )
    # TODO: need to assert something here, check normal prior

    build_prior_operator('test_02',
                         {'distribution': 'log_normal',
                          'mean': 1,
                          'sigma': 2}
                         )
    # TODO: need to assert something here, check lognormal prior

    build_prior_operator('test_03',
                         {'distribution': 'uniform',
                          'min': 1,
                          'max': 2}
                         )
    # TODO: need to assert something here, check uniform prior

    build_prior_operator('test_03',
                         {'distribution': None,
                          'mean': 1, }
                         )
    # TODO: need to assert something here, check uniform prior

    build_prior_operator('test_04',
                         {'distribution': 'uniform',
                          'min': 1,
                          'max': 2,
                          'transformation': 'log',
                          })
    # TODO: need to assert something here, check log-uniform prior

    with pytest.raises(NotImplementedError):
        build_prior_operator('test_04',
                             {'distribution': 'lonormal',
                              'min': 1,
                              'max': 2})

    with pytest.raises(KeyError):
        build_prior_operator('test_04',
                             {'distribution': 'log_normal',
                              'min': 1,
                              'max': 2})

    out_05 = build_prior_operator('test_05',
                                  {'distribution': 'log_normal',
                                   'mean': 1,
                                   'sigma': 2},
                                  shape=(1, 2, 3))
    assert out_05({'test_05': 1.}).shape == (1, 2, 3)


# Test build_parametric_prior
def test_build_parametric_prior():
    import jax.numpy as jnp

    nfw = read_parametric_model('nfw')
    nfw_prior = {key: {'distribution': 'log_normal',
                       'mean': 1,
                       'sigma': 2} for key, _ in nfw.prior_keys}

    prior = build_parametric_prior(nfw, 'test_01', nfw_prior)
    # TODO: need to assert something here, check normal prior
    pos = {key: jnp.full(prior.domain[key].shape, 0.)
           for key in prior.domain}
    out_01 = prior(pos)

    with pytest.raises(ValueError):
        build_parametric_prior(nfw, 'test_02', {'b': 1})
