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


from .parametric_prior import build_parametric_prior
from .parametric_model import read_parametric_model

from nifty8.re import Model
from jax.numpy import array

from numpy.typing import ArrayLike


def build_parametric(
    coords: ArrayLike,
    prefix: str,
    model_config: dict,
    deflection: bool = False,
    full_info: bool = False
) -> Model:
    '''Build a parametric model according to the provided config.

    Parameters
    ----------
    coords : jnp.ndarray
        The coordinates at which the model is evaluated
    prefix: str
        Identifier key for the model
    model_config: dict
        The config dictionary, the keys in the dictionary are the names of the
        parametric model.
        The values provide the prior distribution for the model paramters.
    deflection: bool
        Whether to build a deflection model
    full_info: bool
        If true, return the model, the individual models and associated priors
    '''

    models, priors, ptree = [], [], {}
    for model_name, model_cfg in model_config.items():
        parametric_prefix = '_'.join((prefix, model_name))
        parametric_model = read_parametric_model(
            model_name.split('_')[0].lower())
        parametric_prior = build_parametric_prior(
            parametric_model, parametric_prefix, model_cfg)

        models.append(parametric_model)
        priors.append(parametric_prior)
        ptree.update(parametric_prior.domain)

    model = Model(
        lambda x: array(
            [m(p(x), coords) for m, p in zip(models, priors)]
        ).sum(axis=0),
        domain=ptree
    )

    if deflection:
        model = Model(
            lambda x: array(
                [m.deflection(p(x), coords) for m, p in zip(models, priors)]
            ).sum(axis=0),
            domain=ptree
        )

    if full_info:
        return model, models, priors

    return model
