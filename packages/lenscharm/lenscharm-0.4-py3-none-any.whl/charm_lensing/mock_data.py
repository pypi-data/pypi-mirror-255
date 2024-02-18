# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: Julian Ruestig


import numpy as np
from numpy.typing import ArrayLike
from typing import Any, Optional, Callable

from scipy.interpolate import RectBivariateSpline
from scipy.optimize import brentq

import nifty8 as ift

from charm_lensing.spaces import get_centered_slice
from charm_lensing.spaces import coords
from charm_lensing.utils import load_fits
from charm_lensing.space_model import SpaceModel
from charm_lensing.interpolation import build_linear_interpolation
from charm_lensing.utils import estimate_snr
from charm_lensing.models.parametric_models import (
    read_parametric_model, params_reader)
from charm_lensing.psf_operator import PsfOperator_fft
from charm_lensing.spaces import Space
from charm_lensing.response import build_integration_operator
from charm_lensing.utils import from_random


def reset_random_seed(seed: int):
    """Reset the random seed for both ift and np."""
    ift.random.push_sseq_from_seed(seed)
    np.random.seed(seed)


def hubble_deep_field_loader(config: dict) -> (np.array, tuple[float]):
    '''Loads an Hubble deep field image'''
    source = np.load(config['hubble_path'], allow_pickle=True).item()
    if config['source_id'] is None:
        source_id = np.random.randint(len(source))
    else:
        source_id = int(config['source_id'])
    source = source[source_id]['image']
    source = source / source.max() * config['source_maximum']
    source[source < 0.0] = 0.0
    return source, (config['distance'],) * 2


def fits_loader(config: dict) -> (np.array, tuple[float]):
    '''Loads an fits image'''
    source = load_fits(config['fits_path'])
    source = source / source.max() * config['source_maximum']
    source[source < 0.0] = 0.0
    return source, (config['distance'],) * 2


class ImageSourceSpline:
    def __init__(self, image: np.array, distances: tuple[float]) -> None:
        source_coordinates_0 = coords(image.shape[0], distances[0])
        source_coordinates_1 = coords(image.shape[1], distances[1])
        self.source_model = RectBivariateSpline(
            source_coordinates_0,
            source_coordinates_1,
            image)

    def brightness_point(self, xycoords: np.array) -> np.array:
        return self.source_model(*xycoords, grid=False)


class ImageSourceBilinear:
    def __init__(self, image: np.array, distances: tuple[float]) -> None:
        self.source_space = Space(image.shape, distances)
        self.source = image

    def brightness_point(self, xycoords: np.array) -> np.array:
        model = build_linear_interpolation(
            ('source', self.source_space),
            ('lens', xycoords.reshape(2, -1).shape)
        )
        return model(
            {'source': self.source, 'lens': xycoords.reshape(2, -1)}
        ).reshape(xycoords.shape[1:])


def get_lens_light(lens_space_model: SpaceModel, mock_config: dict, seed: int):
    """ Returns the lens light and the random seed used to generate it.
    The lens light is defined on the extended space, and has units of flux.
    """

    if mock_config['lens_light'] is not None and mock_config['lens_light'].lower() in [
            'self_consistent']:

        # NOTE: Lens light model is defined in flux units
        x_ll = from_random(
            lens_space_model.light_model.model.domain, seed=seed)
        lens_light = lens_space_model.light_model.model(x_ll)

        # NOTE: Lens light is defined on the extended space
        slc_l = get_centered_slice(
            lens_space_model.space.shape, lens_space_model.space.shape)

        return lens_light[slc_l], x_ll
    else:
        return 0, None


