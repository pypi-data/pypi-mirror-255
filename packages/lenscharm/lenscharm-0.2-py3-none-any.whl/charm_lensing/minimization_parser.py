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


import nifty8 as ift
from typing import Callable, Union


# Constants
SWITCHES = 'switches'
NAME = 'name'
DELTA_E = 'deltaE'
CONV_LVL = 'convergence_level'
ITER_MIN = 'miniter'
ITER_LIM = 'maxiter'
MINIMIZATION = 'minimization'
SAMPLES = 'samples'
N_SAMPLES = 'n_samples'
MODE = 'mode'
KL_MINI = 'kl_mini'

LINEAR_KEYWORDS = ['linear', 'lin', 'linear_sample', 'linear_resample']


def get_config_value(
        key: str, config: dict, index: int, default=1
) -> Union[int, float]:
    '''Returns a configuration value.
    If the value is a list, returns the value at the specified index.'''
    value = config.get(key, default)
    if isinstance(value, list):
        try:
            return value[index]
        except IndexError:
            return value[-1]
    return value


def get_range_index(
        mini_cfg: dict, iteration: int, total_iterations: int) -> int:
    '''Return the index of the switch-range the iteration is in'''

    switches = mini_cfg.get(SWITCHES, [0])
    switches = switches + [total_iterations]

    def inner(iteration: int, ranges: list) -> int:
        """Return the index of the switch-range the iteration is in"""
        for i in range(len(ranges)-1):
            if ranges[i] <= iteration < ranges[i+1]:
                return i

    return inner(iteration, switches)


def controller_factory(
    mini_cfg: dict, total_iterations: int, prefix: str = ''
) -> Callable[[int], ift.AbsDeltaEnergyController]:
    """Creates a Callable which returns the appropriate
    controller for a given configuration and iteration."""

    def get_controller(iteration: int) -> ift.AbsDeltaEnergyController:

        range_index = get_range_index(mini_cfg, iteration, total_iterations)

        delta_name = '_'.join((prefix, DELTA_E))
        conv_lvl_name = '_'.join((prefix, CONV_LVL))
        iter_lim_name = '_'.join((prefix, ITER_LIM))

        name = get_config_value(NAME, mini_cfg, range_index)
        delta_e = get_config_value(delta_name, mini_cfg, range_index)
        conv_level = get_config_value(conv_lvl_name, mini_cfg, range_index)
        iter_limit = get_config_value(iter_lim_name, mini_cfg, range_index)

        return ift.AbsDeltaEnergyController(
            deltaE=delta_e,
            convergence_level=conv_level,
            iteration_limit=iter_limit,
            # name=name
            name=f'{name}: dE={delta_e:.1e}, cl={conv_level}, il={iter_limit}'
        )

    return get_controller


def n_samples_factory(mini_cfg: dict) -> Callable[[int], int]:
    '''Creates a Callable[iterations] which returns the number of samples.'''

    def n_samples(iteration: int) -> int:
        range_index = get_range_index(
            mini_cfg[SAMPLES], iteration, mini_cfg['n_total_iterations'])
        return get_config_value(N_SAMPLES, mini_cfg[SAMPLES], range_index)

    return n_samples


def sample_type_factory(mini_cfg: dict) -> Callable[[int], str]:
    '''Creates a Callable[iterations] which returns the sample type for
    nifty8.re.'''

    def sample_type(iteration: int) -> str:
        range_index = get_range_index(
            mini_cfg[SAMPLES], iteration, mini_cfg['n_total_iterations'])
        return get_config_value(MODE, mini_cfg[SAMPLES], range_index).lower()

    sample_keywords = [
        "linear_sample",
        "linear_resample",
        "nonlinear_sample",
        "nonlinear_resample",
        "nonlinear_update",
    ]
    etxt = "Unknown sample type: {t} at iteration {ii}, known types: {k}"
    for ii in range(mini_cfg['n_total_iterations']):
        t = sample_type(ii)
        assert t in sample_keywords, etxt.format(t=t, ii=ii, k=sample_keywords)

    return sample_type


def linear_sample_kwargs_factory(
    mini_cfg: dict, prefix: str = 'lin'
) -> Callable[[int], dict]:
    """Creates a Callable[iterations] which returns linear sample kwargs for
    nifty8.re."""

    def lin_kwargs_getter(iteration: int) -> dict:
        range_index = get_range_index(
            mini_cfg[SAMPLES], iteration, mini_cfg['n_total_iterations'])

        delta_name = '_'.join((prefix, DELTA_E))
        miniter_name = '_'.join((prefix, ITER_MIN))
        maxiter_name = '_'.join((prefix, ITER_LIM))

        minit = get_config_value(miniter_name, mini_cfg[SAMPLES], range_index)
        maxit = get_config_value(maxiter_name, mini_cfg[SAMPLES], range_index)
        delta_e = get_config_value(delta_name, mini_cfg[SAMPLES], range_index)

        return dict(
            cg_name=f'{prefix}: dE={delta_e}, mi={minit}, il={maxit}',
            cg_kwargs=dict(
                absdelta=delta_e,
                miniter=minit,
                maxiter=maxit
            ))

    return lin_kwargs_getter


