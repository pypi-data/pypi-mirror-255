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


import os

import dill

import gwbench.antenna_pattern_np as ant_pat_np
import gwbench.antenna_pattern_sp as ant_pat_sp
import gwbench.waveform as wfc
import gwbench.wf_derivatives_num as wfd_num
import gwbench.wf_derivatives_sym as wfd_sym
import gwbench.utils as utils

lambdified_functions_path = os.path.join(os.getcwd(), 'lambdified_functions')

def calc_det_responses_derivs_num(loc, wf, deriv_symbs_string, f_arr,
                                  params_dic, use_rot=1, label='hf',
                                  step=1e-9, method='central', order=2, d_order_n=1,
                                  user_locs=None, ana_deriv_symbs_string=None,
                                  ana_deriv_aux=None):

    wf_symbs_list    = wf.wf_symbs_string.split(' ')
    deriv_symbs_list = deriv_symbs_string.split(' ')
    if ana_deriv_symbs_string is None: ana_deriv_symbs_list = None
    else:                              ana_deriv_symbs_list = ana_deriv_symbs_string.split(' ')

    if 'f' in wf_symbs_list: wf_symbs_list.remove('f')
    if 'f' in deriv_symbs_list: deriv_symbs_list.remove('f')

    if loc == None:
        wf_params_list = list(utils.get_sub_dict(params_dic, wf_symbs_list).values())

        def pc_func(f_arr, *wf_params_list):
            return wf.eval_np_func(f_arr, [ wf_params_list[wf_symbs_list.index(el)]
                                            for i,el in enumerate(wf_symbs_list) ])

        return wfd_num.part_deriv_hf_func(pc_func, wf_symbs_list, deriv_symbs_list, f_arr, params_dic,
                                          pl_cr=1, compl=1, label=label,
                                          ana_deriv_symbs_list=ana_deriv_symbs_list,
                                          ana_deriv_aux=ana_deriv_aux,
                                          step=step, method=method, order=order, d_order_n=d_order_n)

    else:
        ap_symbs_list = ant_pat_np.ap_symbs_string.split(' ')
        if 'f' in ap_symbs_list: ap_symbs_list.remove('f')

        dr_symbs_list  = utils.reduce_symbols_strings(wf.wf_symbs_string,
                                                      ant_pat_np.ap_symbs_string).split(' ')
        dr_params_list = list(utils.get_sub_dict(params_dic, dr_symbs_list).values())

        def dr_func(f_arr, *dr_params_list):
            hfp, hfc    = wf.eval_np_func(f_arr, [ dr_params_list[dr_symbs_list.index(el)]
                                                   for i,el in enumerate(wf_symbs_list) ])
            Fp, Fc, Flp = ant_pat_np.antenna_pattern_and_loc_phase_fac(f_arr,
                *[ dr_params_list[dr_symbs_list.index(el)] for i,el in enumerate(ap_symbs_list) ],
                loc, use_rot, user_locs=user_locs)
            return Flp * (hfp * Fp + hfc * Fc)

        return wfd_num.part_deriv_hf_func(dr_func, dr_symbs_list, deriv_symbs_list, f_arr, params_dic,
                                          pl_cr=0, compl=1, label=label,
                                          ana_deriv_symbs_list=ana_deriv_symbs_list,
                                          ana_deriv_aux=ana_deriv_aux,
                                          step=step, method=method, order=order, d_order_n=d_order_n)



