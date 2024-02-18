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
from scipy.interpolate import RectBivariateSpline


def source_distortion_ratio(input_source, model_source):
    return 10 * np.log10(np.linalg.norm(input_source) /
                         np.linalg.norm(input_source - model_source))


def chi2(data, model, std):
    return np.nanmean(((data - model)/std)**2)


def percent_inside(x, value):
    return np.sum(np.abs(value) < x)/len(value.flatten())


def shift_and_resize(input, recon, full_info=False, sxsy=None):
    ''' Shifts and resizes the reconstructed image to match the input image.
    This is used for plotting mock data.
    '''
    if input.shape != recon.shape:

        # from charm_lensing.interpolation import build_interpolation, build_xy_jnp

        # from charm_lensing.spaces import get_xycoords
        # from functools import partial

        # length = recon.shape[0]
        # recon_dist = np.array([length/s for s in recon.shape])
        # input_dist = np.array([length/s for s in input.shape])
        # input_xycoords = get_xycoords(input.shape, input_dist)
        # recon_xycoords = get_xycoords(recon.shape, recon_dist)

        # bxy = partial(build_xy_jnp, recon.shape, recon_dist)
        # inter = build_interpolation(bxy, recon_dist)
        # recon = inter(
        #     input_xycoords.reshape(2, -1) - shift,
        #     recon.reshape(-1)
        # ).reshape(input.shape)
        # return recon

        xycoord = np.linspace(0, 1, num=recon.shape[0])
        Recaster = RectBivariateSpline(
            xycoord, xycoord, recon
        )
        xycoordnew = np.linspace(0, 1, num=input.shape[0])
        recon = Recaster(*(xycoordnew,) * 2, grid=True) * (
            recon.shape[0] / input.shape[0]) ** 2

    if sxsy is None:
        # Compute the cross-correlation between the real and reconstruction arrays
        cross_correlation = np.fft.ifft2(
            np.fft.fft2(input).conj() * np.fft.fft2(recon)
        ).real

        # Find the indices where the cross-correlation is maximum
        shift_y, shift_x = np.unravel_index(
            np.argmax(cross_correlation), cross_correlation.shape)

        # Adjust the shifts if they are larger than half of the dimensions
        if shift_x > input.shape[1] // 2:
            shift_x -= input.shape[1]
        if shift_y > input.shape[0] // 2:
            shift_y -= input.shape[0]

        sx, sy = shift_y, shift_x

    else:
        sx, sy = sxsy

    recon = np.roll(recon, (-sx, -sy), axis=(0, 1))

    if full_info:
        return recon, sx, sy
    return recon
