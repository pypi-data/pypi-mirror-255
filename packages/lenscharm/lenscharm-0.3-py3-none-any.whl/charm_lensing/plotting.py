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
# Author: Julian Ruestig, Matteo Guardiani


import nifty8 as ift
import numpy as np
from numpy.typing import ArrayLike

import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.patches import Rectangle
import matplotlib.font_manager as fm
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar

from functools import partial

from charm_lensing.build_lens_system import LensSystem
from charm_lensing.analysis_tools import shift_and_resize, source_distortion_ratio
from charm_lensing.models import Model
from charm_lensing.data_loader import MockData, ImageData

from typing import List, Any, Callable, Dict, Optional

import nifty8.re as jft

try:
    from jubik0.library.plot import plot_sample_and_stats
except ImportError:
    plot_sample_and_stats = None

STANDARD_DEVIATIONS = 3
LOG_MIN = 1e-6
MINMAX = 2


def find_best_grid(N):
    """Find the best grid arangement for a given number of panels to plot."""

    from math import ceil, sqrt
    # Initialize variables
    best_X, best_Y, min_overhead = None, None, float('inf')

    # Initial guess for X and Y
    initial_guess = ceil(sqrt(N))

    for X in range(initial_guess, 0, -1):
        Y = ceil(N / X)
        overhead = X * Y - N

        if overhead < min_overhead:
            best_X, best_Y, min_overhead = X, Y, overhead

    return best_X, best_Y


def display_text(ax: plt.Axes, text: Dict, **kwargs):
    '''Display text on plot
    ax: matplotlib axis
    text: dict or str (default: {'s': str, 'color': 'white'})
    kwargs:
    - keyword: str
        options: 'top_left' (default), 'top_right', 'bottom_left', 'bottom_right'
    - x_offset_ticker: float (default: 0)
    - y_offset_ticker: float (default: 0)
    '''
    keyword = kwargs.get('keyword', 'top_left')
    x_offset_ticker = kwargs.get('x_offset_ticker', 0)
    y_offset_ticker = kwargs.get('y_offset_ticker', 0)

    if type(text) is str:
        text = {'s': text, 'color': 'white'}

    if keyword == 'top_left':
        ax.text(x=0.05 + x_offset_ticker*0.05,
                y=0.95 - y_offset_ticker*0.05,
                ha='left',
                va='top',
                transform=ax.transAxes,
                **text)
    elif keyword == 'top_right':
        ax.text(x=0.95 - x_offset_ticker*0.05,
                y=0.95 - y_offset_ticker*0.05,
                ha='right',
                va='top',
                transform=ax.transAxes,
                **text)
    elif keyword == 'bottom_left':
        ax.text(x=0.05 + x_offset_ticker*0.05,
                y=0.05 + y_offset_ticker*0.05,
                ha='left',
                va='bottom',
                transform=ax.transAxes,
                **text)
    elif keyword == 'bottom_right':
        ax.text(x=0.95 - x_offset_ticker*0.05,
                y=0.05 + y_offset_ticker*0.05,
                ha='right',
                va='bottom',
                transform=ax.transAxes,
                **text)
    else:
        raise ValueError(
            "Invalid keyword. Use 'top_left', 'top_right', 'bottom_left', or 'bottom_right'.")


