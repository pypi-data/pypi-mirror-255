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


def calculate_critical_caustic(lens_system, mean, plot=False):
    # From Meneghetti, 2021: Introduction to Gravitational Lensing, see p.80
    '''Returns the coordinates of the critical caustic of the lens system in
    arcsec.

    Returns:
        critial: Tuple[ArrayLike, ArrayLike] = radial, tangential
        caustic: Tuple[ArrayLike, ArrayLike] = radial, tangential

    For plotting:
        lens_image.plot(*critial, 'k')
        source_image.plot(*caustic, 'k')
    '''

    import matplotlib.pyplot as plt
    from scipy.ndimage import map_coordinates
    from charm_lensing.linear_operators import DeflectionAngle

    DA = DeflectionAngle(lens_system.lens_plane_model.space.extend())
    kappa = lens_system.lens_plane_model.convergence_model.model(mean)

    arcsec = lens_system.lens_plane_model.space.distances[0]
    space = lens_system.lens_plane_model.space.extend()
    a1, a2 = DA(kappa).real
    psi12, psi11 = np.gradient(a1, arcsec)
    psi22, psi21 = np.gradient(a2, arcsec)

    gamma1 = 0.5 * (psi11 - psi22)
    gamma2 = psi12
    gamma = np.sqrt(gamma1**2+gamma2**2)
    lambdat = 1.0-kappa-gamma
    lambdar = 1.0-kappa+gamma
    detA = lambdat*lambdar

    cs = plt.contour(detA, levels=[0.0])
    plt.close()

    fig, ax = plt.subplots(1, 2, figsize=(18, 8))
    contour = cs.collections[0]
    # p contains the paths of each individual critical line
    p = contour.get_paths()
    sizevs = np.empty(len(p), dtype=int)

    # if we find any critical line, then we process it if (sizevs.size >0):
    critical, caustic = [], []
    for j in range(len(p)):
        # the contours are ensembles of polygons, called paths
        # for each path, we create two vectors containing the x1 and x2
        # coordinates of the vertices
        vs = contour.get_paths()[j].vertices
        sizevs[j] = len(vs)
        x1 = []
        x2 = []
        for i in range(len(vs)):
            xx1, xx2 = vs[i]
            x1.append(float(xx1))
            x2.append(float(xx2))
        x1 = np.array(x1)
        x2 = np.array(x2)

        a_1 = map_coordinates(a1, [[x2], [x1]], order=1)[0]
        a_2 = map_coordinates(a2, [[x2], [x1]], order=1)[0]

        # now we use the lens equation to # obtain the caustics and transform
        # the coordinates to physical units:
        offset = (-space.extent[1]+space.distances[0]/2,
                  -space.extent[3]+space.distances[1]/2)
        x1, x2 = (
            np.array(x1)*space.distances[0]+offset[0],
            np.array(x2)*space.distances[1]+offset[1]
        )
        y1 = x1-a_1
        y2 = x2-a_2
        ax[0].plot(x1, x2, '-')
        ax[1].plot(y1, y2, '-')

        critical.append(np.array((x1, x2)))
        caustic.append(np.array((y1, y2)))

    if plot:
        plt.show()
    else:
        plt.close()

    return critical, caustic
