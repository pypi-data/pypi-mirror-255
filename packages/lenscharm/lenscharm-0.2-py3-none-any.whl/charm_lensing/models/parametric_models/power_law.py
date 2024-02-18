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


def hyp2f1_series(t, q, r, z, max_terms=10):
    """
    Computes the Hypergeometric function numerically
    according to the recipe in O'Riordan III.
    """

    # U from
    q_ = (1 - q ** 2) / (q ** 2)
    u = 0.5 * (1 - jnp.sqrt(1 - q_ * (r / z) ** 2))
    # First coefficient
    a_n = 1.0
    # Storage for sum
    F = jnp.zeros_like(z, dtype='complex64')

    for n in range(max_terms):
        F += a_n * (u ** n)
        a_n *= ((2 * n) + 4 - (2 * t)) / ((2 * n) + 4 - t)
    return F


class Spl:
    prior_keys = (('b', (1,)), ('t', (1,)), ('center', (2,)),
                  ('theta', (1,)), ('q', (1,)))

    def __call__(self, params: Tuple[float], coords: ArrayLike) -> ArrayLike:
        '''(2-t)/2 (b/r)**t'''
        b, t, center, theta, q = params
        x, y = rotation((coords[0]-center[0], coords[1]-center[1]), theta)
        return ((2 - t) / 2) * (b / jnp.hypot(q*x, y)) ** t

    def deflection(self, params: Tuple[float], coords: ArrayLike) -> ArrayLike:
        b, t, center, theta, q = params
        x, y = rotation((coords[0]-center[0], coords[1]-center[1]), theta)

        z = x + 1j * y
        er = jnp.hypot(q*x, y)

        f1 = (b ** 2) / (q * z)
        f2 = (b / er) ** (t - 2)
        f3 = hyp2f1_series(t, q, er, z)

        # Rotate back into original frame
        sol = (f1 * f2 * f3).conjugate() * jnp.exp(- 1j * theta)
        return jnp.array((sol.real, sol.imag))


class Bpl:
    prior_keys = (('b', (1,)), ('t1', (1,)), ('t2', (1,)), ('rs', (1,)),
                  ('center', (2,)), ('theta', (1,)), ('q', (1,)))

    def __call__(self, params: Tuple[float], coords: ArrayLike) -> ArrayLike:
        kB, t1, t2, rB, center, theta, q = params
        x, y = rotation((coords[0]-center[0], coords[1]-center[1]), theta)

        # Elliptical radius / break radius
        x = jnp.hypot(x*q, y) / rB

        c1 = jnp.where((x < 1), x**(-t1), 0)
        c2 = jnp.where((x >= 1), x**(-t2), 0)
        return kB*(c1 + c2)

    def deflection(self, params: Tuple[float], coords: ArrayLike) -> ArrayLike:
        kB, t1, t2, rB, center, theta, q = params
        x, y = rotation((coords[0]-center[0], coords[1]-center[1]), theta)

        z = (x + 1j * y) * jnp.exp(+1j*theta)

        R = jnp.hypot(z.real*q, z.imag)

        # Factors common to eq. 18 and 19
        factors = 2 * kB * (rB ** 2) / (q * z * (2 - t1))

        # Hypergeometric functions
        F1 = hyp2f1_series(t1, q, R, z, max_terms=10)
        F2 = hyp2f1_series(t1, q, rB, z, max_terms=10)
        F3 = hyp2f1_series(t2, q, R, z, max_terms=10)
        F4 = hyp2f1_series(t2, q, rB, z, max_terms=10)

        x1 = rB/R
        c1 = jnp.where((1/x1 <= 1), F1 * x1**(t1 - 2), 0)
        c2 = jnp.where((1/x1 > 1), (F2 + (2-t1)/(2-t2)
                                    * ((x1**(t2 - 2)) * F3 - F4)), 0)

        sol = (factors * (c1 + c2)).conjugate() * jnp.exp(-1j*theta)
        return jnp.array((sol.real, sol.imag))


class Cpl:
    prior_keys = (('b', (1,)), ('t', (1,)), ('rs', (1,)),
                  ('center', (2,)), ('theta', (1,)), ('q', (1,)))

    def __call__(self, params: Tuple[float], coords: ArrayLike) -> ArrayLike:
        b, t, rs, center, theta, q = params
        x, y = rotation((coords[0]-center[0], coords[1]-center[1]), theta)

        er = jnp.hypot(q*x, y)
        return b * ((2 - t) / 2) / ((er**2 + rs**2)**t)
