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

from numpy.typing import ArrayLike
from typing import Tuple


class Constant:
    prior_keys = (('value', (1,)),)

    def __call__(self, params: Tuple[float], coords: ArrayLike) -> ArrayLike:
        return jnp.full_like(coords[0], params[0])


class ZeroFlux:
    prior_keys = (('mean', (1,)),)

    def __call__(self, params: Tuple[float]) -> ArrayLike:
        return params[0]


class LinearShift:
    prior_keys = (('ax', (1,)), ('ay', (1,)))

    def __call__(self, params: Tuple[float], coords: ArrayLike) -> ArrayLike:
        ax, ay = params
        out0 = jnp.full_like(coords[0], ax)
        out1 = jnp.full_like(coords[1], ay)
        return jnp.array((out0, out1))

    def deflection(self, params: Tuple[float], coords: ArrayLike) -> ArrayLike:
        ax, ay = params
        out0 = jnp.full_like(coords[0], ax)
        out1 = jnp.full_like(coords[1], ay)
        return jnp.array((out0, out1))
