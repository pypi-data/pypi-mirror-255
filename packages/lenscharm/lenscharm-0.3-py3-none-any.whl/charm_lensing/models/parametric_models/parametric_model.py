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


from .nfw import Nfw, Cnfw
from .isothermal import Piemd, Dpie, Pjaffe
from .power_law import Spl, Bpl, Cpl
from .gaussian import Gaussian
from .sersic import Sersic
from .shear import Shear
from .exponential_disk import ExponentialDisk
from .linear_models import Constant, ZeroFlux, LinearShift

from typing import Protocol, Tuple
from numpy.typing import ArrayLike


class ParametricModel(Protocol):
    prior_keys: Tuple[Tuple]

    def __call__(self, params: Tuple[float], coords: ArrayLike) -> ArrayLike:
        ...


def read_parametric_model(model_type: str) -> ParametricModel:
    """Convenience function to translate a string into a ParametricModel"""
    mean_models = {
        'nfw': Nfw(),
        'cnfw': Cnfw(),
        'piemd': Piemd(),
        'pie': Piemd(),
        'dpie': Dpie(),
        'pjaffe': Pjaffe(),
        'spl': Spl(),
        'bpl': Bpl(),
        'cpl': Cpl(),
        'gaussian': Gaussian(),
        'sersic': Sersic(),
        'shear': Shear(),
        'exponentialdisk': ExponentialDisk(),
        'constant': Constant(),
        'zero_flux': ZeroFlux(),
        'linearshift': LinearShift(),
    }
    if model_type in mean_models:
        return mean_models[model_type]
    raise NotImplementedError(
        f"Invalid model type '{model_type}', supporting {mean_models.keys()}")


# TODO: This can be used to get rid of the params call and simplify the
# prior_keys code structure
def params_reader(model: ParametricModel, params: dict) -> Tuple[float]:
    """Reads the parameters from a dictionary"""
    return tuple(params[key] for key, _ in model.prior_keys)
