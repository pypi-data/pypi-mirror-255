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
import yaml

from os.path import join

import jax.numpy as jnp

from nifty8 import ResidualSampleList
from scipy.stats import multivariate_normal
from astropy.io import fits
from astropy.io.fits.hdu.image import ImageHDU

from charm_lensing.psf_operator import PsfOperator_fft

from numpy.typing import ArrayLike
from typing import Dict, Union

from nifty8.re import ShapeWithDtype, Vector


def chain_model_domains(*model_domains):
    ptree = {}
    for model_keys in model_domains:
        for key, val in model_keys.items():
            if key in ptree:
                raise Warning('Duplicate model key: {}'.format(key))
            ptree.update({key: val})
    return ptree


def full(domain: Union[Dict[str, ShapeWithDtype], Vector], value: float):
    if isinstance(domain, Vector):
        domain = domain.tree

    out = {}
    for key, s in domain.items():
        out.update({key: jnp.full(s.shape, value)})
    return out


def from_random(
    domain: Union[Dict[str, ShapeWithDtype], Vector],
    seed: int = 42
):
    if isinstance(domain, Vector):
        domain = domain.tree

    from jax import random
    from nifty8.re import random_like
    key, subkey = random.split(random.PRNGKey(seed))
    return random_like(subkey, domain)


def unite_dict(a: dict, b: dict) -> dict:
    '''Returns: union of a and b'''
    tmp = {}
    tmp.update(a)
    tmp.update(b)
    return tmp


def save_fits(data, name):
    hdu = fits.PrimaryHDU(data)
    hdul = fits.HDUList([hdu])
    if name.split('.')[-1] == 'fits':
        hdul.writeto(name, overwrite=True)
    else:
        hdul.writeto(name+'.fits', overwrite=True)


def load_fits(path_to_file, fits_number=0, get_header=False):
    with fits.open(path_to_file) as hdul:
        headers = [h.header for h in hdul if isinstance(h, ImageHDU)]
        datas = [h.data for h in hdul if isinstance(h, ImageHDU)]
        if len(headers) == 0:
            header = hdul[0].header
            data = hdul[0].data
        else:
            header = headers[fits_number]
            data = datas[fits_number]
    if get_header:
        return np.array(data).astype(np.float64), header
    return np.array(data).astype(np.float64)


def reconstruction_loader(
        reconstruction_path: str,
):
    '''
    Load mean, samples and necessery objects from reconstruction_path/pickle.
    '''
    # TODO load config also for the mean and samples for nifyt8.re
    mean = ResidualSampleList.load_mean(
        join(reconstruction_path, 'pickle', 'last'))
    samples = ResidualSampleList.load(
        join(reconstruction_path, 'pickle', 'last'))

    # load config
    with open(join(reconstruction_path, 'config.yaml'), 'r') as file:
        cfg = yaml.safe_load(file)

    return mean, samples, cfg


def lognormal_pdf_display(mean, std):
    from nifty8 import LognormalTransform, from_random
    lognorm = LognormalTransform(mean, std, 'test', 1000)
    test = lognorm(from_random(lognorm.domain)).val
    mean, std = test.mean(), test.std()

    from matplotlib.pyplot import subplots, show, title
    fig, ax = subplots()
    ax.hist(test)
    ax.axvline(mean, color='red')
    ax.axvline(mean+std, color='black', linestyle='dashed')
    ax.axvline(mean-std, color='black', linestyle='dashed')
    title(f'mean: {mean:.2f}, std: {std:.2f}')
    show()


smoother = multivariate_normal.pdf(
    np.array(np.meshgrid(*(np.arange(-10, 10, 1),)*2)).T,
    mean=(0, 0),
    cov=2*np.eye(2)
)
smoother = smoother/smoother.sum()


def estimate_snr(data: ArrayLike, noise_scale: float, mask_criterion: float) -> float:
    snr_mask = PsfOperator_fft(data, smoother) > mask_criterion * noise_scale
    return data[snr_mask].sum() / (noise_scale * np.sqrt(snr_mask.sum()))
