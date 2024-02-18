#!/usr/bin/env python3
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
import jax.numpy as jnp

from .parametric_model import ParametricModel
from typing import Callable, Tuple


def shape_adjust(val, shape):
    if jnp.shape(val) == shape:
        return jnp.array(val)
    else:
        return jnp.full(shape, val)


def ducktape(op, key):
    def keyed_call(x):
        return op(x[key])
    return keyed_call


def build_prior_operator(
        domain_key: str, values: dict, shape: Tuple[int] = (1,)
) -> Callable:

    DISTRIBUTION_MAPPING = {
        'normal': (jft.normal_prior, ['mean', 'sigma']),
        'log_normal': (jft.lognormal_prior, ['mean', 'sigma']),
        'lognormal': (jft.lognormal_prior, ['mean', 'sigma']),
        'uniform': (jft.uniform_prior, ['min', 'max']),
        None: (lambda x: lambda _: x, ['mean'])  # FIXME: Is this correct???
    }

    distribution = values.get('distribution')
    transformation = values.get('transformation', None)

    try:
        prior_function, required_params = DISTRIBUTION_MAPPING[distribution]
        vals = [shape_adjust(values[key], shape) for key in required_params]

    except KeyError as e:
        if distribution not in DISTRIBUTION_MAPPING:
            raise NotImplementedError(
                f"{domain_key}: Prior distribution '{distribution}' is not "
                "implemented. Available distributions: \n"
                f"{list(DISTRIBUTION_MAPPING.keys())}"
            ) from e
        else:
            raise KeyError(
                f"{domain_key}: The distribution '{distribution}' requires the"
                f" keys: {required_params}"
            ) from e

    operator = ducktape(prior_function(*vals), domain_key)

    if transformation is not None:
        trafo = getattr(jnp, transformation)
        return lambda x: trafo(operator(x))

    return operator


def check_prior_keys(model: ParametricModel, prior_dict: dict):
    es = '''Not all required keys are specified in the prior dictionary.
    (required) prior keys: {prior_keys}
    (provided) prior dict: {prior_dict}'''
    for key, _ in model.prior_keys:
        if key not in prior_dict:
            raise ValueError(
                es.format(prior_keys=[key[0] for key in model.prior_keys],
                          prior_dict=prior_dict.keys()))


def build_parametric_prior(
        model: ParametricModel, prefix: str, prior_dict: dict
) -> jft.Model:
    check_prior_keys(model, prior_dict)

    ptree = {}
    funcs = []
    for key, shape in model.prior_keys:
        domain_key = '_'.join((prefix, key))
        ptree[domain_key] = jft.ShapeWithDtype((shape))
        op = build_prior_operator(domain_key, prior_dict[key], shape)
        funcs.append(op)

    if len(funcs) == 1:
        prior_model = funcs[0]
    else:
        def prior_model(x):
            return [op(x) for op in funcs]

    return jft.Model(
        prior_model,
        domain=ptree
    )