def display_colorbar(ax, im, **kwargs):
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    divider = make_axes_locatable(ax)

    cbar_setting = kwargs.get(
        'cbar_setting', dict(position='right', display=True, label=None))

    if cbar_setting.get('display', False) or kwargs.get('display_cbar', False):
        if cbar_setting['position'] == 'bottom':
            cax = divider.append_axes("bottom", size="5%", pad=0.1)
            orientation = 'horizontal'
            cbar_label = 'bottom'
        elif cbar_setting['position'] == 'top':
            cax = divider.append_axes("top", size="5%", pad=0.1)
            orientation = 'horizontal'
            cbar_label = 'top'
        elif cbar_setting['position'] == 'left':
            cax = divider.append_axes("left", size="5%", pad=0.1)
            orientation = 'vertical'
            cbar_label = 'left'
        elif cbar_setting['position'] == 'right':
            cax = divider.append_axes("right", size="5%", pad=0.1)
            orientation = 'vertical'
            cbar_label = 'right'
        else:
            raise Exception

        bar = plt.colorbar(im, cax=cax, orientation=orientation)
        if orientation == 'horizontal':
            cax.xaxis.set_ticks_position(cbar_label)
            cax.xaxis.set_label_position(cbar_label)
        elif orientation == 'vertical':
            cax.yaxis.set_ticks_position(cbar_label)
            cax.yaxis.set_label_position(cbar_label)
        bar.set_label(cbar_setting.get('label', None))
    else:
        position = cbar_setting.get('position', 'right')
        cax = divider.append_axes(position, size="5%", pad=0.1)
        cax.set_visible(False)


def configer_panel(ax, im, **kwargs):
    '''
    cbar_setting: dict
        display: bool
        label: str
        position: str, options: right (default), left, top, bottom

    scalebar: dict
        display: bool
        size: float
        unit: str (default: '"')

    '''
    # Set Colorbar
    display_colorbar(ax, im, **kwargs)

    # Display image size as scalebar
    scalebar_kwargs = kwargs.get('scalebar', dict(display=False))
    if kwargs.get('display_scalebar', False) or scalebar_kwargs.get('display'):
        size = scalebar_kwargs.get('scale', 1)
        slabel = r'${}{}$'.format(size, scalebar_kwargs.get('unit', '"'))
        font_properties = scalebar_kwargs.get(
            'font_properties', fm.FontProperties(size=8))
        color = scalebar_kwargs.get('color', 'white')
        ax.add_artist(AnchoredSizeBar(
            ax.transData,
            size,
            slabel,
            'lower left',
            pad=0.1,
            color=color,
            frameon=False,
            fontproperties=font_properties,
        ))

    # Set axis limits
    ax.set_xlim(kwargs.get('xlim', None))
    ax.set_ylim(kwargs.get('ylim', None))

    # Display texts
    texts = kwargs.get('text_kwargs', None)
    if isinstance(texts, dict):
        if 's' in kwargs:
            texts['text']['s'] = kwargs['s']
        texts = [texts]
    for text_kwargs in texts:
        display_text(ax, **text_kwargs)

    # Remove ticks and labels
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.set_aspect('equal')


def configure_matplotlib(
        small_size=8,
        medium_size=8,
        big_size=8,
        font='Nimbus Roman',
        usetex=True,
        widths='mnras',  # 'aanda'
):
    '''Configure matplotlib settings.
    Outputs: column_width, text_width, font_properties'''

    font_properties = fm.FontProperties(size=small_size)

    # controls default text sizes
    plt.rc('font', size=small_size, family='Nimbus Roman')
    plt.rc('axes', titlesize=small_size)     # fontsize of the axes title
    plt.rc('axes', labelsize=medium_size)    # fontsize of the x and y labels
    plt.rc('xtick', labelsize=small_size)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=small_size)    # fontsize of the tick labels
    plt.rc('legend', fontsize=small_size)    # legend fontsize
    plt.rc('figure', titlesize=big_size)
    plt.rc('text', usetex=True)

    if widths == 'mnras':
        column_width = 244*1/72
        text_width = 508*1/72
    elif widths == 'aanda':
        column_width = 88 / 25.4  # mm to inch
        text_width = 170 / 25.4  # mm to inch

    return column_width, text_width, font_properties


def row_imshow(
        row: List[Any],  # Subplot axes
        data: List[ArrayLike],
        titles: List[str],
        settings: List[dict]
):
    for ax, datum, title, setting in zip(row, data, titles, settings):
        # ax.set_title(title)
        im = ax.imshow(datum, **setting, interpolation='none')
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.1)
        ax.tick_params(axis='both', which='both', direction='in')
        ax.text(0.95, 0.05, title, transform=ax.transAxes,
                horizontalalignment='right', verticalalignment='bottom',
                color='k', fontsize=10,
                bbox=dict(facecolor='w', edgecolor='none', pad=1.0, alpha=0.8))
        plt.colorbar(im, cax=cax)


