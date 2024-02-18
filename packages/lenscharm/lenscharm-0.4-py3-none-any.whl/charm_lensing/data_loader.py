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


from functools import reduce
from typing import Callable, Tuple, Optional, Dict, Union
from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike

import nifty8.re as jft


from .spaces import get_extent, Space
from .space_model import SpaceModel
from .mock_data import create_mock_data
from .utils import load_fits, estimate_snr
from .response import (build_response, load_psf_and_lanczos_shift,
                       build_mask_operator)
from .likelihood import build_gaussian_likelihood
from .nifty_connect import jax_operator


@dataclass
class ImageData:
    data_2d: ArrayLike
    noise_2d: ArrayLike
    mask: ArrayLike
    response: Optional[jft.Model] = None
    response_no_psf: Optional[jft.Model] = None
    pixel_size: float = 1

    def extent(self):
        return get_extent(self.data_2d.shape, self.pixel_size)

    def plot_data(self):
        """Plots source, data, convergence and deflection images."""
        import matplotlib.pyplot as plt

        plot_titles = ['Data', 'Mask', 'Noise']
        plot_data = [
            self.data_2d,
            self.mask,
            self.noise_2d
        ]
        fig, axes = plt.subplots(1, 3)
        for data, title, ax in zip(plot_data, plot_titles, axes.flatten()):
            im = ax.imshow(data, origin='lower')
            fig.colorbar(im, ax=ax)
            ax.set_title(title)
        plt.show()


@dataclass
class MockData:
    source: ArrayLike
    convergence: ArrayLike
    deflection: ArrayLike
    snr: float
    data_2d: ArrayLike
    noise_2d: ArrayLike
    mask: ArrayLike
    response: Optional[jft.Model] = None
    response_no_psf: Optional[jft.Model] = None
    pixel_size: float = 1
    Ls: Optional[ArrayLike] = None
    mock_pos: Optional[Dict[str, ArrayLike]] = None

    def extent(self):
        return get_extent(self.data_2d.shape, self.pixel_size)

    def plot_data(self):
        """Plots source, data, convergence and deflection images."""
        import matplotlib.pyplot as plt

        plot_titles = ['Source', 'Data', 'Convergence', 'Deflection']
        plot_data = [
            self.source,
            self.data_2d,
            self.convergence,
            np.hypot(*self.deflection),
        ]
        fig, axes = plt.subplots(2, 2)
        for data, title, ax in zip(plot_data, plot_titles, axes.flatten()):
            im = ax.imshow(data, origin='lower')
            fig.colorbar(im, ax=ax)
            ax.set_title(f'{title} SnR:{self.snr.mean():.3f}' if
                         title == 'Data' else title)
        plt.show()


def load_mask(data_cfg: dict, data: ArrayLike, noise: ArrayLike) -> ArrayLike:
    """Loads the mask from the configuration file."""
    if data_cfg.get('mask_path', None) is None:
        return np.logical_or(
            np.isnan(data),
            np.isnan(noise))
    else:
        mask = load_fits(data_cfg['mask_path'])
        mask = mask.astype(bool)
        nan_mask = np.logical_or(  # Mask where data or noise is nan
            np.isnan(data),
            np.isnan(noise)
        )
        return np.logical_or(mask, nan_mask)


def load_std(data_cfg: dict, data: ArrayLike) -> Tuple[ArrayLike, float]:
    """Loads the noise from the configuration file."""
    if data_cfg.get('noise_path', None) is None:
        noise_scale = data_cfg['noise_scale']
        return np.full(data.shape, noise_scale)
    else:
        return load_fits(data_cfg['noise_path'])


def load_mock_data(
        cfg_data_mock_config: dict,
        lens_source_model: Tuple[SpaceModel, SpaceModel],
        psf: ArrayLike
) -> MockData:
    """Loads the mock data from the configuration file."""

    lens_plane_model, source_plane_model = lens_source_model

    source, data_2d, convergence, deflection, mock_pos, noise_scale, Ls = \
        create_mock_data(
            lens_plane_model,
            source_plane_model,
            mock_config=cfg_data_mock_config,
            psf=psf,
            seed=cfg_data_mock_config['seed'],
        )

    noise_2d = np.full(data_2d.shape, noise_scale)

    pixel_size = cfg_data_mock_config['data_space']['distance']
    if np.isscalar(pixel_size):
        pixel_size = (float(pixel_size),) * len(data_2d.shape)
    else:
        tmp = np.empty(len(data_2d.shape), dtype=float)
        tmp[:] = pixel_size
        pixel_size = tuple(tmp)

    return MockData(
        data_2d=data_2d,
        noise_2d=noise_2d,
        mask=np.full(data_2d.shape, False),
        source=source,
        convergence=convergence,
        deflection=deflection,
        Ls=Ls,
        snr=estimate_snr(data_2d, noise_2d, mask_criterion=2.0),
        pixel_size=pixel_size,
        mock_pos=mock_pos,
    )


