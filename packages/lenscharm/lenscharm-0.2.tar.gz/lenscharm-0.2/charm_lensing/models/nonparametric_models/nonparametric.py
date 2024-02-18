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


import nifty8.re as jft
from ...spaces import Space
from jax.numpy import exp


CFM_KEYS = ['cfm', 'cf', 'correlated', 'correlated_field']
MATERN_KEYS = ['matern', 'mattern', 'matern_field', 'mkf', 'mf']


def add_fluctuations_matern(
    space: Space,
    perturbations_maker: jft.CorrelatedFieldMaker,
    sub_cfg: dict
):
    # Modify dict for matten
    fluc_cfg = sub_cfg['fluctuations']
    fluc_cfg['non_parametric_kind'] = fluc_cfg.get(
        'non_parametric_kind', 'amplitude')
    fluc_cfg['renormalize_amplitude'] = fluc_cfg.get(
        'renormalize_amplitude', False)
    perturbations_maker.add_fluctuations_matern(
        space.shape,
        space.distances,
        **fluc_cfg)


def add_fluctuations(
    space: Space,
    perturbations_maker: jft.CorrelatedFieldMaker,
    sub_cfg: dict
):
    fluc_cfg = sub_cfg['fluctuations']
    fluc_cfg['non_parametric_kind'] = fluc_cfg.get(
        'non_parametric_kind', 'power')
    perturbations_maker.add_fluctuations(
        space.shape,
        space.distances,
        **fluc_cfg)


def build_nonparametric(
    space: Space, model_key: str, pert_cfg: dict
) -> jft.Model:

    supported_models = {
        name: add_fluctuations_matern if name in MATERN_KEYS else
        add_fluctuations for name in CFM_KEYS + MATERN_KEYS
    }

    for key in pert_cfg:
        key_lower = key.split('_')[0].lower()
        if key_lower not in supported_models:
            raise NotImplementedError(
                f"Invalid perturbation model '{key_lower}'"
                f", supporting {list(supported_models.keys())}")

        sub_cfg = pert_cfg[key]
        prefix = '_'.join((model_key, key))  # LEVEL_HIGHER ??

        perturbations_maker = jft.CorrelatedFieldMaker(f'{prefix}_')
        supported_models[key_lower](space, perturbations_maker, sub_cfg)
        perturbations_maker.set_amplitude_total_offset(
            **sub_cfg['amplitude'])

    perturbations = perturbations_maker.finalize()
    model = jft.Model(
        lambda x: exp(perturbations(x)),
        domain=perturbations.domain
    )

    return model
