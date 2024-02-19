# Copyright (C) 2020  Ssohrab Borhanian
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


import numpy as np
import sympy as sp

from gwbench.antenna_pattern_np import ap_symbs_string, det_angles_shape
from gwbench.utils import time_fac, REarth, halfTEarth, cLight

cos = sp.cos
sin = sp.sin
exp = sp.exp

f, Mc, tc, ra, dec, psi, gmst0 = sp.symbols(ap_symbs_string, real=True)

def detector_response_expr(hfp, hfc, loc, use_rot, user_locs=None):
    # input:    hfp     sympy expression of plus polarization
    #           hfc     sympy expression of cross polarization
    #           loc     location (and implied orientation) of a detector
    #           use_rot use frequency dependent time due to roa=tation of earth and SPA
    #
    # output:   hf
    return detector_response(f, hfp, hfc, Mc, tc, ra, dec, psi, gmst0, loc, use_rot, user_locs=user_locs)

def antenna_pattern_and_loc_phase_fac_expr(loc, use_rot, user_locs=None):
    # input:    loc     location (and implied orientation) of a detector
    #           use_rot use frequency dependent time due to roa=tation of earth and SPA
    #
    # output:   Fp, Fc, Flp
    return antenna_pattern_and_loc_phase_fac(f, Mc, tc, ra, dec, psi, gmst0, loc, use_rot, user_locs=user_locs)

def detector_response(f, hfp, hfc, Mc, tc, ra, dec, psi, gmst0, loc, use_rot, user_locs=None):
    # input:    f       frequency domain [Hz]
    #           hfc     cross polarization
    #           hfp     plus polarization
    #           Mc      chirp Mass [solar mass]
    #           tc      time of coalescence [s]
    #           dec     declination [rad]
    #           ra      right ascencsion [rad]
    #           psi     polarization angle [rad]
    #           gmst0   GreenwichMeanSiderialTime according to LAL
    #           loc     location (and implied orientation) of a detector
    #           use_rot use frequency dependent time due to rotation of earth and SPA
    #
    # output:   hf      detector strain

    Fp, Fc, Flp = antenna_pattern_and_loc_phase_fac(f, Mc, tc, ra, dec, psi, gmst0, loc, use_rot, user_locs=user_locs)
    return Flp * (Fp * hfp + Fc * hfc)

def antenna_pattern_and_loc_phase_fac(f, Mc, tc, ra, dec, psi, gmst0, loc, use_rot, user_locs=None):
    # input:    f       frequency domain [Hz]
    #           Mc      chirp Mass [solar mass]
    #           tc      time of coalescence [s]
    #           dec     declination [rad]
    #           ra      right ascencsion [rad]
    #           psi     polarization angle [rad]
    #           gmst0   GreenwichMeanSiderialTime according to LAL
    #           loc     location (and implied orientation) of a detector
    #           use_rot use frequency dependent time due to rotation of earth and SPA
    #
    # output:   Fp, Fc, Flp

    gra  = calc_gra(ra, gmst0, use_rot, f, Mc, tc)
    D, d = det_ten_and_loc_vec(loc, REarth, user_locs=user_locs)

    return *ant_pat_funcs(D, *ant_pat_vectors(gra, dec, psi)), loc_phase_func(gra, dec, f, d)

def calc_gra(ra, gmst0, use_rot, f, Mc, tc):
    if use_rot: return gmst0 - ra + np.pi / halfTEarth * (tc - 5. / 256 * (time_fac * Mc)**(-5./3) * (np.pi * f)**(-8./3))
    else:       return gmst0 - ra

def loc_phase_func(gra, dec, f, d):
    theta = np.pi/2 - dec
    return exp(1j * 2 * np.pi * f * d.T*sp.Matrix([cos(gra)*sin(theta), sin(gra)*sin(theta), cos(theta)]))[0,0]

def ant_pat_funcs(D, XX, YY):
    return (0.5 * (XX.T*D*XX - YY.T*D*YY))[0,0], \
           (0.5 * (XX.T*D*YY + YY.T*D*XX))[0,0]

def ant_pat_vectors(gra, dec, psi):
    return sp.Matrix([ -cos(psi)*sin(gra) - sin(psi)*cos(gra)*sin(dec),
                       -cos(psi)*cos(gra) + sin(psi)*sin(gra)*sin(dec),
                                                     sin(psi)*cos(dec) ]), \
           sp.Matrix([  sin(psi)*sin(gra) - cos(psi)*cos(gra)*sin(dec),
                        sin(psi)*cos(gra) + cos(psi)*sin(gra)*sin(dec),
                                                     cos(psi)*cos(dec) ])

def det_ten_and_loc_vec(loc, R, user_locs=None):
    i_vec = sp.Matrix([1,0,0])
    j_vec = sp.Matrix([0,1,0])
    k_vec = sp.Matrix([0,0,1])

    et_vec2 = ( i_vec + np.sqrt(3.)*j_vec)/2.
    et_vec3 = (-i_vec + np.sqrt(3.)*j_vec)/2.

    alpha, beta, gamma, shape = det_angles_shape(loc, user_locs=user_locs)
    beta = np.pi/2 - beta
    EulerD1 = rot_mat(alpha,'k') * rot_mat(beta,'j') * rot_mat(gamma,'k')

    if   shape == 'V3':
        eDArm1 = -1 * EulerD1*et_vec2
        eDArm2 = -1 * EulerD1*et_vec3
    elif shape == 'V2':
        eDArm1 =      EulerD1*et_vec3
        eDArm2 = -1 * EulerD1*i_vec
    elif shape == 'V1':
        eDArm1 =      EulerD1*i_vec
        eDArm2 =      EulerD1*et_vec2
    elif shape == 'L':
        eDArm1 =      EulerD1*i_vec
        eDArm2 =      EulerD1*j_vec

    return eDArm1*eDArm1.T - eDArm2*eDArm2.T, R/cLight * EulerD1*k_vec

def rot_mat(angle, axis):
    c = np.cos(angle)
    s = np.sin(angle)

    if axis == 'i': return sp.Matrix( [ [1,0,0], [0,c,-s], [0,s,c] ] )
    if axis == 'j': return sp.Matrix( [ [c,0,s], [0,1,0], [-s,0,c] ] )
    if axis == 'k': return sp.Matrix( [ [c,-s,0], [s,c,0], [0,0,1] ] )
