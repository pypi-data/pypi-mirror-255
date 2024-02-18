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


class Shear:
    prior_keys = (('strength', (1,)), ('theta', (1,)), ('center', (2,)))

    def __call__(self, params: Tuple[float], coords: ArrayLike) -> ArrayLike:
        ss, sa, center = params
        xx, yy = coords - center.reshape(2, -1)
        ax = jnp.cos(2*sa)*xx + jnp.sin(2*sa)*yy
        ay = jnp.sin(2*sa)*xx - jnp.cos(2*sa)*yy
        return ss*jnp.array((ax, ay))

    def deflection(self, params: Tuple[float], coords: ArrayLike) -> ArrayLike:
        ss, sa, center = params
        xx, yy = coords - center.reshape(2, -1)
        ax = jnp.cos(2*sa)*xx + jnp.sin(2*sa)*yy
        ay = jnp.sin(2*sa)*xx - jnp.cos(2*sa)*yy
        return ss*jnp.array((ax, ay))
