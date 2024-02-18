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


import numpy as np
from nifty8 import RGSpace
from numpy import isscalar, empty, ndarray
from numpy.typing import ArrayLike

from dataclasses import dataclass, field
from typing import Tuple, Callable


def central_mask_operator(domain, target):
    sl = []
    for i in range(len(domain.shape)):
        slStart = int((domain.shape[i] - target.shape[i]) / 2.)
        slStop = slStart + target.shape[i]
        sl.append(slice(slStart, slStop, 1))
    slices = tuple(sl)

    def central_mask(x):
        return x[slices]

    return central_mask


def coords(shape: int, distance: float) -> ArrayLike:
    '''Returns coordinates such that the edge of the array is
    shape/2*distance'''
    halfside = shape/2 * distance
    return np.linspace(-halfside+distance/2, halfside-distance/2, shape)


def get_extent(
        shape: tuple[int],
        distances: tuple[float],
        center: tuple[float] = (0, 0)
) -> tuple[float]:
    assert len(shape) == 2

    if isscalar(distances):
        distances = (float(distances),) * len(shape)
    halfside = np.array(shape)/2 * np.array(distances)

    return ((-halfside[0]+center[0], halfside[0]+center[0]) +
            (-halfside[1]+center[1], halfside[1]+center[1]))


def get_xycoords(shape: tuple[int], distances: tuple[float]) -> ArrayLike:
    assert len(shape) == 2
    if isscalar(distances):
        distances = (float(distances),) * len(shape)
    x_direction = coords(shape[0], distances[0])
    y_direction = coords(shape[1], distances[1])
    return np.array(np.meshgrid(x_direction, y_direction, indexing='xy'))


def get_klcoords(shape: tuple[int], distances: tuple[float]) -> ArrayLike:
    assert len(shape) == 2
    if isscalar(distances):
        distances = (float(distances),) * len(shape)
    kx = [np.fft.fftfreq(shape[i], d=distances[i]) for i in range(len(shape))]
    return np.array(np.meshgrid(kx[1], kx[0]))


def get_centered_slice(
    extended_shape: Tuple[int],
    original_shape: Tuple[int],
    coordinates: bool = False
) -> Tuple[slice]:
    slices = []

    for oshp_dim, eshp_dim in zip(original_shape, extended_shape):
        center = eshp_dim // 2
        half_side = oshp_dim // 2
        start_idx = center - half_side
        end_idx = start_idx + oshp_dim

        # Ensure the indices are within the extended array shape
        start_idx = max(0, min(start_idx, eshp_dim - 1))
        end_idx = max(0, min(end_idx, eshp_dim))

        slices.append(slice(start_idx, end_idx))

    if coordinates:
        slices.insert(0, slice(None))

    return tuple(slices)


@ dataclass
class Space:
    """Represents a regular 2D Cartesian grid.

    Parameters
    ----------
    shape : tuple of int
    distances : tuple of float
    """
    shape: Tuple[int]
    distances: Tuple[float]
    space_key: str = ''
    extend_factor: float = 1.0
    center: ndarray = field(default_factory=lambda: np.array((0., 0.)))
    extent: Tuple[float] = field(init=False)
    nifty_domain: RGSpace = field(init=False)

    def __post_init__(self):
        self.shape = tuple(int(s) for s in self.shape)
        if isscalar(self.distances):
            self.distances = (float(self.distances),) * len(self.shape)
        else:
            tmp = empty(len(self.shape), dtype=float)
            tmp[:] = self.distances
            self.distances = tuple(tmp)

        self.center = np.array(self.center)
        self.extent = get_extent(self.shape, self.distances, self.center)
        self.nifty_domain = RGSpace(self.shape, self.distances)

    def coords(self) -> ndarray:
        return get_xycoords(self.shape, self.distances) + self.center[..., None, None]

    def extend(self, extend=None) -> 'Space':
        """Returns a new Space with the shape extended by the extend_factor."""
        if extend is None:
            extend = self.extend_factor
        extended_shape = tuple(int(s * extend) for s in self.shape)
        return Space(
            extended_shape,
            self.distances,
            self.space_key + '_ext', 1.0,
            self.center
        )

    def get_mask_operator(self) -> Callable[ArrayLike, ArrayLike]:
        return central_mask_operator(
            self.extend().nifty_domain, self.nifty_domain)

    def get_mask(
        self, coordinates: bool = False, as_array: bool = False
    ) -> slice | ArrayLike:

        slice = get_centered_slice(
            self.extend().shape, self.shape, coordinates=coordinates)

        if as_array:
            arr = np.full(
                self.extend().coords().shape if coordinates else
                self.extend().shape,
                False)
            arr[slice] = True
            return arr

        return slice