def get_lens_mass(lens_space_model: SpaceModel, mock_config: dict, seed: int):
    """Handles the lens type based on the mock configuration."""
    if mock_config['lens_type'].lower() == 'self_consistent':
        x_ld = from_random(
            lens_space_model.convergence_model.deflection().domain, seed=seed)
        lens_convergence = lens_space_model.convergence_model(x_ld)
        lens_deflection = lens_space_model.convergence_model.deflection()(x_ld)
        lens_deflection = lens_deflection.reshape(2, *lens_convergence.shape)
        slc_d = get_centered_slice(
            lens_space_model.space.extend().shape,
            lens_space_model.space.shape,
            coordinates=True)
        slc = get_centered_slice(
            lens_space_model.space.extend().shape,
            lens_space_model.space.shape,
            coordinates=False)
        return lens_convergence[slc], lens_deflection[slc_d], x_ld

    elif mock_config['lens_type'].lower() in ['direct_set', 'direct']:
        direct = mock_config['direct_set']
        mean_models = [
            (read_parametric_model(model_name.lower()),
             params_reader(read_parametric_model(model_name.lower()), model_params))
            for model_name, model_params in direct.items()
        ]
        lens_convergence = np.zeros(lens_space_model.space.shape)
        lens_deflection = np.zeros((2, *lens_space_model.space.shape))
        for model, params in mean_models:
            assert hasattr(model, 'deflection'), \
                f"""Model {model} does not have a deflection field.
            Direct mock set needs to be adjusted"""
            # TODO: Add support for all models

            lens_convergence += model(params, lens_space_model.space.coords())
            lens_deflection += model.deflection(
                params, lens_space_model.space.coords())

        return lens_convergence, lens_deflection, None


def get_source_light_and_projection(
        source_space_model: SpaceModel,
        lens_space_model: float,
        mock_config: dict,
        seed: int,
        y: ArrayLike
):
    """Creates the source light based on the mock configuration."""

    if mock_config['source_light'].lower() in ['self_consistent']:
        x_sl = from_random(
            source_space_model.light_model.model.domain, seed=seed)
        s = source_space_model.light_model(x_sl)
        s_brightness = s / np.prod(source_space_model.space.distances)
        source_evaluater = build_linear_interpolation(
            ('source', source_space_model.space),
            ('points', y.reshape(2, -1).shape)
        )

        tmp_field = ift.makeField(
            source_evaluater.domain,
            {'source': s_brightness, 'points': y.reshape(2, -1)}
        )
        ls = source_evaluater(tmp_field).val
        Ls = ls.reshape(lens_space_model.space.shape) * \
            lens_space_model.space.nifty_domain.dvol

        return s.T, Ls, x_sl  # FIXME: Why is the transpose needed?

    elif mock_config['source_light'].lower() in ['hubble', 'fits']:
        if mock_config['source_light'].lower() == 'hubble':
            source, distances = hubble_deep_field_loader(mock_config['hubble'])
        elif mock_config['source_light'].lower() == 'fits':
            source, distances = fits_loader(mock_config['fits'])

        source_dvol = np.prod(distances)
        source = source / source_dvol
        if mock_config.get('interpolation', 'bilinear').lower() == 'bilinear':
            source_evaluater = ImageSourceBilinear(source, distances)
            print("Using bilinear interpolation")
        elif mock_config.get('interpolation', 'bilinear').lower() == 'spline':
            source_evaluater = ImageSourceSpline(source, distances)
            print("Using spline interpolation")
        else:
            raise ValueError(
                f"Invalid interpolation method: {mock_config.get('interpolation', 'bilinear')}"
            )
        s = source_evaluater.brightness_point(
            source_space_model.space.coords()
        ) * source_space_model.space.nifty_domain.dvol
        s = s.clip(1e-16)
        Ls = source_evaluater.brightness_point(
            y
        ) * lens_space_model.space.nifty_domain.dvol
        return s, Ls, None

    else:
        raise ValueError("Invalid source light configuration")


