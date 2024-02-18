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
from jax import custom_jvp

from typing import Tuple
from numpy.typing import ArrayLike


@custom_jvp
def F(x):
    def bigger(x):
        return (x**2-1)**(-1/2) * jnp.arctan(jnp.sqrt(x**2-1))

    def smaller(x):
        return (1-x**2)**(-1/2) * jnp.arctanh(jnp.sqrt(1-x**2))

    x0 = jnp.where(x > 1, bigger(x), 0)
    x1 = jnp.where(x < 1, smaller(x), 0)
    x2 = jnp.where(x == 1, 1, 0)

    return x0 + x1 + x2


@F.defjvp
def F_jvp(primals, tangents):
    x, = primals
    x_dot, = tangents
    primal_out = F(x)
    tangent_out = jnp.where(x != 1, (1 - x**2 * F(x)) / (x*(x**2 - 1)), 0)
    return primal_out, tangent_out * x_dot


class Nfw:
    prior_keys = (('b', (1,)), ('rs', (1,)), ('center', (2,)),
                  ('theta', (1,)), ('q', (1,)))

    def __call__(self, params: Tuple[float], coords: ArrayLike) -> ArrayLike:
        # convergence field (Keeton 2002 eq. 55)
        b, rs, center, theta, q = params

        x, y = rotation((coords[0]-center[0], coords[1]-center[1]), theta)
        R = jnp.hypot(q*x, y)

        x = R / rs
        return 2*b*(1-F(x))/(x**2-1)


class Cnfw:
    prior_keys = (('b', (1,)), ('rs', (1,)), ('center', (2,)))

    def __call__(self, params: Tuple[float], coords: ArrayLike) -> ArrayLike:
        # convergence field (Keeton 2002 eq. 55)
        b, rs, center = params

        x, y = coords[0]-center[0], coords[1]-center[1]
        R = jnp.hypot(x, y)

        x = R / rs
        return 2*b*(1-F(x))/(x**2-1)

    def deflection(self, params: Tuple[float], coords: ArrayLike) -> ArrayLike:
        # deflection field (Keeton 2002 eq. 56)
        b, rs, center = params

        x, y = coords[0]-center[0], coords[1]-center[1]
        R = jnp.hypot(x, y)
        theta = jnp.arctan2(y, x)

        x = R / rs
        alpha = 4*b*rs*(jnp.log(x/2)+F(x))/x

        sol = alpha * jnp.exp(1j * theta)
        return jnp.array((sol.real, sol.imag))