def hist_plot(
        ax: plt.Axes,
        data: ArrayLike,
        model: ArrayLike,
        noise: float = 0,
        s: str = 'Lens light',
        xaxis_label: str = 'Input flux [arbitrary  units]',
        yaxis_label: str = 'Model flux [arbitrary  units]',
        min_flux: float = 0.01
):
    d = data.flatten()[data.flatten() > min_flux]
    m = model.flatten()[data.flatten() > min_flux]
    im = ax.hist2d(d, m, bins=100, norm=LogNorm(), cmap='gnuplot2')
    max, min = np.max([d.max(), m.max()]), np.min([d.min(), m.min()])

    xy = np.arange(min, max, 0.1)
    ax.plot(*(xy,)*2, label='y=x', linestyle='-', color='black',
            linewidth=0.5)
    if noise > 0:
        ax.plot(xy, xy+noise, label='y=x', linestyle='--', color='black',
                linewidth=0.5)
        ax.plot(xy, xy-noise, label='y=x', linestyle='--', color='black',
                linewidth=0.5)

    ax.set_xlabel(xaxis_label)
    ax.set_ylabel(yaxis_label)
    ax.set_xlim(min, max)
    ax.set_ylim(min, max)
    ax.tick_params(axis='both', which='both', direction='in')
    text = dict(
        color='black',
        bbox=dict(facecolor='white', edgecolor='none', pad=1.0, alpha=0.5),
        s=s
    )
    display_text(ax, text)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)
    plt.colorbar(im[3], cax=cax)


def parameter_check(model: Model, position: ift.MultiField, ax, color='white'):
    if (model is None) or (position is None):
        return None
    elif (model.parametric() is None):
        return None

    extent = model.space.extend().extent
    top = extent[3]
    left = extent[0]

    _, models, priors = model.parametric(full_info=True)
    itercounter = -1
    for m, prior in zip(models, priors):
        itercounter += 1
        mean_params = prior(position)
        for s, val in zip(m.prior_keys, mean_params):
            itercounter += 1
            symbol = s[0]
            value = ', '.join([f'{v:.2f}' for v in val])
            ax.text(
                left*0.95, top*(0.90 - (itercounter) * 0.1),
                f'{symbol} = {value}', color=color, alpha=0.5,
            )


def add_box(ax, extent, linestyle='-', edgecolor='white'):
    xy = (extent[0], extent[0])
    width = extent[1]-extent[0]
    height = extent[1]-extent[0]
    ax.add_patch(Rectangle(xy=xy,
                           width=width,
                           height=height,
                           linestyle=linestyle,
                           edgecolor=edgecolor,
                           facecolor='none',
                           lw=1))


