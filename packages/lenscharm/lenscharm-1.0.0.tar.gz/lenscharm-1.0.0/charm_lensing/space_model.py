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


from dataclasses import dataclass

from .spaces import Space
from .models import Model, build_hybrid_model


@ dataclass
class SpaceModel:
    space: Space
    light_model: Model | None = None
    convergence_model: Model | None = None


def build_space_model(
        space: Space,
        space_cfg: dict,
        light_extend: bool = False
) -> SpaceModel:

    convergence = build_hybrid_model(
        space.extend(),
        'convergence',
        space_cfg.get('convergence', None),
    )

    light = build_hybrid_model(
        space.extend() if light_extend else space,
        'light',
        space_cfg.get('light', None),
    )

    return SpaceModel(space, light, convergence)
