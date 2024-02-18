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
from numpy.typing import ArrayLike


def build_gaussian_likelihood(
        data: ArrayLike,
        std: ArrayLike
):
    if not isinstance(std, float):
        assert data.shape == std.shape

    var = std**2

    return jft.Gaussian(
        data=data,
        noise_cov_inv=lambda x: x/var,
        noise_std_inv=lambda x: x/std
    )


def model_wrap(model, target_domain=None):
    if target_domain is None:
        def wrapper(x):
            out = model(x)
            for x, val in x.items():
                out[x] = val
            return out
    else:
        def wrapper(x):
            out = model(x)
            for key in target_domain.keys():
                out[key] = x[key]
            return out
    return wrapper


def connect_likelihood_to_model(
    likelihood: jft.Likelihood,
    model: jft.Model
) -> jft.Likelihood:

    ldom = likelihood.domain.tree
    tdom = {t: ldom[t] for t in ldom.keys() if t not in model.target.keys()}
    mdom = {t: model.domain[t] for t in model.domain.keys()}
    mdom.update(tdom)

    model_wrapper = model_wrap(model, tdom)

    model = jft.Model(
        lambda x: jft.Vector(model_wrapper(x)),
        domain=jft.Vector(mdom)
    )

    return likelihood.amend(model, domain=model.domain)
