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


from numpy.typing import ArrayLike
import nifty8 as ift

from nifty8.re import Model, Vector
from typing import Union

MATERN_KEYS = ['matern', 'mattern', 'matern_field', 'mkf', 'mf']
ZERO_FLUX_KEYS = ['zero_flux', 'zf']


def update_distribution(dictionary):
    if isinstance(dictionary, dict):
        if ('distribution' in dictionary and dictionary['distribution'] == 'uniform'):
            if 'mean' in dictionary:
                dictionary['min'] = float(dictionary.pop('mean'))
            if 'sigma' in dictionary:
                dictionary['max'] = dictionary['min'] + \
                    float(dictionary.pop('sigma'))
        else:
            for key, value in dictionary.items():
                if isinstance(value, str):
                    try:
                        dictionary[key] = float(value)
                    except ValueError:
                        pass
                elif isinstance(value, list):
                    dictionary[key] = [float(item) if isinstance(
                        item, str) else item for item in value]
                elif isinstance(value, dict):
                    update_distribution(value)

                if key in MATERN_KEYS:
                    dictionary[key]['fluctuations']['renormalize_amplitude'] = False
                    dictionary[key]['fluctuations']['non_parametric_kind'] = 'amplitude'

                if key in ZERO_FLUX_KEYS:
                    out = dictionary[key]
                    dictionary[key] = {'mean': out}


def update_position(position, key_missing_update=False):
    from numpy import array
    key_rename = {
        'lens_ext_lens_ext_deflection_shear_strength': 'lens_ext_convergence_shear_strength',
        'lens_ext_lens_ext_deflection_shear_theta': 'lens_ext_convergence_shear_theta',
    }
    key_rename_2 = {
        'zero_flux': 'zero_flux_mean'
    }
    key_missing = {
        'lens_ext_convergence_shear_center': array([0., 0.]),
    }

    jft_position = {}
    for key in position.keys():
        if key in key_rename:
            jft_position[key_rename[key]] = position[key]
        elif '_'.join(key.split('_')[-2:]) in key_rename_2:
            out = '_'.join(
                key.split('_')[:-2] + [key_rename_2['_'.join(key.split('_')[-2:])]])
            jft_position[out] = position[key]
        else:
            jft_position[key] = position[key]

    if key_missing_update:
        for key in key_missing:
            jft_position[key] = key_missing[key]

    return jft_position


def jft_samples_converter(
        mean: Union[dict, ift.MultiField], samples: ift.SampleList):
    from jax.numpy import array
    from nifty8.re import Samples, Vector

    if isinstance(mean, ift.MultiField):
        mean = mean.val

    out = {key: [] for key in update_position(next(samples.iterator())).keys()}
    for s in samples.iterator():
        s = update_position(s.val)
        for key, value in s.items():
            out[key].append(value - mean[key])

    for key, val in out.items():
        out[key] = array(val)

    return Samples(pos=Vector(mean), samples=Vector(out))


def get_nifty_domain(domain: dict):
    if isinstance(domain, Vector):
        domain = domain.tree
    elif not isinstance(domain, dict):
        return ift.UnstructuredDomain(domain.shape)

    out = {}
    for key, val in domain.items():
        out[key] = ift.UnstructuredDomain(val.shape)
    return ift.makeDomain(out)


def jax_operator(op: Model) -> ift.JaxOperator:
    return ift.JaxOperator(
        domain=get_nifty_domain(op.domain),
        target=get_nifty_domain(op.target),
        func=op.__call__)


def build_gaussian_likelihood(
        domain: ift.UnstructuredDomain,
        data: ArrayLike,
        std: ArrayLike
):
    assert domain.shape == data.shape == std.shape

    v = ift.makeField(domain, std**2)
    d = ift.makeField(domain, data)

    N = ift.DiagonalOperator(v, sampling_dtype=float)
    return ift.GaussianEnergy(data=d, inverse_covariance=N.inverse)


class Passer(ift.LinearOperator):
    def __init__(self, domain, target):
        self._domain = domain
        self._target = target
        self._capability = self.TIMES | self.ADJOINT_TIMES

    def apply(self, x, mode):
        self._check_input(x, mode)
        if mode == self.TIMES:
            out = {t: x.val[t] for t in self.target.keys()}
            return ift.makeField(self.target, out)
        out = {t: x.val[t]
               if t in self.target.keys() else 0 for t in self.domain.keys()}
        return ift.makeField(self.domain, out)


def connect_likelihood_to_model(
        likelihood: ift.LikelihoodEnergyOperator, model: Model
) -> ift.LikelihoodEnergyOperator:
    '''Connect a likelihood to a model.'''

    if not isinstance(model, Model):
        raise ValueError('model must be an instance of nifty8.re.Model')
    model = jax_operator(model)

    ldom = likelihood.domain
    if isinstance(ldom, Vector):
        ldom = ldom.tree

    tdom = {t: ldom[t] for t in ldom.keys() if t not in model.target.keys()}
    mdom = {t: model.domain[t] for t in model.domain.keys()}
    mdom.update(tdom)
    passer = Passer(ift.makeDomain(mdom), ift.makeDomain(tdom))

    return likelihood @ (model + passer)
