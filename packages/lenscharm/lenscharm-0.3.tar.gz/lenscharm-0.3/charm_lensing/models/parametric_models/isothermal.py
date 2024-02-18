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


from .rotation import rotation

import jax.numpy as jnp

from typing import Tuple
from numpy.typing import ArrayLike


def piemd_deflection(f, bc, x1, x2):
    fprim = jnp.sqrt(1-f**2)
    b = jnp.sqrt(x1**2 + f**2*x2**2)
    bdx = x1 + 1j * f**2 * x2
    tmp = jnp.sqrt(f)/fprim * (
        jnp.arctanh(fprim*jnp.sqrt(b**2+bc**2)/bdx) -
        jnp.arctanh(fprim*bc/(f*(x1 + 1j*x2)))
    )
    return jnp.array((tmp.real, -tmp.imag))


class Piemd:
    prior_keys = (('b', (1,)), ('rs', (1,)), ('center', (2,)),
                  ('theta', (1,)), ('q', (1,)))

    def __call__(self, params: Tuple[float], coords: ArrayLike) -> ArrayLike:
        b, rs, center, theta, q = params
        x, y = rotation((coords[0]-center[0], coords[1]-center[1]), theta)

        f, bc = 1/q, rs/q
        return b*jnp.sqrt(f)/(2*jnp.sqrt(x**2+f**2*y**2+bc**2))

    def deflection(self, params: Tuple[float], coords: ArrayLike) -> ArrayLike:
        b, rs, center, theta, q = params
        x, y = rotation((coords[0]-center[0], coords[1]-center[1]), theta)

        f, bc = 1/q, rs/q
        return b*jnp.array(rotation(piemd_deflection(f, bc, x, y), -theta))


class Dpie:
    prior_keys = (('b', (1,)), ('rs', (1,)), ('rc', (1,)),
                  ('center', (2,)), ('theta', (1,)), ('q', (1,)))

    def __call__(self, params: Tuple[float], coords: ArrayLike) -> ArrayLike:
        b, rs, rc, center, theta, q = params
        x, y = rotation((coords[0]-center[0], coords[1]-center[1]), theta)

        f, bc_core, bc_cut = 1/q, rs/q, rc/q
        return b*jnp.sqrt(f)*(
            1/(2*jnp.sqrt(x**2 + f**2*y**2 + bc_core**2)) -
            1/(2*jnp.sqrt(x**2 + f**2*y**2 + bc_cut**2))
        )

    def deflection(self, params: Tuple[float], coords: ArrayLike) -> ArrayLike:
        b, rs, rc, center, theta, q = params
        x, y = rotation((coords[0]-center[0], coords[1]-center[1]), theta)

        f, bc_core, bc_cut = 1/q, rs/q, rc/q
        return b*jnp.array(
            rotation(
                piemd_deflection(f, bc_core, x, y) -
                piemd_deflection(f, bc_cut, x, y),
                -theta))


class Pjaffe:
    prior_keys = (('b', (1,)), ('rs', (1,)), ('center', (2,)))

    def __call__(self, params: Tuple[float], coords: ArrayLike) -> ArrayLike:
        b, rs, center = params
        R = jnp.hypot(coords[0]-center[0], coords[1]-center[1])

        return b/2 * (1/R - 1/jnp.sqrt(R**2 + rs**2))

    def deflection(self, params: Tuple[float], coords: ArrayLike) -> ArrayLike:
        b, rs, center = params
        x, y = coords[0]-center[0], coords[1]-center[1]
        return b*jnp.array(
            piemd_deflection(0.9999, 0.0, x, y) -
            piemd_deflection(0.9999, rs, x, y),
        )
