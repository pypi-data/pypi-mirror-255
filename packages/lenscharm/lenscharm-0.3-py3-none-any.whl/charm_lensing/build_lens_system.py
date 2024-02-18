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
from charm_lensing import (spaces, space_model, utils, projection_operator)

from dataclasses import dataclass


@ dataclass
class LensSystem:
    lens_plane_model: space_model.SpaceModel
    source_plane_model: space_model.SpaceModel
    source_projector: jft.Model

    def _get_forward_model(self, only_source=False, parametric=False):
        deflection_model = self.lens_plane_model.convergence_model.deflection(
            parametric=parametric)

        ptree = utils.chain_model_domains(
            deflection_model.domain,
            self.source_plane_model.light_model.domain
        )

        forward = jft.Model(
            lambda x: {'sky': self.source_projector(
                {'source': self.source_plane_model.light_model(x),
                 'deflection': deflection_model(x)}
            )},
            domain=ptree)

        lens_light = self.get_lens_light()
        if lens_light is None or only_source:
            return forward
        else:
            ptree = utils.chain_model_domains(ptree, lens_light.domain)
            return jft.Model(
                lambda x: {'sky': forward(x)['sky'] + lens_light(x)},
                domain=ptree
            )

    def get_forward_model_full(self, only_source=False):
        '''Return the forward pass of the nonparmetric or hybrid model to
        produce the sky emission.

        Parameters
        ----------
        only_source : bool
            If true, the lens light model is not included in the forward model.
        '''
        return self._get_forward_model(only_source=only_source, parametric=False)

    def get_forward_model_parametric(self, only_source=False):
        '''Return the forward pass of the parametric model to
        produce the sky emission.

        Parameters
        ----------
        only_source : bool
            If true, the lens light model is not included in the forward model.
        '''
        return self._get_forward_model(only_source=only_source, parametric=True)

    def get_lens_light(self):
        if self.lens_plane_model.light_model is None:
            return None
        return self.lens_plane_model.light_model

    def critical_caustic(self, position: dict, plot=False):
        '''Calculate the critical and caustic lines of the lens system.

        Parameters
        ----------
        position : dict
            A position in latent space of the lens system.
        plot : bool
            If true, the critical and caustic are plotted.
        '''
        from .critical_and_caustic import calculate_critical_caustic as clcc
        return clcc(self, position, plot=plot)


def build_lens_system(cfg: dict) -> LensSystem:
    '''
    Parse the configuration file and build the lens system and the projection 
    operator.

    Parameters
    ----------
    cfg : dict, The configuration file which has to hold
        - 'lens_space' : dict
          - 'Npix' : int
          - 'distance' : float
          - 'padding_ratio' : float (default=0.0)
        - 'source_space' : dict
          - 'Npix' : int
          - 'distance' : float
          - 'padding_ratio' : float (default=0.0)
        - 'model' : dict
          - 'lens' : dict (The lens model)
          - 'source' : dict (The source light model)
    '''

    # Spaces and larger Spaces to avoid periodic boundary conditions
    lens_space = spaces.Space(
        cfg['spaces']['lens_space']['Npix'],
        cfg['spaces']['lens_space']['distance'],
        'lens',
        cfg['spaces']['lens_space']['padding_ratio'])

    source_space = spaces.Space(
        cfg['spaces']['source_space']['Npix'],
        cfg['spaces']['source_space']['distance'],
        'source',
        cfg['spaces']['source_space']['padding_ratio'])

    lens_plane_model = space_model.build_space_model(
        lens_space,
        cfg['model']['lens'],
        light_extend=False
    )

    source_plane_model = space_model.build_space_model(
        source_space,
        cfg['model']['source'],
        light_extend=True
    )

    source_projector = projection_operator.build_projection_operator(
        lens_space, source_space, cfg['spaces'].get('interpolation', 'bilinear'))

    return LensSystem(
        lens_plane_model=lens_plane_model,
        source_plane_model=source_plane_model,
        source_projector=source_projector
    )