def nonlinear_sample_kwargs_factory(
    mini_cfg: dict, prefix: str = 'nonlin'
) -> Callable[[int], dict]:
    '''Creates a Callable[iterations] which returns nonlinear sample kwargs for
    nifty8.re.'''

    def nonlin_kwargs_getter(iteration: int) -> dict:
        range_index = get_range_index(
            mini_cfg[SAMPLES], iteration, mini_cfg['n_total_iterations'])

        delta_name = '_'.join((prefix, DELTA_E))
        miniter_name = '_'.join((prefix, ITER_MIN))
        maxiter_name = '_'.join((prefix, ITER_LIM))
        minit = get_config_value(miniter_name, mini_cfg[SAMPLES], range_index)
        maxit = get_config_value(maxiter_name, mini_cfg[SAMPLES], range_index)
        delta_e = get_config_value(delta_name, mini_cfg[SAMPLES], range_index)

        cg_delta_name = '_'.join((prefix, 'cg', DELTA_E))
        cg_miniter_name = '_'.join((prefix, 'cg',  ITER_MIN))
        cg_maxiter_name = '_'.join((prefix,  'cg', ITER_LIM))
        cg_delta = get_config_value(
            cg_delta_name, mini_cfg[SAMPLES], range_index, default=None)
        cg_minit = get_config_value(
            cg_miniter_name, mini_cfg[SAMPLES], range_index, default=None)
        cg_maxit = get_config_value(
            cg_maxiter_name, mini_cfg[SAMPLES], range_index, default=None)

        nl_name = f'{prefix}: xtol={delta_e}, mi={minit}, il={maxit}'
        cg_name = f'{prefix}_cg: dE={cg_delta}, mi={cg_minit}, il={cg_maxit}'
        return dict(
            minimize_kwargs=dict(
                name=nl_name,
                xtol=delta_e,
                miniter=minit,
                maxiter=maxit,
                cg_kwargs=dict(
                    name=cg_name,
                    absdelta=cg_delta,
                    miniter=cg_minit,
                    maxiter=cg_maxit
                )))

    return nonlin_kwargs_getter


def kl_kwargs_factory(
        mini_cfg: dict, prefix: str = 'kl'
) -> Callable[[int], dict]:
    '''Creates a Callable[iterations] which returns kl minimization kwargs for
    nifyt8.re.'''

    def kl_kwargs_getter(iteration: int) -> dict:
        range_index = get_range_index(
            mini_cfg[KL_MINI], iteration, mini_cfg['n_total_iterations'])

        delta_name = '_'.join((prefix, DELTA_E))
        miniter_name = '_'.join((prefix, ITER_MIN))
        maxiter_name = '_'.join((prefix, ITER_LIM))
        minit = get_config_value(miniter_name, mini_cfg[KL_MINI], range_index)
        maxit = get_config_value(maxiter_name, mini_cfg[KL_MINI], range_index)
        delta_e = get_config_value(delta_name, mini_cfg[KL_MINI], range_index)

        return dict(
            minimize_kwargs=dict(
                name=f'{prefix}: dE={delta_e}, mi={minit}, il={maxit}',
                absdelta=delta_e,
                miniter=minit,
                maxiter=maxit,
                cg_kwargs=dict(name=f'{prefix}CG')
            ))

    return kl_kwargs_getter


def linear_sampling_factory(
        mini_cfg: dict
) -> Callable[[int], ift.AbsDeltaEnergyController]:
    '''Creates a Callable[iterations] which returns the
    LinearSamplingController.'''
    return controller_factory(
        mini_cfg[SAMPLES], mini_cfg['n_total_iterations'], 'lin')


def nonlinear_sampling_factory(
        mini_cfg: dict, minimizer_algorithm=ift.NewtonCG
) -> Callable[[int], Union[None, ift.NewtonCG]]:
    """Creates a Callable[iterations] which returns the minimizer
    with the AbsDeltaEnergyController."""

    def nonlinear_sampling(iteration: int) -> Union[None, ift.NewtonCG]:
        range_index = get_range_index(
            mini_cfg[SAMPLES], iteration, mini_cfg['n_total_iterations'])
        mode = get_config_value(MODE, mini_cfg[SAMPLES], range_index)

        if mode.lower() in LINEAR_KEYWORDS:
            return None
        else:
            controller = controller_factory(
                mini_cfg[SAMPLES], mini_cfg['n_total_iterations'], 'nonlin')
            return minimizer_algorithm(controller(iteration))

    return nonlinear_sampling


def minimizer_factory(
        mini_cfg: dict, minimizer_algorithm=ift.NewtonCG
) -> Callable[[int], ift.NewtonCG]:
    """Creates a Callable[iterations] which returns the minimizer
    with the appropriate AbsDeltaEnergyController."""

    def minimizer(iteration: int) -> ift.NewtonCG:
        controller = controller_factory(
            mini_cfg[KL_MINI], mini_cfg['n_total_iterations'], 'kl')
        return minimizer_algorithm(controller(iteration))

    return minimizer


def domain_transition(new_domain, sample_list):
    print('*'*80)
    print('Switching to full model')
    print('*'*80)

    mean, _ = sample_list.sample_stat()
    mean_dict_old = mean.to_dict()
    mean_new = ift.from_random(new_domain) * 0.1
    mean_dict_new = mean_new.to_dict()
    for key, val in mean_dict_new.items():
        if key in mean_dict_old:
            mean_dict_new[key] = mean_dict_old[key]

    return ift.MultiField.from_dict(mean_dict_new)
