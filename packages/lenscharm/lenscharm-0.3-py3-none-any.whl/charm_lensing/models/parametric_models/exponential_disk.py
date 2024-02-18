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


class ExponentialDisk:
    prior_keys = (('ie', (1,)), ('re', (1,)), ('center', (2,)),
                  ('theta', (1,)), ('q', (1,)))

    def __call__(self, params: Tuple[float], coords: ArrayLike) -> ArrayLike:
        ie, re, center, theta, q = params
        x, y = rotation((coords[0]-center[0], coords[1]-center[1]), theta)

        r = jnp.sqrt(q**2 * x**2 + y**2)
        return ie * jnp.exp(-r / re)
