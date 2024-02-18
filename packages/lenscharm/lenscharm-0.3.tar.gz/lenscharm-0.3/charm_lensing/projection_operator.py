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
# Author: Julian Ruestig, Matteo Guardiani


import nifty8.re as jft
from .spaces import Space
from .interpolation import (
    build_linear_interpolation, build_finufft_interpolation)


def build_projection_operator(
        lens_space: Space, source_space: Space, interpolation='bilinear'
) -> jft.Model:
    # Lens equation / Ray casting
    lens_coords_slice = lens_space.get_mask(
        coordinates=True, as_array=True).reshape(2, -1)
    lens_xycoords = lens_space.coords().reshape(2, -1)

    def lens_equation(alpha): return (
        lens_xycoords - alpha[lens_coords_slice].reshape(2, -1)
    )

    if interpolation == 'bilinear':
        print("Using bilinear interpolation")
        ray_trace = build_linear_interpolation(
            ('source', source_space.extend()),
            ('lens', lens_xycoords.shape))
    elif interpolation == 'finufft':
        print("Using finufft interpolation")
        ray_trace = build_finufft_interpolation(
            ('source', source_space.extend()),
            ('lens', lens_xycoords.shape))
    else:
        raise NotImplementedError

    # The lens projection conserves surface brightness, so we
    # 1) devide the source flux by the volume -> surface brightness
    # 2) multiply the lensed surface brightness by the lens volume -> flux
    flux_source_vol = source_space.nifty_domain.dvol
    flux_lens_vol = lens_space.nifty_domain.dvol
    flux_ratio = flux_lens_vol / flux_source_vol

    ptree = {
        'deflection': jft.ShapeWithDtype(lens_coords_slice.shape),
        'source': jft.ShapeWithDtype(source_space.extend().shape)
    }

    return jft.Model(
        lambda x: ray_trace(
            {'lens': lens_equation(x['deflection']),
             'source': x['source']}
        ).reshape(lens_space.shape) * flux_ratio,
        domain=ptree
    )
