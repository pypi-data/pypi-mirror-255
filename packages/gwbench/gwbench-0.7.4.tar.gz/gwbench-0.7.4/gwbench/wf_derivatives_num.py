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


'''This module contains two methods that calculate numerical derivatives.
'''

import numdifftools as nd

import gwbench.analytic_derivatives as ad
import gwbench.utils as utils

def part_deriv_hf_func(hf, symbols_list, deriv_symbs_list, f, params_dic,
                       pl_cr=0, compl=1, label='hf',
                       ana_deriv_symbs_list=None, ana_deriv_aux=None,
                       step=1e-9, method='central', order=2, d_order_n=1):

    if 'f' in symbols_list: symbols_list.remove('f')
    if ana_deriv_symbs_list is None: _ana_deriv_symbs_list = []
    else:                            _ana_deriv_symbs_list = [ el for el in deriv_symbs_list if el in ana_deriv_symbs_list ]
    params_list       = [ params_dic[param] for param in symbols_list ]
    _deriv_symbs_list = [ el for el in deriv_symbs_list if el not in _ana_deriv_symbs_list ]
    deriv_params_list = [ params_dic[param] for param in _deriv_symbs_list ]

    if _ana_deriv_symbs_list:
        if pl_cr:
            d_hfpc         = { pc : ad.wf_ana_derivs(f, params_dic, ana_deriv_aux[f'hf{pc}']) for pc in ('p', 'c') }
            del_hf_dic_ana = { f'del_{name}_{label + pc}' : d_hfpc[pc][name] for name in _ana_deriv_symbs_list for pc in ('p', 'c') }
        else:
            d_hf           = ad.dr_ana_derivs(f, params_dic, **ana_deriv_aux)
            del_hf_dic_ana = { f'del_{name}_{label}'      : d_hf[name] for name in _ana_deriv_symbs_list }

    if not _deriv_symbs_list: return del_hf_dic_ana

    def hf_of_deriv_params(f, *deriv_params_list):
        return hf(f, *[deriv_params_list[_deriv_symbs_list.index(el)] if el in _deriv_symbs_list else params_list[i] for i,el in enumerate(symbols_list)])

    del_hf = part_deriv(hf_of_deriv_params, f, deriv_params_list, pl_cr, compl, step, method, order, d_order_n)

    if pl_cr:
        if len(_deriv_symbs_list) == 1: del_hf = (del_hf[0][:,None], del_hf[1][:,None])
        del_hf_dic = { f'del_{name}_{label + pc}' : _del_hf[:,i] for i,name in enumerate(_deriv_symbs_list) for pc, _del_hf in zip(('p', 'c'), del_hf) }
    else:
        if len(_deriv_symbs_list) == 1: del_hf = del_hf[:,None]
        del_hf_dic = { f'del_{name}_{label}'      :  del_hf[:,i] for i,name in enumerate(_deriv_symbs_list) }

    if _ana_deriv_symbs_list:
        del_hf_dic  = { **del_hf_dic, **del_hf_dic_ana }
        sorted_keys = [ key for name in deriv_symbs_list for key in del_hf_dic if name == key[4:].split(f'_{label}')[0] ]
        del_hf_dic  = { key : del_hf_dic[key] for key in sorted_keys}

    return del_hf_dic


def part_deriv(func, f, params_list, pl_cr=0, compl=None, step=1e-9, method='central', order=2, d_order_n=1):
    if pl_cr:
        if compl:
            def amp_pha_of_hfpc_compl(f, *params_list):
                return utils.pl_cr_to_amp_pha(*func(f, *params_list))

            amp_pl, pha_pl, amp_cr, pha_cr = amp_pha_of_hfpc_compl(f, *params_list)

            del_amp_pl = part_deriv_ndGradient(amp_pha_of_hfpc_compl, f, params_list, 0, step, method, order, d_order_n)
            del_pha_pl = part_deriv_ndGradient(amp_pha_of_hfpc_compl, f, params_list, 1, step, method, order, d_order_n)
            del_amp_cr = part_deriv_ndGradient(amp_pha_of_hfpc_compl, f, params_list, 2, step, method, order, d_order_n)
            del_pha_cr = part_deriv_ndGradient(amp_pha_of_hfpc_compl, f, params_list, 3, step, method, order, d_order_n)

            del_hfp = utils.z_deriv_from_amp_pha(amp_pl, pha_pl, del_amp_pl, del_pha_pl)
            del_hfc = utils.z_deriv_from_amp_pha(amp_cr, pha_cr, del_amp_cr, del_pha_cr)

            return del_hfp, del_hfc

        else:
            def amp_pha_of_hfpc_real(f, *params_list):
                return utils.amp_pha_from_re_im(*func(f, *params_list))

            amp, pha = amp_pha_of_hfpc_real(f, *params_list)
            del_amp = part_deriv_ndGradient(amp_pha_of_hfpc_real, f, params_list, 0, step, method, order, d_order_n)
            del_pha = part_deriv_ndGradient(amp_pha_of_hfpc_real, f, params_list, 1, step, method, order, d_order_n)

            return utils.re_im_from_z(utils.z_deriv_from_amp_pha(amp, pha, del_amp, del_pha))

    else:
        if compl:
            def amp_pha_of_hf(f, *params_list):
                return utils.amp_pha_from_z(func(f, *params_list))

            amp, pha = amp_pha_of_hf(f, *params_list)
            del_amp = part_deriv_ndGradient(amp_pha_of_hf, f, params_list, 0, step, method, order, d_order_n)
            del_pha = part_deriv_ndGradient(amp_pha_of_hf, f, params_list, 1, step, method, order, d_order_n)

            return utils.z_deriv_from_amp_pha(amp, pha, del_amp, del_pha)

        else:
            return part_deriv_ndGradient(func, f, params_list, None, step, method, order, d_order_n)


def part_deriv_ndGradient(func, f, params_list=None, funcid=None, step=1e-9, method='central', order=2, d_order_n=1):
    def wraps(x):
        if funcid == None: return func(f,*x)
        else:              return func(f,*x)[funcid]

    if params_list == None: return nd.Gradient(wraps, step=step, method=method, order=order, n=d_order_n)
    else:                   return nd.Gradient(wraps, step=step, method=method, order=order, n=d_order_n)(params_list)