def mock_data_plot(
        position: Dict[str, ArrayLike],
        output_name_template: Optional[str],
        data: Dict[str, MockData],
        lens_system: LensSystem,
        iteration: int,
        parametric: bool = True,
        log_data: bool = False,
) -> None:

    key = next(iter(data.keys()))
    input_source = data[key].source
    convergence_data = data[key].convergence
    deflection_data = data[key].deflection
    R = data[key].response

    # Calculate the reconstructed source
    source_extent = lens_system.source_plane_model.space.extend().extent
    source_mask = lens_system.source_plane_model.space.get_mask_operator()
    source_mean = source_mask(
        lens_system.source_plane_model.light_model.parametric()(position)
    ).T
    source_perturbations = source_mask(
        lens_system.source_plane_model.light_model.nonparametric()(position)
    ).T
    source_reconstruction = source_mask(
        lens_system.source_plane_model.light_model(position)
    ).T  # FIXME: Why the hell is here a transpose?
    source_reconstruction, sx, sy = shift_and_resize(
        input_source, source_reconstruction, full_info=True)
    source_mean = shift_and_resize(input_source, source_mean, sxsy=(sx, sy))
    source_perturbations = shift_and_resize(
        input_source, source_perturbations, sxsy=(sx, sy))

    lens_light_model = lens_system.get_lens_light()
    deflection_mean = lens_system.lens_plane_model.convergence_model.deflection(
        parametric=True)
    forward_parametric = lens_system.get_forward_model_parametric()

    if parametric:
        convergence_model = lens_system.lens_plane_model.convergence_model.parametric()
        deflection_model = lens_system.lens_plane_model.convergence_model.deflection(
            parametric=True)
        forward_full = lens_system.get_forward_model_parametric()
        forward_source = lens_system.get_forward_model_parametric(
            only_source=True)
    else:
        convergence_model = lens_system.lens_plane_model.convergence_model
        deflection_model = lens_system.lens_plane_model.convergence_model.deflection()
        forward_full = lens_system.get_forward_model_full()
        forward_source = lens_system.get_forward_model_full(only_source=True)

    # Calculate the convergence and deflection field
    lens_mask = lens_system.lens_plane_model.space.get_mask_operator()
    lens_mask_slice = lens_system.lens_plane_model.space.get_mask(
        coordinates=True)
    convergence = lens_mask(convergence_model.model(position))
    convergence_mean = convergence_model.parametric()(position)
    perturbations = convergence_model.nonparametric()
    if perturbations is None or parametric:
        convergence_perturbations = np.ones_like(convergence)
    else:
        convergence_perturbations = perturbations(position)
    deflection = deflection_model.model(position).reshape(
        2, *lens_system.lens_plane_model.space.extend().shape
    )
    deflection_mean = deflection_mean.model(position).reshape(
        2, *lens_system.lens_plane_model.space.extend().shape
    )
    deflection = deflection[lens_mask_slice]
    deflection_mean = deflection_mean[lens_mask_slice]
    convergence_extent = lens_system.lens_plane_model.space.extend().extent

    # Calculate the model data
    # mask_lens = lens_system.lens_plane_model.space.get_mask()
    mask_lens_extent = lens_system.lens_plane_model.space.extent
    data_extent = {key: d.extent() for key, d in data.items()}
    data_model_full = R(forward_full(position))
    data_model_parametric = R(forward_parametric(position))
    source_light_lens = next(iter(forward_source(position).values()))
    source_light_lens = source_light_lens  # [mask_lens]
    if lens_light_model is None:
        first_row = data_model_parametric
        first_row_name = 'Parametric lensed light'
    else:
        first_row = lens_light_model(position)
        first_row_name = 'Lens light (no PSF)'

    fig, axes = plt.subplots(4, 5, figsize=(21, 14))
    row_imshow(
        axes[0],
        [source_mean, source_perturbations, source_reconstruction,
            input_source, input_source-source_reconstruction, ],
        ['Source parametric', 'Source perturbations', 'Source model',
         'Source input', 'Source (input-model)'],
        [*({'origin': 'lower', 'extent': source_extent,
            'vmin': 0, 'vmax': input_source.max()},)*4,
         {'origin': 'lower', 'extent': source_extent, 'cmap': 'RdBu_r',
          'vmin': -MINMAX, 'vmax': MINMAX}],
    )
    parameter_check(
        lens_system.source_plane_model.light_model, position, axes[0, 0])
    parameter_check(
        lens_system.source_plane_model.light_model, data[key].mock_pos,
        axes[0, 3])

    sdr = source_distortion_ratio(input_source, source_reconstruction)
    display_text(axes[0, -1], {
        's': f'SDR = {sdr:.2f}',
        'color': 'black',
        'bbox': {'facecolor': 'white', 'alpha': 0.5, 'edgecolor': 'none'},
    }, keyword='top_right')

    row_imshow(
        axes[1],
        [first_row,
         source_light_lens,
         data_model_full,
         data[key].data_2d,
         (data[key].data_2d-data_model_full)/data[key].noise_2d],
        [first_row_name,
         'Lensed source (no PSF)',
         'R(lens + lensed source)',
         'Data',
         '(data-reconstruction)/std'],
        [{'origin': 'lower', 'extent': data_extent[key]},
         {'origin': 'lower', 'extent': data_extent[key]},
         *({'origin': 'lower', 'extent': data_extent[key],
           'vmax': data[key].data_2d[~data[key].mask].max(),
            'vmin': data[key].data_2d[~data[key].mask].min()},)*2,
         {'origin': 'lower', 'extent': data_extent[key], 'cmap': 'RdBu_r',
         'vmin': -STANDARD_DEVIATIONS, 'vmax': STANDARD_DEVIATIONS}]
    )
    parameter_check(
        lens_system.lens_plane_model.light_model, position, axes[1, 0])

    conv_min = convergence_data[~np.isnan(convergence_data)].min()
    conv_max = convergence_data[~np.isnan(convergence_data)].max()
    if convergence_data.sum() == 0.:
        convergence_data = np.ones_like(convergence)
        conv_min = convergence.min()
        conv_max = convergence.max()
    row_imshow(
        axes[2],
        [convergence_mean,
         convergence_perturbations,
         convergence,
         convergence_data,
         convergence_data - convergence],
        ['Convergence parametric',
         'Convergence perturbations',
         'Convergence model',
         'Convergence data',
         'Convergence (data-model)', ],
        [*({'origin': 'lower',
            'cmap': 'RdYlBu_r',
            'extent': convergence_extent,
            'norm': LogNorm(conv_min, conv_max)},)*2,
         *({'origin': 'lower', 'cmap': 'RdYlBu_r', 'extent': mask_lens_extent,
            'norm': LogNorm(conv_min, conv_max)},)*2,
         {'origin': 'lower', 'cmap': 'RdBu_r', 'extent': mask_lens_extent,
          'vmin': -0.3, 'vmax': 0.3}]
    )
    parameter_check(
        lens_system.lens_plane_model.convergence_model, position, axes[2, 0])
    parameter_check(
        lens_system.lens_plane_model.convergence_model, data[key].mock_pos,
        axes[2, 3])

    defl_min = np.hypot(*deflection_data).min()
    defl_max = np.hypot(*deflection_data).max()
    if np.sum(deflection_data) == 0.:
        deflection_data = np.ones_like(deflection)
        defl_min = np.hypot(*deflection).min()
        defl_max = np.hypot(*deflection).max()

    row_imshow(
        axes[3],
        [np.hypot(*deflection_mean),
         np.hypot(*deflection_mean),
         np.hypot(*deflection),
         np.hypot(*deflection_data),
         np.hypot(*(deflection_data-deflection))],
        ['Deflection parametric',
         'Deflection parametric',
         'Deflection model',
         'Deflection data',
         'Deflection (data-model)'],
        [*({'origin': 'lower', 'extent': mask_lens_extent,
            'vmin': defl_min, 'vmax': defl_max},)*4,
         {'origin': 'lower', 'cmap': 'RdBu_r', 'extent': mask_lens_extent,
          'vmin': -0.3, 'vmax': 0.3}]
    )
    axes[3, 0].cla()

    compare = data[key].Ls if data[key].Ls is not None else data[key].data_2d
    hist_plot(axes[3, 0], compare, data_model_full)

    if output_name_template is None:
        plt.show()
        return None

    output_name = output_name_template.format(iteration=iteration)
    plt.tight_layout()
    plt.savefig(f'{output_name}.png')
    plt.close()