def create_mock_data(
        lens_space_model: SpaceModel,
        source_space_model: SpaceModel,
        mock_config: dict,
        psf: Optional[ArrayLike] = None,
        seed: int = 42
) -> tuple[Any, int | float | Any, Any, Any]:

    lens_light, x_ll = get_lens_light(lens_space_model, mock_config, seed)

    lens_convergence, lens_deflection, x_ld = get_lens_mass(
        lens_space_model, mock_config, seed)

    y = lens_space_model.space.coords() - lens_deflection
    s, Ls, x_sl = get_source_light_and_projection(
        source_space_model, lens_space_model, mock_config, seed, y)

    # NOTE: Get mock position unless for first_config which is complete None
    mock_pos_list = [x for x in [x_ll, x_ld, x_sl] if x is not None]
    if len(mock_pos_list) > 0:
        mock_pos = mock_pos_list[0]
        for pos in mock_pos_list[1:]:
            mock_pos.update(pos)

        # from functools import reduce
        # mock_pos = reduce(lambda x, y: x.update(y), mock_pos_list)
    else:
        mock_pos = None

    if psf is None:
        lensed_light = Ls
        light_distribution = Ls + lens_light
    else:
        lensed_light = PsfOperator_fft(Ls, psf)
        light_distribution = PsfOperator_fft(Ls + lens_light, psf)

    # Data space can be different from lens space
    data_space = Space(
        mock_config['data_space']['Npix'],
        mock_config['data_space']['distance'],
        space_key='data'
    )
    integration = build_integration_operator(
        lens_space_model.space,
        data_space.nifty_domain.distances)
    lensed_light = integration(lensed_light)
    light_distribution = integration(light_distribution)

    # NOTE: Set noise scale only for the lensed light
    if mock_config.get('SNR', None) is not None:
        noise_scale = noise_scale_for_target_snr(
            lensed_light, mock_config.get('SNR'),
            mock_config.get('mask_criterion'))
    else:
        noise_scale = mock_config.get('noise_scale')

    reset_random_seed(seed)
    d = light_distribution + np.random.normal(0, noise_scale, data_space.shape)

    return s, d, lens_convergence, lens_deflection, mock_pos, noise_scale, Ls


def fun_to_optimize(noise_scale: float, signal: np.ndarray, target_snr: float,
                    mask_criterion: float) -> float:

    estimated_snr = get_average_signal_to_noise(
        signal, noise_scale, mask_criterion=mask_criterion)
    return estimated_snr - target_snr


def old_fun_to_optimize(
    noise_scale: float,
    signal: np.ndarray,
    target_snr: float,
    mask_criterion: float
) -> float:
    noise_realization = np.random.normal(0, noise_scale, signal.shape)
    estimated_snr = estimate_snr(
        signal + noise_realization, noise_scale, mask_criterion=mask_criterion)
    return estimated_snr - target_snr


def noise_scale_for_target_snr(
        data: np.ndarray,
        target_snr: float,
        mask_criterion: float,
        fun: Callable = old_fun_to_optimize
) -> np.ndarray:
    # initial guess for the bounds of noise_scale
    lower_bound = 0.001
    upper_bound = 0.9 * np.sqrt(data.max()/mask_criterion)
    noise_scale = brentq(fun, lower_bound, upper_bound,
                         args=(data, target_snr, mask_criterion))
    return noise_scale


def get_average_signal_to_noise(signal: np.ndarray, noise_scale: float,
                                mask_criterion: float) -> float:
    """
    Calculate the signal-to-noise ratio for the given signal.

    Args:
        signal (np.ndarray): The input signal as a NumPy array.
        noise_scale (float): The scale of the noise.
        mask_criterion (float): The criterion for masking the signal.
        Sets the minimum signal (with respect to the noise) to be
        considered when calculating the average signal-to-noise ratio.

    Returns:
        float: The calculated signal-to-noise ratio.

    Raises:
        ValueError: If no signal is above the mask criterion.
    """
    snr = signal / noise_scale
    mask = snr > mask_criterion * noise_scale
    if mask.sum() == 0:
        raise ValueError("No signal above the mask criterion.")
    return snr[mask].mean()