def load_data(
        cfg_data: dict,
) -> Union[ImageData, MockData]:
    '''Load data from file'''

    data_2d = load_fits(cfg_data['data_path'])
    noise_2d = load_std(cfg_data, data_2d)
    mask = load_mask(cfg_data, data_2d, noise_2d)

    pixel_size = cfg_data['pixel_size']
    if np.isscalar(pixel_size):
        pixel_size = (float(pixel_size),) * len(data_2d.shape)
    else:
        tmp = np.empty(len(data_2d.shape), dtype=float)
        tmp[:] = pixel_size
        pixel_size = tuple(tmp)

    # Some tests
    assert data_2d.shape == noise_2d.shape
    assert data_2d.shape == mask.shape

    # Check if source is provided (Birrer)
    if cfg_data.get('source_path', None) is None:
        return ImageData(
            data_2d=data_2d,
            noise_2d=noise_2d,
            mask=mask,
            pixel_size=pixel_size
        )

    source = load_fits(cfg_data['source_path'])
    return MockData(
        data_2d=data_2d,
        noise_2d=noise_2d,
        mask=mask,
        pixel_size=pixel_size,
        source=source,
        convergence=np.zeros_like(data_2d),
        deflection=(np.zeros_like(data_2d),)*2,
        snr=estimate_snr(data_2d, noise_2d, mask_criterion=2.0),
    )


DataLoadingStrategy = Callable[
    [dict,  # cfg
     str,  # domain_key
     Space,  # sky_domain
     Optional[Tuple[SpaceModel, SpaceModel]]  # lens_source_model
     ],
    Tuple[jft.Likelihood, Dict[str, Union[ImageData, MockData]]]
]


def MockDataLoadingStrategy(
        cfg: dict,
        sky_key: str,
        sky_domain: Space,
        lens_source_model: Tuple[SpaceModel, SpaceModel],
        nifty_connect: bool = True
) -> Tuple[jft.Likelihood, Dict[str, MockData]]:

    likelihood_key = 'likelihood_01'
    data_dict = {
        likelihood_key: load_mock_data(
            cfg['data']['mock_config'],
            lens_source_model,
            load_psf_and_lanczos_shift(cfg['data']['files'], sky_domain)[0])
    }

    R, response_no_psf = build_response(
        domain_key=sky_key,
        domain=sky_domain,
        data_pixel_size=data_dict[likelihood_key].pixel_size,
        likelihood_key=likelihood_key,
        likelihood_config=cfg['data']['files']
    )

    mask_array = ~data_dict[likelihood_key].mask
    Mask_d = build_mask_operator(R.target, mask_array)

    likelihood = build_gaussian_likelihood(
        data=data_dict[likelihood_key].data_2d[mask_array],
        std=data_dict[likelihood_key].noise_2d[mask_array],
    )

    likelihood = likelihood.amend(Mask_d)
    likelihood = likelihood.amend(R, domain=R.domain)

    data_dict[likelihood_key].response = R
    data_dict[likelihood_key].response_no_psf = response_no_psf
    data_dict[likelihood_key].mask2data = Mask_d

    if nifty_connect:
        from .nifty_connect import build_gaussian_likelihood as bgl
        Mask_d = jax_operator(Mask_d)
        R = jax_operator(R)
        response_no_psf = jax_operator(response_no_psf)
        likelihood = bgl(
            domain=Mask_d.target,
            data=data_dict[likelihood_key].data_2d[mask_array],
            std=data_dict[likelihood_key].noise_2d[mask_array],
        )
        likelihood = (likelihood @ Mask_d) @ R

    return likelihood, data_dict


def RealDataLoadingStrategy(
        cfg: dict,
        sky_key: str,
        sky_domain: Space,
        nifty_connect: bool = True
) -> Tuple[jft.Likelihood, Dict[str, Union[ImageData, MockData]]]:

    data_dict = {}
    likelihoods = []

    for key in cfg['data']['files']:
        data_dict[key] = load_data(cfg['data']['files'][key])
        R, response_no_psf = build_response(
            domain_key=sky_key,
            domain=sky_domain,
            data_pixel_size=data_dict[key].pixel_size,
            likelihood_key=key,
            likelihood_config=cfg['data']['files'][key])

        # Load mask and Mask operator
        Mask_d = build_mask_operator(R.target, ~data_dict[key].mask)

        likelihood = build_gaussian_likelihood(
            data=data_dict[key].data_2d[~(data_dict[key].mask)],
            std=data_dict[key].noise_2d[~(data_dict[key].mask)]
        )
        # likelihood = (likelihood @ Mask_d) @ R
        likelihood = likelihood.amend(Mask_d)
        likelihood = likelihood.amend(R, domain=R.domain)

        data_dict[key].response = R
        data_dict[key].response_no_psf = response_no_psf
        data_dict[key].mask2data = Mask_d

        if nifty_connect:
            from .nifty_connect import build_gaussian_likelihood as bgl
            Mask_d = jax_operator(Mask_d)
            R = jax_operator(R)
            response_no_psf = jax_operator(response_no_psf)
            likelihood = bgl(
                domain=Mask_d.target,
                data=data_dict[key].data_2d[~(data_dict[key].mask)],
                std=data_dict[key].noise_2d[~(data_dict[key].mask)],
            )
            likelihood = (likelihood @ Mask_d) @ R

        likelihoods.append(likelihood)

    likelihood = reduce(lambda x, y: x + y, likelihoods)

    return likelihood, data_dict
