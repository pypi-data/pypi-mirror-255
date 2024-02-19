import numpy as np

from gwbench.antenna_pattern_np import ant_pat_vectors, calc_gra, det_ten_and_loc_vec, loc_phase_func
from gwbench.utils import REarth, halfTEarth

cos = np.cos
sin = np.sin

# for the antenna pattern and location phase derivatives
# del__ra_dec_psi_tc__gra/dec/psi
deriv_keys    = ('ra', 'dec', 'psi', 'tc')

def d_gra_dec_psi(use_rot):
    if use_rot is not None and use_rot:
        return np.array([ [ -1, 0, 0, np.pi / halfTEarth ],
                          [  0, 1, 0, 0 ],
                          [  0, 0, 1, 0 ] ])
    else:
        return np.array([ [ -1, 0, 0, 0 ],
                          [  0, 1, 0, 0 ],
                          [  0, 0, 1, 0 ] ])

def dr_ana_derivs(f, params_dic, hf, hfp, hfc, Fp, Fc, Flp, loc, use_rot, user_locs=None):
    d_hf              = wf_ana_derivs(f, params_dic, hf)
    d_Fp, d_Fc, d_Flp = antenna_pattern_and_loc_phase_fac_ana_derivs(f, params_dic, loc, use_rot, user_locs=user_locs)
    return {
        'DL'    : d_hf['DL'],
        'phic'  : d_hf['phic'],
        'tc'    : d_Flp['tc']  * (hfp * Fp + hfc * Fc) + Flp * (hfp * d_Fp['tc']  + hfc * d_Fc['tc'] ) + d_hf['tc'],
        'ra'    : d_Flp['ra']  * (hfp * Fp + hfc * Fc) + Flp * (hfp * d_Fp['ra']  + hfc * d_Fc['ra'] ),
        'dec'   : d_Flp['dec'] * (hfp * Fp + hfc * Fc) + Flp * (hfp * d_Fp['dec'] + hfc * d_Fc['dec']),
        'psi'   : d_Flp['psi'] * (hfp * Fp + hfc * Fc) + Flp * (hfp * d_Fp['psi'] + hfc * d_Fc['psi']),
        }

# waveform derivatives
def wf_ana_derivs(f, params_dic, hf):
    return {
        'DL'    : -hf / params_dic['DL'],
        'tc'    : (1j * 2 * np.pi) * f * hf,
        'phic'  : -1j * hf,
        }

# antenna pattern and location phase factor derivatives
def antenna_pattern_and_loc_phase_fac_ana_derivs(f, params_dic, loc, use_rot, user_locs=None):
    gra        = calc_gra(params_dic['ra'], params_dic['gmst0'], use_rot, f, params_dic['Mc'], params_dic['tc'])
    D, d       = det_ten_and_loc_vec(loc, REarth, user_locs=user_locs)
    d_XX, d_YY = np.matmul(calc_d_ant_pat_vectors(gra, params_dic['dec'], params_dic['psi']), d_gra_dec_psi(use_rot))
    d_Fp, d_Fc = calc_d_ant_pat_funcs(D, *ant_pat_vectors(gra, params_dic['dec'], params_dic['psi']))
    return { key : deriv for key,deriv in zip(deriv_keys, (np.matmul(d_Fp['XX'], d_XX) + np.matmul(d_Fp['YY'], d_YY)).flatten()) }, \
           { key : deriv for key,deriv in zip(deriv_keys, (np.matmul(d_Fc['XX'], d_XX) + np.matmul(d_Fc['YY'], d_YY)).flatten()) }, \
           { key : deriv for key,deriv in zip(deriv_keys, np.matmul(calc_d_loc_phase_func(gra, params_dic['dec'], f, d).T, d_gra_dec_psi(use_rot)[:2]).T) }

# location phase factor
def calc_d_loc_phase_func(gra, dec, f, d):
    theta = np.pi/2 - dec
    return loc_phase_func(gra, dec, f, d) * 1j * 2 * np.pi * f * np.array([
        # del_gra_Flp
        np.matmul(d, np.array([ -sin(gra)*sin(theta),  cos(gra)*sin(theta),           np.zeros_like(gra) ])),
        # del_dec_Flp
        np.matmul(d, np.array([ -cos(gra)*cos(theta), -sin(gra)*cos(theta), sin(theta)*np.ones_like(gra) ]))
        ])

# antenna patterns
def calc_d_ant_pat_funcs(D, XX, YY):
    # return d_Fp, d_Fc
    return {'XX': np.matmul(D,XX).T[None,:,:], 'YY':-np.matmul(D,YY).T[None,:,:]}, \
           {'XX': np.matmul(D,YY).T[None,:,:], 'YY': np.matmul(D,XX).T[None,:,:]}

# antenna pattern vectors
def calc_d_ant_pat_vectors(gra, dec, psi):
    # return del_gra_dec_psi_XX, del_gra_dec_psi_XX
    return np.array([ [ -cos(psi)*cos(gra) + sin(psi)*sin(gra)*sin(dec),  cos(psi)*sin(gra) + sin(psi)*cos(gra)*sin(dec),                   np.zeros_like(gra) ],
                      [                     -sin(psi)*cos(gra)*cos(dec),                      sin(psi)*sin(gra)*cos(dec), -sin(psi)*sin(dec)*np.ones_like(gra) ],
                      [  sin(psi)*sin(gra) - cos(psi)*cos(gra)*sin(dec),  sin(psi)*cos(gra) + cos(psi)*sin(gra)*sin(dec),  cos(psi)*cos(dec)*np.ones_like(gra) ] ]).T, \
           np.array([ [  sin(psi)*cos(gra) + cos(psi)*sin(gra)*sin(dec), -sin(psi)*sin(gra) + cos(psi)*cos(gra)*sin(dec),                   np.zeros_like(gra) ],
                      [                     -cos(psi)*cos(gra)*cos(dec),                      cos(psi)*sin(gra)*cos(dec), -cos(psi)*sin(dec)*np.ones_like(gra) ],
                      [  cos(psi)*sin(gra) + sin(psi)*cos(gra)*sin(dec),  cos(psi)*cos(gra) - sin(psi)*sin(gra)*sin(dec), -sin(psi)*cos(dec)*np.ones_like(gra) ] ]).T
