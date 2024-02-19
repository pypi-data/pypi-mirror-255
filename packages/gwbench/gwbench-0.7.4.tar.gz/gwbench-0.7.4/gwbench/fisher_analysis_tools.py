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


import mpmath as mp
import numpy as np

import gwbench.snr as snr_mod
from gwbench.utils import log_msg

def calc_fisher_cov_matrices(del_hf_list, psd, f, only_fisher=0, cond_sup=None, fac=101, logger=None, tag=''):
    n = len(del_hf_list)
    fisher = np.zeros((n,n))

    for i in np.arange(n):
        fisher[i,i]     = snr_mod.scalar_product_freq_array(del_hf_list[i], del_hf_list[i], psd, f)
        for j in np.arange(i+1,n):
            fisher[i,j] = snr_mod.scalar_product_freq_array(del_hf_list[i], del_hf_list[j], psd, f)
            fisher[j,i] = fisher[i,j]

    if only_fisher: return fisher, None, None, None

    cond_num     = calc_cond_number(fisher, logger=logger, tag=tag)
    cov, inv_err = calc_cov_inv_err(fisher, cond_num, cond_sup, fac, logger=logger, tag=tag)
    return fisher, cov, cond_num, inv_err

def calc_cond_number(fisher, logger=None, tag=''):
    EWs,_ = np.linalg.eig(fisher)
    if not np.amin(np.abs(EWs)):
        log_msg(f'calc_cond_number: tag = {tag} - Fisher matrix is singular!', logger=logger, level='WARNING')
        return np.inf
    else:
        return np.amax(np.abs(EWs))/np.amin(np.abs(EWs))

def calc_cov_inv_err(fisher, cond_num=None, cond_sup=None, fac=101, logger=None, tag=''):
    if cond_num is None: cond_num = calc_cond_number(fisher, logger=logger, tag=tag)
    if cond_num == np.inf: return None, None # Singular Fisher matrix

    try:
        if cond_sup is not None and cond_sup < 1e16 and cond_sup > cond_num:
            cov   = np.linalg.inv(fisher)
            cov   = (cov + cov.T) / 2
            ident = np.identity(len(fisher))
            return cov, inv_err_from_fisher_cov(fisher, cov, ident, fac, None)
        else:
            mp.mp.dps = max(int(np.ceil(np.log10(cond_num))) + 2, 20)
            fisher_mp = mp.matrix(fisher)
            cov_mp    = fisher_mp**-1
            cov_mp    = (cov_mp + cov_mp.T) / 2
            ident_mp  = mp.matrix(np.identity(len(fisher)))
            return conv_mp_to_np(cov_mp), inv_err_from_fisher_cov(fisher_mp, cov_mp, ident_mp, fac, mp.mp.dps)

    except (ZeroDivisionError, np.linalg.LinAlgError):
        log_msg(f'calc_cov_inv_err: tag = {tag} - There was an exception in the inversion of the Fisher matrix!',
                logger=logger, level='WARNING')
        return None, None

def get_errs_from_cov(cov, deriv_variables):
    if cov is None: return None
    else:           return { name : np.sqrt(cov[i,i]) for i,name in enumerate(deriv_variables) }

def conv_mp_to_np(matrix, dtype=np.float32):
    return np.matrix(matrix.tolist(), dtype=dtype)

def inv_err_from_fisher_cov(fisher, cov, ident, fac, dps):
    cov_err, delta = calc_cov_err_inv_res(fisher, cov, ident)
    if dps is None:
        inv_err                = {'fisher_mp': None,   'cov_mp': None, 'dps_mp':None}
        inv_err['inv_err_mat'] = delta
        inv_err['inv_err']     = np.amax(np.abs(delta))
        inv_err['inv_cond']    = np.all(np.abs(fac * cov_err) < np.abs(cov))
        return inv_err
    else:
        inv_err                = {'fisher_mp': fisher, 'cov_mp': cov,  'dps_mp':dps}
        inv_err['inv_err_mat'] = delta
        inv_err['inv_err']     = np.amax(np.abs(conv_mp_to_np(delta)))
        inv_err['inv_cond']    = np.all(np.abs(fac * conv_mp_to_np(cov_err)) < np.abs(conv_mp_to_np(cov)))
        return inv_err

def calc_cov_err_inv_res(fisher, cov, ident):
    if isinstance(fisher, np.ndarray):
        delta = np.matmul(fisher, cov) - ident
        return np.matmul(np.matmul(cov, delta), np.linalg.inv(ident + delta)), delta
    else:
        delta = fisher * cov - ident
        return cov * delta * (ident + delta)**-1, delta