def generate_det_responses_derivs_sym(wf_model_name, wf_other_var_dic, deriv_symbs_string, use_rot,
                                      locs=None, user_locs=None, user_waveform=None,
                                      user_lambdified_functions_path=None):

    # initialize waveform object
    wf = wfc.Waveform(wf_model_name, wf_other_var_dic, user_waveform=user_waveform)

    # check that derivative variables are a subset of the detector response variables
    full_set = set( wf.wf_symbs_string.split(' ') + ant_pat_np.ap_symbs_string.split(' ') )
    sub_set  = set( deriv_symbs_string.split(' ') )
    if not sub_set <= full_set:
        utils.log_msg('The choice of derivative variables is not a subset of the waveform ' +
                      'and antenna pattern variables!', level='ERROR')

    utils.log_msg( 'Generating lambdified derivatives via sympy with the following settings:\n' +
                  f'      wf_model_name      = {wf.wf_model_name}\n' +
                  f'      deriv_symbs_string = {deriv_symbs_string}\n' +
                  f'      use_rot            = {bool(use_rot)}\n' +
                   'Use these settings for a network loading these derivatives.\n', level='INFO')

    hfpc               = wf.get_sp_expr()
    responses          = {}
    responses['pl_cr'] = hfpc

    # make sure specified locations are known
    if locs is None: locs = utils.available_locs
    else:
        for loc in locs:
            if loc not in utils.available_locs and loc not in user_locs:
                utils.log_msg(f'generate_det_responses_derivs_sym: Specified location {loc} not ' +
                               'known in antenna pattern module and was not provided in user_locs.',
                                level='ERROR')

    # compute sympy expressions of the detector responses
    for loc in locs:
        utils.log_msg(f'Loading the detector response expression for {loc}.', level='INFO')
        responses[loc] = ant_pat_sp.detector_response_expr(hfpc[0], hfpc[1], loc,
                                                           use_rot, user_locs=user_locs)
    # compute derivatives
    for key in responses.keys():
        if key == 'pl_cr':
            utils.log_msg('Calculating derivatives of the plus/cross polarizations.', level='INFO')
            _deriv_symbs_string = utils.remove_symbols(deriv_symbs_string, wf.wf_symbs_string)
            symbs_string        = wf.wf_symbs_string
        else:
            utils.log_msg(f'Calculating derivatives of the detector responses for: {key}.', level='INFO')
            _deriv_symbs_string = deriv_symbs_string
            symbs_string        = utils.reduce_symbols_strings(wf.wf_symbs_string,
                                                               ant_pat_np.ap_symbs_string)

        if not _deriv_symbs_string:
            utils.log_msg( 'The plus and cross polarizations of the waveform model ' +
                          f'{wf.wf_model_name}   do not depend on the derivative variables:  ' +
                          f'{deriv_symbs_string}\n' +
                          f'         Did not generate lambdified functions file!', level='WARNING')
            continue

        deriv_dic                    = wfd_sym.part_deriv_hf_expr(responses[key], symbs_string,
                                                                  _deriv_symbs_string, pl_cr=(key=='pl_cr'))
        deriv_dic['variables']       = symbs_string
        deriv_dic['deriv_variables'] = _deriv_symbs_string

        if user_lambdified_functions_path is None: output_path = lambdified_functions_path
        else:
            output_path = os.path.join(user_lambdified_functions_path, 'lambdified_functions')
        if not os.path.exists(output_path): os.makedirs(output_path)

        file_name = f'par_deriv_WFM_{wf.wf_model_name}_' + \
                    f'DVAR_{_deriv_symbs_string.replace(" ", "_")}_ROT_{int(use_rot)}_DET_{key}.dat'
        with open(os.path.join(output_path, file_name), "wb") as fi:
            dill.dump(deriv_dic, fi, recurse=True)

    utils.log_msg('Done.', level='INFO')
    return


def load_det_responses_derivs_sym(loc, wf_model_name, deriv_symbs_string, use_rot,
                                  return_bin=0, user_lambdified_functions_path=None):
    if user_lambdified_functions_path is None: user_lambdified_functions_path = lambdified_functions_path
    file_name = f'par_deriv_WFM_{wf_model_name}_' + \
                f'DVAR_{deriv_symbs_string.replace(" ", "_")}_ROT_{int(use_rot)}_DET_{loc}.dat'

    try:
        with open(os.path.join(user_lambdified_functions_path, file_name), "rb") as fi:
            if return_bin: return fi.read()
            else:          return dill.load(fi)
    except FileNotFoundError: utils.log_msg(f'Could not find the lambdified function file: {file_name}',
                                            level='ERROR')
