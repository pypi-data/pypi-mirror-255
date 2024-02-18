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


from charm_lensing.spaces import Space

import nifty8.re as jft

import jax
import jax.numpy as jnp

from typing import Tuple, Callable
from functools import partial


def build_xy_jnp(dom_shape, dom_dist, sampling_points):
    """Builds the jax array for the xy coordinates."""
    N_dim, N_points = sampling_points.shape

    mg = jnp.mgrid[(slice(0, 2),) * N_dim]
    mg = jnp.array(list(map(jnp.ravel, mg)))
    dist = jnp.array(dom_dist).reshape(-1, 1)
    pos = sampling_points / dist
    excess = pos - jnp.floor(pos)
    pos = jnp.floor(pos).astype(jnp.int64)
    max_index = jnp.array(dom_shape).reshape(-1, 1)

    outside = jnp.any((pos > max_index) + (pos < 0), axis=0)

    data = jnp.zeros((2, len(mg[0]), N_points))
    jj = jnp.zeros((len(mg[0]), N_points), dtype=jnp.int64)

    for i in range(len(mg[0])):
        quadrant = jnp.abs(1 - mg[:, i].reshape(-1, 1) - excess)
        data = data.at[:, i, :].set(quadrant)

        data = jnp.where(outside, 0., data)

        fromi = (pos + mg[:, i].reshape(-1, 1)) % max_index
        jj = jj.at[i, :].set(fromi[0] * dom_shape[0] + fromi[1])

    return jj, data


def forward(ff, val):
    return jnp.sum(ff * val, axis=0)


vmap_forward = jax.vmap(forward, in_axes=(None, 0))


def build_interpolation(
        build_xy: Callable,
        dom_dist: Tuple[float]
) -> Callable:

    @jax.custom_jvp
    def interpolation(position, field):
        jj, quadrants = build_xy(position)
        return forward(field[jj], jnp.prod(quadrants, axis=0))

    @interpolation.defjvp
    def interpolation_jvp(primals, tangents):
        position, field = primals
        position_dot, field_dot = tangents

        jj, quadrants = build_xy(position)
        primal_val = jnp.prod(quadrants, axis=0)
        grad_x_val = quadrants[1] * \
            jnp.array((-1, -1, 1, 1))[..., None] / dom_dist[0]
        grad_y_val = quadrants[0] * \
            jnp.array((-1, 1, -1, 1))[..., None] / dom_dist[1]

        # position
        primal_out, grad_x, grad_y = vmap_forward(
            field[jj], jnp.array((primal_val, grad_x_val, grad_y_val))
        )

        # field
        field_dot = forward(field_dot[jj], primal_val)

        tangent_out = (
            jnp.sum(jnp.array((grad_x, grad_y)) * position_dot, axis=0) +
            field_dot
        )

        return primal_out, tangent_out

    return interpolation


def build_linear_interpolation(
        regular_grid: Tuple[str, Space],
        points: Tuple[str, Tuple[int, int]]
):
    """
    Multilinear interpolation for variable points in an RGSpace

    Parameters
    ----------
    regular_grid: Tuple[str, Space]
        Tuple containing the domain key and the regular grid, 2D space,
        on which to interpolate.
    points: Tuple[str, Tuple[int, int]]
        Tuple containing the domain key of the points to be interpolated
        and their shape.
    """

    rgrid_key, rgrid_dom = regular_grid
    points_key, points_shape = points

    # Checks and balances
    if not isinstance(rgrid_dom, Space):
        raise TypeError
    if len(rgrid_dom.shape) != 2:
        raise TypeError
    if len(points_shape) != 2:
        raise ValueError('Point domain shape length incompatible')
    if points_shape[0] != len(rgrid_dom.shape):
        raise ValueError('Point domain incompatible with RGSpace')

    parameter_tree = {
        rgrid_key: jft.ShapeWithDtype(rgrid_dom.shape),
        points_key: jft.ShapeWithDtype(points_shape)
    }

    # CHECKED: This is doing the correct thing:
    # upper_left is the coordiante of the center of the upper left pixel of
    # the rgrid domain.
    # Consequently, the (interpolated) points which are centered with respect
    # to the image center get shifted in the interpolation by upper_left.
    # This conforms to the convention that the interpolation assumes that the
    # upper left corner of the image is at (0,0).
    upper_left = rgrid_dom.coords()[..., 0, 0]
    upper_left = upper_left[..., None]

    build_xy = partial(
        build_xy_jnp,
        rgrid_dom.shape,
        rgrid_dom.distances)
    inter = jax.jit(build_interpolation(
        build_xy,
        rgrid_dom.distances))

    def interpolation(x):
        return inter(
            x[points_key] - upper_left,
            x[rgrid_key].reshape(-1)
        )

    return jft.Model(
        interpolation,
        domain=parameter_tree
    )


def build_finufft_interpolation(
    regular_grid: Tuple[str, Space],
    points: Tuple[str, Tuple[int, int]]
):
    """
    Build interpolation based on the jax_finufft library for variable points
    in RGSpace

    Parameters
    ----------
    regular_grid: Tuple[str, Space]
        Tuple containing the domain key and the regular grid, 2D space,
        on which to interpolate.
    points: Tuple[str, Tuple[int, int]]
        Tuple containing the domain key of the points to be interpolated
        and their shape.
    """

    rgrid_key, rgrid_dom = regular_grid
    points_key, points_shape = points

    # Checks and balances
    if not isinstance(rgrid_dom, Space):
        raise TypeError
    if len(rgrid_dom.shape) != 2:
        raise TypeError
    if len(points_shape) != 2:
        raise ValueError('Point domain shape length incompatible')
    if points_shape[0] != len(rgrid_dom.shape):
        raise ValueError('Point domain incompatible with RGSpace')

    if rgrid_dom.distances[0] != rgrid_dom.distances[1]:
        raise ValueError('Finufft only supports uniform grids')
    if rgrid_dom.shape[0] != rgrid_dom.shape[1]:
        raise ValueError('Finufft only supports square grids')

    parameter_tree = {
        rgrid_key: jft.ShapeWithDtype(rgrid_dom.shape),
        points_key: jft.ShapeWithDtype(points_shape)
    }

    upper_left = rgrid_dom.coords()[..., 0, 0]
    upper_left = upper_left[..., None]

    rgrid_extent = rgrid_dom.distances[0] * rgrid_dom.shape[0]
    from jax_finufft import nufft2

    # # FIXME: THIS SHOULD BE DONE IN THE MAIN SCRIPT
    # import jax
    # jax.config.update("jax_platform_name", "cpu")

    def finufft_interpolation(pos, field):
        x_finufft = (pos - upper_left) / rgrid_extent * 2 * jnp.pi

        f_field = jnp.fft.ifftshift(jnp.fft.ifft2(field))
        n_field = nufft2(
            f_field, x_finufft[0].reshape(-1), x_finufft[1].reshape(-1)
        )
        return n_field.real

    return jft.Model(
        lambda x: finufft_interpolation(x[points_key], x[rgrid_key]),
        domain=parameter_tree
    )
