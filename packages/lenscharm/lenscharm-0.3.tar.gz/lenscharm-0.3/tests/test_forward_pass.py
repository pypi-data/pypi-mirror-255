import numpy as np
from charm_lensing.build_lens_system import build_lens_system
from charm_lensing.nifty_connect import update_position

import jax
jax.config.update("jax_platform_name", "cpu")

TEST_FOLDER = './data/charm_lensing_test'


def load_position():
    from os.path import join
    position = np.load(join(TEST_FOLDER, 'position.npy'), allow_pickle=True)
    position = position.item()
    return update_position(position, key_missing_update=True)


def load_field(field_name):
    from os.path import join
    field = np.load(join(TEST_FOLDER, f'{field_name}.npy'))
    return field


position = load_position()
lens_system = build_lens_system(
    dict(
        spaces=dict(
            source_space=dict(
                Npix=[64, 64],
                distance=0.04,
                padding_ratio=1.0
            ),
            lens_space=dict(
                Npix=[128, 128],
                distance=0.1,
                padding_ratio=2.0
            )
        ),

        model=dict(
            source=dict(
                light=dict(
                    mean=dict(
                        gaussian=dict(
                            center=dict(
                                distribution='normal',
                                mean=0.0,
                                sigma=0.2),
                            covariance=dict(
                                distribution='log_normal',
                                mean=0.2,
                                sigma=7e-2),
                            off_diagonal=dict(
                                distribution='normal',
                                mean=0.0,
                                sigma=10.0))
                    ),
                    perturbations=dict(
                        mattern=dict(
                            amplitude=dict(
                                offset_mean=0.0,
                                offset_std=[0.5e+0, 1e-1]),
                            fluctuations=dict(
                                non_parametric_kind='amplitude',
                                renormalize_amplitude=False,
                                scale=[1.5, 0.1],
                                cutoff=[0.22, 0.02],
                                loglogslope=[-4.0, 0.5])))
                )),

            lens=dict(
                poisson_padding=2,
                convergence=dict(
                    mean=dict(
                        piemd=dict(
                            b=dict(
                                distribution='log_normal',
                                mean=1.0,
                                sigma=0.2),
                            rs=dict(
                                distribution='log_normal',
                                mean=0.3,
                                sigma=0.2),
                            center=dict(
                                distribution='normal',
                                mean=0.0,
                                sigma=0.2),
                            q=dict(
                                distribution='uniform',
                                min=1.0,
                                max=2.4),
                            theta=dict(
                                distribution='normal',
                                mean=0.0,
                                sigma=10.0))),
                    perturbations=dict(
                        correlated_field=dict(
                            amplitude=dict(
                                offset_mean=0.0,
                                offset_std=[0.1e-5, 1e-6]),
                            fluctuations=dict(
                                fluctuations=[0.1, 0.05],
                                loglogavgslope=[-5.0, 0.5],
                                flexibility=[0.5, 1.0],
                                asperity=None))),
                    shear=dict(
                        shear=dict(
                            strength=dict(
                                distribution='normal',
                                mean=0.0,
                                sigma=0.07),
                            theta=dict(
                                distribution='normal',
                                mean=0.0,
                                sigma=10.0),
                            center=dict(
                                distribution=None,
                                mean=0.,
                                sigma=0.)
                        ))
                ),

                light=dict(
                    mean=dict(
                        sersic=dict(
                            ie=dict(
                                distribution='log_normal',
                                mean=0.001,
                                sigma=0.0001),
                            re=dict(
                                distribution='log_normal',
                                mean=1.5,
                                sigma=0.25),
                            n=dict(
                                distribution='uniform',
                                min=0.36,
                                max=10.0),
                            center=dict(
                                distribution='normal',
                                mean=0.0,
                                sigma=0.01),
                            q=dict(
                                distribution='uniform',
                                min=0.5,
                                max=10.5),
                            theta=dict(
                                distribution='normal',
                                mean=0.0,
                                sigma=10.0)))
                ),

            )
        )
    ))


def test_kappa():
    kappa_model = lens_system.lens_plane_model.convergence_model.model
    kappa = kappa_model(position)
    kappa_test = load_field('kappa')
    assert np.allclose(kappa, kappa_test)


def test_alpha():
    alpha_model = lens_system.lens_plane_model.convergence_model.deflection()
    alpha = alpha_model(position)
    alpha_test = load_field('alpha')
    assert np.allclose(alpha, alpha_test)


def test_lens_light():
    lens_light_model = lens_system.lens_plane_model.light_model.model
    lens_light = lens_light_model(position)
    lens_light_test = load_field('lens_light')
    assert np.allclose(lens_light, lens_light_test)


def test_source_light():
    source_light_model = lens_system.source_plane_model.light_model.model
    source_light = source_light_model(position)
    source_light_test = load_field('source_light')
    assert np.allclose(source_light, source_light_test)


def test_lensed_light():
    lensed_light_model = lens_system.get_forward_model_full()
    lensed_light = lensed_light_model(position)['sky']
    lensed_light_test = load_field('lensed_light')
    assert np.allclose(lensed_light, lensed_light_test)


def test_lensed_light_parametric():
    lensed_light_model = lens_system.get_forward_model_parametric()
    lensed_light = lensed_light_model(position)['sky']
    lensed_light_test = load_field('lensed_light_parametric')
    assert np.allclose(lensed_light, lensed_light_test)
