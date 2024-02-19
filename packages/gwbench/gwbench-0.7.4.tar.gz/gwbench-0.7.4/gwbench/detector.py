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


"""This module handles calculations for a single gravitational wave detector.

"""

from copy import copy

import dill
import numpy as np

import gwbench.antenna_pattern_np as ant_pat_np
import gwbench.detector_response_derivatives as drd
import gwbench.err_deriv_handling as edh
import gwbench.fisher_analysis_tools as fat
import gwbench.psd as psd
import gwbench.snr as snr_mod
import gwbench.utils as utils

class Detector:

    ###
    #-----Init methods-----
    def __init__(self, det_key):
        #-----detector specification-----
        # full detector specification, specifying technology and location, e.g. CE2-40-CBO_C
        self.det_key = det_key
        # detector technology and locations
        self.tec = det_key.split('_')[0]
        self.loc = det_key.split('_')[1]

        #-----waveform and injection based quantities-----
        # frequency array
        self.f = None

        #-----technology and location based quantities-----
        # detector PSD
        self.psd = None
        # antenna pattern
        self.Fp = None
        self.Fc = None
        # location phase factor
        self.Flp = None

        #-----detector reponses-----
        # detector repsonse
        self.hf = None
        # derivative dictionary for detector responses
        self.del_hf = None
        # sympy expression of derivative dictionary for detector responses
        self.del_hf_expr = None

        #-----SNR-----
        # SNR, SNR^2 and d(SNR^2) calculated from self.hf
        self.snr = None
        self.snr_sq = None
        self.d_snr_sq = None

        #-----errors-----
        # Fisher matrix
        self.fisher = None
        # condition number of Fisher matrix
        self.cond_num = None
        # covariance matrix
        self.cov = None
        # dictionary containing information about the inversion error between the two matrices
        self.inv_err = None
        # dictionary of errors for given derivative variables
        self.errs = None


    ###
    #-----Setter methods-----
    def set_f(self, f):
        self.f = copy(f)


    ###
    #-----PSDs and antenna patterns-----
    def setup_psds(self, F_lo=-np.inf, F_hi=np.inf, user_psds=None):
        if user_psds is None or (self.det_key not in user_psds and self.tec not in user_psds):
            psd_file = None
            is_asd   = None
        elif self.det_key in user_psds:
            psd_file = user_psds[self.det_key]['psd_file']
            is_asd   = user_psds[self.det_key]['is_asd']
        else:
            psd_file = user_psds[self.tec]['psd_file']
            is_asd   = user_psds[self.tec]['is_asd']
        self.psd, self.f = psd.psd(self.tec,self.f,F_lo,F_hi,psd_file,is_asd)

    def setup_ant_pat_lpf(self, inj_params, use_rot, user_locs=None):
        self.Fp, self.Fc, self.Flp = ant_pat_np.antenna_pattern_and_loc_phase_fac(self.f, inj_params.get('Mc'), inj_params.get('tc'),
            inj_params['ra'], inj_params['dec'], inj_params['psi'], inj_params['gmst0'], self.loc, use_rot, user_locs=user_locs)


    ###
    #-----Detector responses-----
    def calc_det_responses(self, wf, inj_params):
        hfp, hfc = wf.eval_np_func(self.f, utils.get_sub_dict(inj_params, wf.wf_symbs_string))
        self.hf = self.Flp * (hfp * self.Fp + hfc * self.Fc)
        return self.hf, hfp, hfc

    def calc_det_responses_derivs_num(self, inj_params, wf, deriv_symbs_string, deriv_variables, conv_cos, conv_log, use_rot,
                                      step, method, order, d_order_n, user_locs, ana_deriv_symbs_string):
        _, hfp, hfc = self.calc_det_responses(wf, inj_params)
        self.del_hf = drd.calc_det_responses_derivs_num(self.loc, wf, deriv_symbs_string, self.f, inj_params, use_rot=use_rot, label='hf',
                                                        step=step, method=method, order=order, d_order_n=d_order_n, user_locs=user_locs,
                                                        ana_deriv_symbs_string=ana_deriv_symbs_string,
                                                        ana_deriv_aux={'hf':self.hf,   'hfp':hfp,         'hfc':hfc,
                                                                       'Fp':self.Fp,   'Fc':self.Fc,      'Flp':self.Flp,
                                                                       'loc':self.loc, 'use_rot':use_rot, 'user_locs':user_locs})
        self.del_hf, c_quants = edh.get_conv_del_eval_dic(self.del_hf, inj_params, conv_cos, conv_log, deriv_symbs_string)
        inj_params, deriv_variables = edh.get_conv_inj_params_deriv_variables(c_quants, inj_params, deriv_variables)

    def load_det_responses_derivs_sym(self, wf_model_name, deriv_symbs_string, use_rot, return_bin=0, user_lambdified_functions_path=None):
        self.del_hf_expr = drd.load_det_responses_derivs_sym(self.loc, wf_model_name, deriv_symbs_string, use_rot, return_bin, user_lambdified_functions_path)

    def calc_det_responses_derivs_sym(self, wf, inj_params, deriv_symbs_string, deriv_variables, conv_cos, conv_log):
        self.calc_det_responses(wf, inj_params)
        self.del_hf = {}
        for deriv in self.del_hf_expr:
            if deriv in ('variables', 'deriv_variables'): continue
            self.del_hf[deriv] = self.del_hf_expr[deriv](self.f, **utils.get_sub_dict(inj_params, self.del_hf_expr['variables']))

        self.del_hf, c_quants = edh.get_conv_del_eval_dic(self.del_hf, inj_params, conv_cos, conv_log, deriv_symbs_string)
        inj_params, deriv_variables = edh.get_conv_inj_params_deriv_variables(c_quants, inj_params, deriv_variables)


    ###
    #-----SNR calculations-----
    def calc_snrs(self, only_net):
        snr,snr_sq = snr_mod.snr_snr_sq_freq_array(self.hf, self.psd, self.f)
        if not only_net:
            self.snr = snr
            self.snr_sq = snr_sq
        return snr_sq

    def calc_snr_sq_integrand(self):
        self.d_snr_sq = snr_mod.snr_square_integrand(self.hf, self.psd)


    ###
    #-----Error calculation and Fisher analysis-----
    def calc_fisher_cov_matrices(self, only_net, cond_sup, logger=None):
        del_hf_sub_dict = utils.get_sub_dict(self.del_hf, ('hf',), 0)
        if not only_net:
            self.fisher, self.cov, self.cond_num, self.inv_err = fat.calc_fisher_cov_matrices(list(del_hf_sub_dict.values()), self.psd, self.f, only_fisher=0, cond_sup=cond_sup, logger=logger, tag=self.det_key)
            return self.fisher
        else:
            fisher,_,_,_ = fat.calc_fisher_cov_matrices(list(del_hf_sub_dict.values()), self.psd, self.f, only_fisher=1, cond_sup=cond_sup, logger=logger, tag=self.det_key)
            return fisher

    def calc_inv_err(self):
        self.inv_err = fat.inv_err_from_fisher_cov(self.fisher,self.cov)

    def calc_errs(self, deriv_variables):
        self.errs = fat.get_errs_from_cov(self.cov,deriv_variables)

    def calc_sky_area_90(self, deriv_variables, logger=None):
        if self.cov is None or self.errs is None: return
        if 'ra' in deriv_variables and ('cos_dec' in deriv_variables or 'dec' in deriv_variables):
            if 'cos_dec' in deriv_variables: dec_str = 'cos_dec'
            else:                                 dec_str = 'dec'
            ra_id      = deriv_variables.index('ra')
            dec_id     = deriv_variables.index(dec_str)
            is_cos_dec = (dec_str == 'cos_dec')
            self.errs['sky_area_90'] = edh.sky_area_90(self.errs['ra'],self.errs[dec_str],self.cov[ra_id,dec_id],self.inj_params['dec'],is_cos_dec)
        else:
            utils.log_msg(f'calc_sky_area_90: tag = {self.det_key} - Nothing done due to missing of either RA or COS_DEC (DEC) errors.', logger=logger, level='WARNING')

    def calc_sky_area_90_network(self, ra_id, dec_id, dec_val, is_cos_dec, dec_str):
        if self.cov is None or self.errs is None: return
        self.errs['sky_area_90'] = edh.sky_area_90(self.errs['ra'],self.errs[dec_str],self.cov[ra_id,dec_id],dec_val,is_cos_dec)


    ###
    #-----IO methods-----
    def print_detector(self,print_format=1):
        if print_format:
            sepl='-----------------------------------------------------------------------------------'
            print()
            print(sepl)
            print('Printing detector.')
            print(sepl)
            print()
        for key,value in vars(self).items():
            if type(value) == dict:
                print('Key: ',key)
                for key in value.keys():
                    print('',key)
                    print('',value[key])
                print()
            elif value is not None:
                print('Key: ',key)
                print(value)
                print()
        if print_format:
            print(sepl)
            print('Printing detector done.')
            print(sepl)
            print()
