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


import jax.numpy as jnp

from charm_lensing.spaces import Space, get_klcoords
from numpy import array


class FFTOperator():
    def __init__(self, domain):
        self.domain = domain

    def times(self, field):
        return jnp.fft.fft2(field)

    def inverse(self, field):
        return jnp.fft.ifft2(field)


class ZeroPadder():
    def __init__(self, domain, factor):
        self.domain = domain
        self.target = Space(array(domain.shape)*factor, domain.distances)
        self._zeros = jnp.zeros(self.target.shape)
        self._slice = slice(0, domain.shape[0]), slice(0, domain.shape[1])

    def times(self, field):
        return self._zeros.at[self._slice].set(field)

    def adjoint(self, field):
        return field[self._slice]

    def __repr__(self):
        return 'ZeroPadder: \n domain={} \n target={}'.format(
            self.domain, self.target)


class DeflectionAngle():
    def __init__(self, domain, factor=4):
        self.domain = (domain.shape, domain.distances)
        self.target = ((2,)+domain.shape, domain.distances)

        self.Zp = ZeroPadder(domain, factor)
        self.FFT = FFTOperator(self.Zp.target)
        self.greenskernel = self.deflection_greens_kernel(
            get_klcoords(self.Zp.target.shape, self.Zp.target.distances))

    def __repr__(self):
        return 'domain: {}\ntarget: {}'.format(self.domain, self.target)

    @staticmethod
    def deflection_greens_kernel(kl_coords):
        '''Returns greens-kernel field in Fourier domain'''
        k_square = array(kl_coords[0]**2 + kl_coords[1]**2)
        k_square[0, 0] = 1
        return -1j*kl_coords/(jnp.pi*k_square)

    def deflection_field(self, field):
        tmp = self.FFT.times(self.Zp.times(field))
        return jnp.array((
            self.Zp.adjoint(self.FFT.inverse(self.greenskernel[0]*tmp)).real,
            self.Zp.adjoint(self.FFT.inverse(self.greenskernel[1]*tmp)).real
        ))

    def __call__(self, x):
        return self.deflection_field(x)


class LensingPotential():
    def __init__(self, domain, factor=4):
        self.domain = (domain.shape, domain.distances)
        self.target = (domain.shape, domain.distances)

        self.ZP = ZeroPadder(domain, factor)
        self.FFT = FFTOperator(self.ZP.target)
        self.potential_kernel = self.fourier_potential_kernel(
            get_klcoords(self.ZP.target.shape, self.ZP.target.distances))

    @staticmethod
    def fourier_potential_kernel(kl_coords):
        k_square = array(kl_coords[0]**2 + kl_coords[1]**2)
        k_square[0, 0] = 1.0
        potential_kernel = -1.0 / (k_square*(2.0*jnp.pi**2))
        return potential_kernel

    def potential_field(self, field):
        fft_convolved_field = self.potential_kernel * \
            self.FFT.times(self.ZP.times(field))
        return self.ZP.adjoint(self.FFT.inverse(fft_convolved_field))

    def __call__(self, x):
        return self.potential_field(x)