def standard_data_plot(
        position: Dict[str, ArrayLike],
        output_name_template: Optional[str],
        data: Dict[str, ImageData],
        lens_system: LensSystem,
        iteration: int,
        parametric: bool = True,
        log_data: bool = False,
) -> None:

    # Calculate the reconstructed source
    source_reconstruction = lens_system.source_plane_model.light_model(
        position).T  # FIXME: Why is here a transpose?
    source_extent = lens_system.source_plane_model.space.extend().extent

    convergence_model = lens_system.lens_plane_model.convergence_model
    deflection_model = lens_system.lens_plane_model.convergence_model.deflection(
        parametric=parametric)
    lens_light_model = lens_system.get_lens_light()
    if parametric:
        convergence_model = convergence_model.parametric()
        forward = lens_system.get_forward_model_parametric()
        forward_source = lens_system.get_forward_model_parametric(
            only_source=True)
    else:
        forward = lens_system.get_forward_model_full()
        forward_source = lens_system.get_forward_model_full(only_source=True)

    # Calculate the convergence and deflection field
    convergence = convergence_model.model(position)
    perturbations = convergence_model.nonparametric()
    if perturbations is None or parametric is True:
        convergence_perturbations = np.ones_like(convergence)
    else:
        convergence_perturbations = perturbations(position)
    deflection_field = deflection_model.model(position).reshape(
        2, *convergence.shape
    )
    convergence_extent = lens_system.lens_plane_model.space.extend().extent

    # Calculate the model data
    mask_lens_extent = lens_system.lens_plane_model.space.extent
    data_extent = {key: d.extent() for key, d in data.items()}

    sky = forward(position)
    sky.update(position)  # do this to get all parameters of the response model
    lensed_light = forward_source(position)
    lensed_light.update(position)

    if lens_light_model is None:
        lens_light = None
    else:
        lens_light = lens_light_model(position)

    fig, axes = plt.subplots(
        2 + len(data.keys()), 3, figsize=(19, 10 + 5 * len(data.keys()))
    )
    row_imshow(
        axes[0],
        [source_reconstruction, convergence, convergence_perturbations],
        ['Source reconstruction', 'Convergence', 'Convergence perturbations'],
        [{'origin': 'lower', 'extent': source_extent, 'vmin': 0},
         {'origin': 'lower', 'extent': convergence_extent, 'cmap': 'RdYlBu_r',
          'norm': LogNorm()},
         {'origin': 'lower', 'extent': convergence_extent, 'cmap': 'RdYlBu_r',
          'norm': LogNorm()}]
    )
    add_box(axes[0, 1], data_extent[next(iter(data.keys()))])
    add_box(axes[0, 2], data_extent[next(iter(data.keys()))])
    parameter_check(lens_system.source_plane_model.light_model,
                    position, axes[0, 0])
    parameter_check(lens_system.lens_plane_model.convergence_model,
                    position, axes[0, 1])

    if lens_light is None:
        row_imshow(
            axes[1],
            [source_reconstruction,
             lensed_light['sky'],
             np.hypot(*deflection_field)],
            ['Source reconstruction', 'Lensed Light', 'Deflection field'],
            [{'origin': 'lower',
              'extent': source_extent,
              'norm': LogNorm(vmin=np.max((1e-5, source_reconstruction.min())))
              },
             {'origin': 'lower', 'norm': LogNorm() if log_data else None,
              'extent': mask_lens_extent},
             {'origin': 'lower', 'extent': convergence_extent}])
        add_box(axes[1, 2], data_extent[next(iter(data.keys()))])
    else:
        row_imshow(
            axes[1],
            [source_reconstruction, lensed_light['sky'], lens_light],
            ['Source reconstruction', 'Lensed Light', 'Lens Light'],
            [{'origin': 'lower', 'extent': source_extent,
              'norm': LogNorm(vmin=source_reconstruction.max()*1e-3)},
             {'origin': 'lower',  # 'norm': LogNorm() if log_data else None,
              'extent': mask_lens_extent},
             {'origin': 'lower',  'norm': LogNorm() if log_data else None,
              'extent': mask_lens_extent}]
        )

    for ii, key in enumerate(data.keys()):
        data_max = data[key].data_2d[~data[key].mask].max()
        data_min = data[key].data_2d[~data[key].mask].min()
        if log_data:
            data_plot_kwargs = {'origin': 'lower', 'extent': data_extent[key],
                                'norm': LogNorm(vmin=1e-3, vmax=data_max)}
        else:
            data_plot_kwargs = {'origin': 'lower', 'extent': data_extent[key],
                                'vmax': data_max, 'vmin': data_min}

        data_model_noPsf = data[key].response_no_psf(sky)
        data_model_full = data[key].response(sky)

        plot_data = [
            data[key].data_2d,
            data_model_noPsf,
            (data[key].data_2d-data_model_full)/data[key].noise_2d]

        from .analysis_tools import chi2
        chi_2 = chi2(data[key].data_2d, data_model_full, data[key].noise_2d)

        plot_titles = ['Data', 'Model=Ls', f'abs(data-BLs)/std={chi_2:.2f}']
        plot_kwargs = [data_plot_kwargs, data_plot_kwargs,
                       {'origin': 'lower', 'extent': data_extent[key],
                        'cmap': 'RdBu_r', 'vmin': -STANDARD_DEVIATIONS,
                        'vmax': STANDARD_DEVIATIONS}]

        row_imshow(axes[ii+2], plot_data, plot_titles, plot_kwargs)
        if data[key].mask is not None:
            axes[ii+2, 0].contour(data[key].mask, levels=[0.5], colors='w',
                                  extent=data_extent[key])
            axes[ii+2, 2].contour(data[key].mask, levels=[0.5], colors='w',
                                  extent=data_extent[key])

    if output_name_template is None:
        plt.show()
    else:
        output_name = output_name_template.format(iteration=iteration)
        plt.tight_layout()
        plt.savefig(f'{output_name}.png')
        plt.close()


