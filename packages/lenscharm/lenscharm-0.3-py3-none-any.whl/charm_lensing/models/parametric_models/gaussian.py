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


import jax.numpy as jnp

from typing import Tuple
from numpy.typing import ArrayLike


class Gaussian:
    # FIXME : Put in I0
    prior_keys = (('center', (2,)), ('covariance', (2,)),
                  ('off_diagonal', (1,)))

    def __call__(self, params: Tuple[float], coords: ArrayLike) -> ArrayLike:
        center, covariance, off_diagonal = params
        sx, sy = covariance
        theta = off_diagonal

        x, y = coords[0] - center[0], coords[1] - center[1]

        a = jnp.cos(theta)**2/(2*sx**2) + jnp.sin(theta)**2/(2*sy**2)
        b = -jnp.sin(2*theta)/(4*sx**2) + jnp.sin(2*theta)/(4*sy**2)
        c = jnp.sin(theta)**2/(2*sx**2) + jnp.cos(theta)**2/(2*sy**2)

        return jnp.exp(-(a*x**2 + 2*b*x*y + c*y**2))

    # def __call__(self, params: Tuple[float], coords: ArrayLike) -> ArrayLike:
    #     center, covariance, off_diagonal = params
    #     g00, g11 = covariance
    #     g01 = g00*g11*off_diagonal
    #     x, y = coords[0]-center[0], coords[1]-center[1]
    #     det = jnp.abs(g00*g11-g01*g01)
    #     return jnp.exp(-0.5/det * (x**2*g11-x*y*(g01+g01)+y**2*g00))
