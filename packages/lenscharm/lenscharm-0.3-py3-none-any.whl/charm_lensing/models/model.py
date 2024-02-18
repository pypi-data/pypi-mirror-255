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


#!/usr/bin/env python3
from dataclasses import dataclass
from typing import Callable, Union, Tuple
from typing_extensions import Self

import nifty8.re as jft


from ..spaces import Space
from ..linear_operators import DeflectionAngle
from .parametric_models import read_parametric_model, build_parametric
from .nonparametric_models import build_nonparametric


MEAN_KEY = 'mean'
PERT_KEY = 'perturbations'
SHEAR_KEY = 'shear'
POISSON_KEY = 'poisson_padding'


@ dataclass
class Model:
    model: jft.Model
    config: dict
    prefix: str
    space: Space

    def parametric(
        self, full_info=False
    ) -> Union[Self, Tuple[Self, jft.Model, jft.Model]]:
        # FIXME: A bit hacky as this assumes that we either have a
        # parametric model, or a hybrid model.
        # I.e. this breaks in case of a nonparametric model

        if self.config.get(MEAN_KEY):
            m, ms, ps = build_parametric(
                self.space.coords(), self.prefix, self.config[MEAN_KEY],
                full_info=True
            )
        else:
            m, ms, ps = build_parametric(
                self.space.coords(), self.prefix, self.config,
                full_info=True
            )
        if full_info:
            return Model(m, self.config, self.prefix, self.space), ms, ps
        return Model(m, self.config, self.prefix, self.space)

    def nonparametric(self) -> Union[Self, Tuple[Self, jft.Model, jft.Model]]:
        if self.config.get(PERT_KEY, None) is None:
            return None
        return Model(
            build_nonparametric(
                self.space, self.prefix, self.config[PERT_KEY]),
            self.config, self.prefix, self.space)

    def deflection(
        self,
        parametric: bool = False,
    ) -> Union[Self, Tuple[Self, jft.Model, jft.Model]]:
        '''Gets the deflection of the model.

        Parameters
        ----------
        parametric : bool
            If True, only the parametric model (and shear) is returned.
        '''

        if parametric and MEAN_KEY in self.config:
            config = self.config[MEAN_KEY]
        else:
            config = self.config

        # All convergence models need to have an analytic deflection
        if check_analytic_deflection(config):
            deflection_conv = build_parametric(
                self.space.coords().reshape(2, -1),
                self.prefix,
                config,
                deflection=True
            )

        else:
            poisson = DeflectionAngle(
                self.space, factor=self.config.get(POISSON_KEY, 2))
            deflection_conv = jft.Model(
                lambda x: poisson(self.model(x)).reshape(2, -1),
                domain=self.domain)

        if self.config.get(SHEAR_KEY):
            shear = build_parametric(
                self.space.coords().reshape(2, -1),
                self.prefix,
                self.config[SHEAR_KEY],
                deflection=True
            )

            ptree = {}
            ptree.update(deflection_conv.domain)
            ptree.update(shear.domain)

            deflection_model = jft.Model(
                lambda x: deflection_conv(x) + shear(x),
                domain=ptree
            )
        else:
            deflection_model = deflection_conv

        return Model(deflection_model, self.config, self.prefix, self.space)

    @property
    def domain(self):
        return self.model.domain

    @property
    def target(self):
        return self.model.target

    def __call__(self, x):
        return self.model(x)


def check_analytic_deflection(convergence_model_config: Model) -> bool:
    if convergence_model_config.get(PERT_KEY, None) is not None:
        return False

    return all(
        hasattr(read_parametric_model(
            model_name.lower().split('_')[0]), 'deflection')
        for model_name in convergence_model_config
    )


BuilderPattern = Callable[[Space, str, dict], Model]


def build_parametric_model(
    space: Space,
    prefix: str,
    model_cfg: dict,
) -> Model:
    '''Build a parametric model according to the provided config.

    Parameters
    ----------
    space : Space
        The space where the model is evaluated
    prefix: str
        Identifier key for the model
    model_cfg: dict
        The config dictionary, the keys in the dictionary are the names of the
        parametric model.
        The values provide the prior distribution for the model paramters.
    '''
    if model_cfg is None:
        return None

    prefix = '_'.join((space.space_key, prefix))
    model = build_parametric(space.coords(), prefix, model_cfg)
    return Model(model, model_cfg, prefix, space)


def build_nonparametric_model(
    space: Space,
    prefix: str,
    model_cfg: dict
) -> Model:
    '''Build a nonparametric model according to the provided config.

    Parameters
    ----------
    space : Space
        The space where the model is evaluated
    prefix: str
        Identifier key for the model
    model_cfg: dict
        The config dictionary, which provides the prior settings of the model.
    '''
    if model_cfg is None:
        return None

    prefix = '_'.join((space.space_key, prefix))
    model = build_nonparametric(space, prefix, model_cfg)
    return Model(model, model_cfg, prefix, space)


# TODO: Change this function to build only a hybrid model.
# It should not decide on its own, this should be taken care of by some other
# function.
def build_hybrid_model(
    space: Space,
    model_key: str,
    model_cfg: dict
) -> Model:
    '''Build a hybrid model according to the provided config.

    Parameters
    ----------
    space : Space
        The space where the model is evaluated
    model_key: str
        Identifier key for the model
    model_cfg: dict
        - 'mean' key provides the prior settings of the mean model.
        - 'perturbations' key provides the prior settings of the nonparametric
            perturbations.
    '''

    if model_cfg is None:
        return None

    prefix = '_'.join((space.space_key, model_key))
    para = build_parametric(space.coords(), prefix, model_cfg[MEAN_KEY])

    if model_cfg.get(PERT_KEY):
        pert = build_nonparametric(space, prefix, model_cfg[PERT_KEY])

        ptree = {}
        for m in [para, pert]:
            ptree.update(m.domain)

        if model_cfg.get('type') in [None, 'multiplication']:
            model = jft.Model(
                lambda x: para(x) * pert(x),
                domain=ptree
            )

        elif model_cfg.get('type') == 'addition':
            model = jft.Model(
                lambda x: para(x) + pert(x),
                domain=ptree
            )

        else:
            raise ValueError(
                f"""Invalid perturbation type '{model_cfg.get('type')}'\n
                (supported: 'multiplication', 'addition')""")

    else:
        model = para

    return Model(model, model_cfg, prefix, space)