def samples_dictionary_parser(
    samples_config: Dict,
    lens_system: LensSystem,
) -> Dict[str, dict]:

    if samples_config is False:
        return {}

    samples_dict = {}
    for key, val in samples_config.items():
        if key in ['convergence']:
            samples_dict['_'.join(('samples', key))] = {
                'func': lens_system.lens_plane_model.convergence_model,
                'logscale': val['log_scale']}

        if key in ['source']:
            samples_dict['_'.join(('samples', key))] = {
                'func': lens_system.source_plane_model.light_model,
                'logscale': val['log_scale']}

    return samples_dict


def nifty_plotting_wrapper(plot_check: Callable) -> Callable:
    from functools import wraps

    @wraps(plot_check)
    def convert_to_jft_plot(samples: ift.SampleList, kl_iteration: int):
        from .nifty_connect import jft_samples_converter
        mean, _ = samples.sample_stat()
        jft_samples = jft_samples_converter(mean, samples)
        jft_state = jft.OptimizeVIState(nit=kl_iteration, key=42)
        return plot_check(jft_samples, jft_state)

    return convert_to_jft_plot


def plot_check_factory(
        outputdir: str,
        data: Dict,
        cfg: Dict,
        lens_system: LensSystem,
        parametric: bool,
        min_iterations: int = 0,
        operators_samples: Optional[dict] = {},
) -> Callable:

    plotter = partial(
        mock_data_plot if (
            cfg['mock'] or cfg['plotting_options'].get('mock_data', False)
        ) else standard_data_plot,

        output_name_template=f'{outputdir}/KL{{iteration}}' if outputdir is not None else None,
        data=data,
        lens_system=lens_system,
        parametric=parametric,
        log_data=cfg['plotting_options']['log_data']
    )

    def plot_check(samples: jft.Samples,
                   state: jft.OptimizeVIState):
        kl_iteration = state.nit + min_iterations
        print(f'Plotting iteration {kl_iteration} in {outputdir}\n')

        plotter(position=samples.pos.tree, iteration=kl_iteration)
        if operators_samples != {}:
            plot_sample_and_stats(
                output_directory=outputdir,
                operators_dict=operators_samples,
                res_sample_list=samples,
                state=state,
                iteration=kl_iteration,
                log_scale=cfg['plotting_options']['log_data'])

        print("Plotting done")

    return plot_check
