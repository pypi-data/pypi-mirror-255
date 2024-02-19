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


"""This module handles the benchmarking of graviational waveforms observed by a network of detectors.

"""

import logging
from copy import copy, deepcopy

import dill
import numpy as np
from pathos.pools import ProcessPool

import gwbench.detector as dc
import gwbench.detector_response_derivatives as drd
import gwbench.err_deriv_handling as edh
import gwbench.fisher_analysis_tools as fat
import gwbench.waveform as wfc
import gwbench.utils as utils

# logger
glob_logger = logging.getLogger('network_module')
glob_logger.setLevel('INFO')

class Network:

    ###
    #-----Init methods-----
    def __init__(self, network_spec=None, logger_name='Network', logger_level='INFO'):
        ##-----logger-----
        self.logger = utils.get_logger(name=logger_name, level=logger_level)

        ##-----initialize network object-----
        if network_spec is None:
            #-----network and detectors
            # network label
            self.label = None
            # detector labels list
            self.det_keys = None
            # list of detectors in network
            self.detectors = None
        elif isinstance(network_spec, str):
            #-----network and detectors
            self.set_network_and_detectors_from_label(network_spec)
        elif isinstance(network_spec, list) or isinstance(network_spec, tuple):
            #-----network and detectors
            self.set_network_and_detectors_from_key_list(network_spec)

        #-----injection and waveform quantities-----
        # frequency array
        self.f = None
        # dictionary of injection parameters
        self.inj_params = None
        # derivative variables - symbs_string and list
        self.deriv_symbs_string = None
        self.deriv_variables = None
        # derivative variables for which analytical derivatives should be used
        self.ana_deriv_symbs_string = None
        self.ana_deriv_symbs_list = None
        # waveform
        self.wf = None

        #-----analysis settings-----
        # list of inj_params to convert to cos, ln versions
        self.conv_cos = None
        self.conv_log = None
        # use f-dependent gmst (SPA) in antenna patterns
        self.use_rot = None

        #-----user defined detector locations and PSDs-----
        self.user_locs = None
        self.user_psds = None
        self.user_lambdified_functions_path = None

        #-----waveform polarizations-----
        # plus/cross polarizations
        self.hfp = None
        self.hfc = None
        # derivative dictionary for polarizations
        self.del_hfpc = None
        # sympy expressions of derivative dictionary for polarizations
        self.del_hfpc_expr = None

        #-----network SNR-----
        # SNR, SNR^2 calculated from hf
        self.snr = None
        self.snr_sq = None

        #-----network errors-----
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

        if self.label is None: self.logger.debug('Empty network initialized.')
        else:                  self.logger.debug('Network initialized.')


    ###
    #-----Setter methods-----
    #
    # it is best practice to always change the instance variables using these setter methods
    #
    def set_logger_level(self, level):
        utils.set_logger_level(self.logger, level)

    def set_network_and_detectors_from_label(self, network_label):
        #-----network and detectors
        self.label     = network_label
        self.det_keys  = utils.read_det_keys_from_label(network_label)
        self.detectors = [ dc.Detector(det_key) for det_key in self.det_keys ]

    def set_network_and_detectors_from_key_list(self, det_key_list):
        #-----network and detectors
        if isinstance(det_key_list, tuple): self.det_keys = [ tec + '_' + loc for tec,loc in zip(det_key_list[0], det_key_list[1]) ]
        else:                               self.det_keys = copy(det_key_list)
        self.label     = '..'.join(self.det_keys)
        self.detectors = [ dc.Detector(det_key) for det_key in self.det_keys ]

    def set_wf_vars(self, wf_model_name, wf_other_var_dic=None, user_waveform=None, cosmo=None):
        self.wf = wfc.Waveform(wf_model_name, wf_other_var_dic=wf_other_var_dic, user_waveform=user_waveform, cosmo=cosmo, logger=self.logger)

    def set_net_vars(self, wf_model_name=None, wf_other_var_dic=None, user_waveform=None, cosmo=None,
                     f=None, inj_params=None, deriv_symbs_string=None, conv_cos=None, conv_log=None,
                     use_rot=None, user_locs=None, user_psds=None, user_lambdified_functions_path=None, ana_deriv_symbs_string=None):
        if wf_model_name is not None:
            self.wf = wfc.Waveform(wf_model_name, wf_other_var_dic=wf_other_var_dic, user_waveform=user_waveform, cosmo=cosmo, logger=self.logger)
        if f is not None:
            self.f = copy(f)
            if self.detectors is not None:
                for det in self.detectors:
                    det.set_f(self.f)
        if inj_params is not None:
            self.inj_params = deepcopy(inj_params)
            self.constrain_gmst0()
        if deriv_symbs_string is not None:
            self.deriv_symbs_string = copy(deriv_symbs_string)
            self.deriv_variables = deriv_symbs_string.split(' ')
        if ana_deriv_symbs_string is not None:
            self.ana_deriv_symbs_string = copy(ana_deriv_symbs_string)
            self.ana_deriv_symbs_list = ana_deriv_symbs_string.split(' ')
        if conv_cos is not None:
            self.conv_cos = copy(conv_cos)
        if conv_log is not None:
            self.conv_log = copy(conv_log)
        if use_rot is not None:
            self.use_rot = copy(use_rot)
        if user_locs is not None:
            self.user_locs = deepcopy(user_locs)
        if user_psds is not None:
            self.user_psds = deepcopy(user_psds)
        if user_lambdified_functions_path is not None:
            self.user_lambdified_functions_path = copy(user_lambdified_functions_path)

    ##
    #-----Resetter methods for instance variables-----
    def reset_ant_pat_lpf_psds(self):
        for det in self.detectors:
            det.Fp = None
            det.Fc = None
            det.Flp = None
            det.psd = None

    def reset_wf_polarizations(self):
        self.hfp = None
        self.hfc = None
        self.del_hfpc = None
        self.del_hfpc_expr = None

    def reset_det_responses(self):
        for det in self.detectors:
            det.hf = None
            det.del_hf = None
            det.del_hf_expr = None

    def reset_snrs(self):
        self.snr = None
        self.snr_sq = None
        for det in self.detectors:
            det.snr = None
            det.snr_sq = None
            det.d_snr_sq = None

    def reset_errors(self):
        self.fisher = None
        self.cond_num = None
        self.cov = None
        self.inv_err = None
        self.errs = None
        for det in self.detectors:
            det.fisher = None
            det.cond_num = None
            det.cov = None
            det.inv_err = None
            det.errs = None


    ###
    #-----Getters-----
    def get_detector(self,det_key):
        return self.detectors[self.det_keys.index(det_key)]

    def get_snrs_errs_cov_fisher_inv_err_for_key(self,key='network'):
        if key == 'network': out_obj = self
        else:                out_obj = self.detectors[self.det_keys.index(key)]
        return out_obj.snr, out_obj.errs, out_obj.cov, out_obj.fisher, out_obj.inv_err


    ###
    #----Helper-----
    def pool_calc_func(self, calc_func, num_cores):
        if num_cores is None: list(map(calc_func, self.detectors))
        else:
            self.detectors, self.inj_params, self.deriv_variables = list(zip(*ProcessPool(nodes=num_cores).imap(calc_func, self.detectors)))
            self.inj_params                                       = self.inj_params[0]
            self.deriv_variables                                  = self.deriv_variables[0]

    def constrain_gmst0(self):
        if 'gmst0' in self.inj_params:
            self.inj_params['gmst0_input'] = self.inj_params['gmst0']
            self.inj_params['gmst0'] = self.inj_params['gmst0'] % (2 * np.pi)
        else: self.logger.debug('gmst0 is not in the passed inj_params.')

    def check_none_vars_net(self, labels, ret_bool, tag=''):
        if tag: tag += ': '
        for label in labels:
            if self.__getattribute__(label) is None:
                if ret_bool: return True
                else:        utils.log_msg(f'{tag}{label} is not set!', logger=self.logger, level='ERROR')
        return False

    def check_none_vars_det(self, labels, ret_bool, tag=''):
        if tag: tag += ': '
        for label in labels:
            for det in self.detectors:
                if det.__getattribute__(label) is None:
                    if ret_bool: return True
                    else:        utils.log_msg(f'{tag}{det.det_key} - {label} is not set!', logger=self.logger, level='ERROR')
        return False


    ###
    #-----PSDs and antenna patterns-----
    def setup_ant_pat_lpf_psds(self, F_lo=-np.inf, F_hi=np.inf):
        self.check_none_vars_net(['inj_params'], False, tag='setup_ant_pat_lpf_psds')
        self.check_none_vars_det(['f'], False, tag='setup_ant_pat_lpf_psds')
        for det in self.detectors:
            # the psd has to be set first to avoid inconsistent array lengths
            det.setup_psds(F_lo, F_hi, user_psds=self.user_psds)
            det.setup_ant_pat_lpf(self.inj_params, self.use_rot, user_locs=self.user_locs)
        self.logger.info('PSDs, antenna patterns, and LPFs loaded.')


    ###
    #-----Waveform polarizations-----
    def calc_wf_polarizations(self):
        self.check_none_vars_net(['wf', 'f', 'inj_params'], False, tag='calc_wf_polarizations')
        self.hfp, self.hfc = self.wf.eval_np_func(self.f, utils.get_sub_dict(self.inj_params, self.wf.wf_symbs_string))
        self.logger.info('Polarizations calculated.')

    def calc_wf_polarizations_derivs_num(self, step=1e-9, method='central', order=2, d_order_n=1):
        self.logger.info('Calculate numeric derivatives of polarizations.')
        self.check_none_vars_net(['deriv_symbs_string', 'deriv_variables'], False, tag='calc_wf_polarizations_derivs_num')
        self.calc_wf_polarizations()
        self.del_hfpc = drd.calc_det_responses_derivs_num(None, self.wf, utils.remove_symbols(self.deriv_symbs_string,self.wf.wf_symbs_string),
                                                          self.f, self.inj_params, use_rot=self.use_rot, label='hf',
                                                          step=step, method=method, order=order, d_order_n=d_order_n, user_locs=self.user_locs,
                                                          ana_deriv_symbs_string=self.ana_deriv_symbs_string, ana_deriv_aux={'hfp':self.hfp,'hfc':self.hfc})
        self.del_hfpc, c_quants = edh.get_conv_del_eval_dic(self.del_hfpc, self.inj_params, self.conv_cos, self.conv_log, self.deriv_symbs_string)
        self.inj_params, self.deriv_variables = edh.get_conv_inj_params_deriv_variables(c_quants, self.inj_params, self.deriv_variables)
        self.logger.info('Numeric derivatives of polarizations calculated.')

    def load_wf_polarizations_derivs_sym(self, return_bin=0):
        self.check_none_vars_net(['wf', 'deriv_symbs_string'], False, tag='load_wf_polarizations_derivs_sym')
        self.del_hfpc_expr = drd.load_det_responses_derivs_sym('pl_cr', self.wf.wf_model_name,
                                                               utils.remove_symbols(self.deriv_symbs_string, self.wf.wf_symbs_string),
                                                               self.use_rot, return_bin, self.user_lambdified_functions_path)
        self.logger.info('Lambdified polarizations loaded.')

    def calc_wf_polarizations_derivs_sym(self):
        self.logger.info('Evaluate polarizations.')
        self.check_none_vars_net(['deriv_symbs_string', 'deriv_variables'], False, tag='calc_wf_polarizations_derivs_sym')
        if self.check_none_vars_net(['del_hfpc_expr'], True): self.load_wf_polarizations_derivs_sym()
        self.calc_wf_polarizations()
        self.del_hfpc = { deriv : self.del_hfpc_expr[deriv](self.f, **utils.get_sub_dict(self.inj_params, self.del_hfpc_expr['variables']))
                          for deriv in self.del_hfpc_expr if deriv not in ('variables','deriv_variables')}
        self.del_hfpc, c_quants = edh.get_conv_del_eval_dic(self.del_hfpc, self.inj_params, self.conv_cos, self.conv_log, self.deriv_symbs_string)
        self.inj_params, self.deriv_variables = edh.get_conv_inj_params_deriv_variables(c_quants, self.inj_params, self.deriv_variables)
        self.logger.info('Lambdified polarizations evaluated.')


    ###
    #-----Detector responses-----
    def calc_det_responses(self):
        self.check_none_vars_net(['wf', 'inj_params'], False, tag='calc_det_responses')
        self.check_none_vars_det(['f'], False, tag='calc_det_responses')
        if self.check_none_vars_det(['psd', 'Fp', 'Fc', 'Flp'], True): self.setup_ant_pat_lpf_psds()
        for det in self.detectors:
            det.calc_det_responses(self.wf, self.inj_params)
        self.logger.info('Detector responses calculated.')

    def calc_det_responses_derivs_num(self, step=1e-9, method='central', order=2, d_order_n=1, num_cores=None):
        self.logger.info('Calculate numeric derivatives of detector responses.')
        self.check_none_vars_net(['wf', 'inj_params', 'deriv_symbs_string', 'deriv_variables'], False, tag='calc_det_responses_derivs_num')
        self.check_none_vars_det(['f'], False, tag='calc_det_responses_derivs_num')
        if self.check_none_vars_det(['psd', 'Fp', 'Fc', 'Flp'], True): self.setup_ant_pat_lpf_psds()
        def calc_func(det):
            self.logger.info(f'   {det.det_key}')
            det.calc_det_responses_derivs_num(self.inj_params, self.wf, self.deriv_symbs_string, self.deriv_variables, self.conv_cos, self.conv_log,
                                              self.use_rot, step, method, order, d_order_n, self.user_locs, self.ana_deriv_symbs_string)
            return det, self.inj_params, self.deriv_variables
        self.pool_calc_func(calc_func, num_cores)
        self.logger.info('Numeric derivatives of detector responses calculated.')

    def load_det_responses_derivs_sym(self, return_bin=0):
        self.check_none_vars_net(['wf', 'deriv_symbs_string', 'deriv_variables'], False, tag='load_det_responses_derivs_sym')
        for det in self.detectors:
            det.load_det_responses_derivs_sym(self.wf.wf_model_name, self.deriv_symbs_string, self.use_rot, return_bin, self.user_lambdified_functions_path)
        self.logger.info('Lambdified detector responses loaded.')

    def calc_det_responses_derivs_sym(self, num_cores=None):
        self.logger.info('Evaluate lambdified detector responses.')
        self.check_none_vars_net(['wf', 'inj_params', 'deriv_symbs_string', 'deriv_variables'], False, tag='calc_det_responses_derivs_sym')
        self.check_none_vars_det(['f'], False, tag='calc_det_responses_derivs_sym')
        if self.check_none_vars_det(['psd', 'Fp', 'Fc', 'Flp'], True): self.setup_ant_pat_lpf_psds()
        if self.check_none_vars_det(['del_hf_expr'], True): self.load_det_responses_derivs_sym()
        def calc_func(det):
            self.logger.info(f'   {det.det_key}')
            det.calc_det_responses_derivs_sym(self.wf, self.inj_params, self.deriv_symbs_string, self.deriv_variables, self.conv_cos, self.conv_log)
            return det, self.inj_params, self.deriv_variables
        self.pool_calc_func(calc_func, num_cores)
        self.logger.info('Lambdified detector responses evaluated.')


    ###
    #-----SNR calculations-----
    def calc_snrs(self, only_net=0):
        self.check_none_vars_det(['f'], False, tag='calc_snrs')
        if self.check_none_vars_det(['psd'], True): self.setup_ant_pat_lpf_psds()
        if self.check_none_vars_det(['hf'], True): self.calc_det_responses()
        self.snr_sq = 0
        for det in self.detectors:
             self.snr_sq += det.calc_snrs(only_net)
        self.snr = np.sqrt(self.snr_sq)
        self.logger.info('SNRs calculated.')

    def calc_snr_sq_integrand(self):
        self.check_none_vars_det(['f'], False, tag='calc_snr_sq_integrand')
        if self.check_none_vars_det(['psd'], True): self.setup_ant_pat_lpf_psds()
        if self.check_none_vars_det(['hf'], True): self.calc_det_responses()
        for det in self.detectors:
            det.calc_snr_sq_integrand()
        self.logger.info('SNR integrands calculated.')


    ###
    #-----Error calculation and Fisher analysis-----
    def calc_errors(self, cond_sup=None, only_net=0, derivs=None, step=None, method=None, order=None, num_cores=None):
        self.check_none_vars_net(['deriv_variables'], False, tag='calc_errors')
        self.check_none_vars_det(['f'], False, tag='calc_errors')
        if self.check_none_vars_det(['psd'], True): self.setup_ant_pat_lpf_psds()
        if self.check_none_vars_det(['del_hf'], True):
            if   derivs == 'num' and None not in [step, method, order]:
                self.calc_det_responses_derivs_num(step=step, method=method, order=order, d_order_n=1, num_cores=num_cores)
            elif derivs == 'sym':
                self.load_det_responses_derivs_sym()
                self.calc_det_responses_derivs_sym(num_cores=num_cores)
            else: utils.log_msg('calc_errors: Neither detector response derivatives have been pre-calculated, nor was ' +
                                'the differentiation method specified. Calculate the derivatives beforehand ' +
                                'or specify the derivative type (derivs=[num, sym]) and [step, method, order] for ' +
                                'the numerical differentiation.', logger=self.logger, level='ERROR')
        if self.check_none_vars_net(['snr'], True): self.calc_snrs(only_net=only_net)
        self.logger.info('Calculate errors (Fisher & cov matrices).')
        #-----calculate the error matrices: Fisher and Cov-----
        self.fisher = 0
        for det in self.detectors:
            self.logger.info(f'   {det.det_key}')
            self.fisher += det.calc_fisher_cov_matrices(only_net, cond_sup, logger=self.logger)
        self.cond_num = fat.calc_cond_number(self.fisher, logger=self.logger, tag='network')
        self.cov, self.inv_err = fat.calc_cov_inv_err(self.fisher, self.cond_num, cond_sup=cond_sup, logger=self.logger, tag='network')
        #-----calculate the absolute errors of the various variables-----
        self.errs = fat.get_errs_from_cov(self.cov, self.deriv_variables)
        if not only_net:
            for det in self.detectors:
                det.calc_errs(self.deriv_variables)
        #-----calculate 90%-credible sky area
        if 'ra' in self.deriv_variables and ('cos_dec' in self.deriv_variables or 'dec' in self.deriv_variables):
            if 'cos_dec' in self.deriv_variables: dec_str = 'cos_dec'
            else:                                 dec_str = 'dec'
            ra_id      = self.deriv_variables.index('ra')
            dec_id     = self.deriv_variables.index(dec_str)
            is_cos_dec = (dec_str == 'cos_dec')
            self.errs['sky_area_90'] = edh.sky_area_90(self.errs['ra'], self.errs[dec_str], self.cov[ra_id,dec_id], self.inj_params['dec'], is_cos_dec)
            if not only_net:
                for det in self.detectors:
                    det.calc_sky_area_90_network(ra_id, dec_id, self.inj_params['dec'], is_cos_dec, dec_str)
            self.logger.info('Sky areas calculated.')
        else: self.logger.warning('calc_errors: tag = network - 90%-credible sky area not calculated due to missing RA or DEC (COS_DEC) errors.')
        self.logger.info('Errors calculated.')


    ###
    #-----IO methods-----
    def save_network(self,filename_path):
        '''Save the network under the given path using *dill*.'''
        with open(filename_path, "wb") as fi:
            dill.dump(self, fi, recurse=True)
        self.logger.info('Network pickled.')
        return

    def load_network(filename_path):
        '''Loading the network from the given path using *dill*.'''
        with open(filename_path, "rb") as fi:
            net = dill.load(fi)
        net.logger.info('Network loaded.')
        return net

    def print_network(self):
        sepl='--------------------------------------------------------------------------------------'
        print()
        print(sepl)
        print('Printing network.')
        print(sepl)
        print()
        for key,value in vars(self).items():
            if type(value) == dict:
                print('Key: ',key)
                for kkey in value.keys():
                    print('',kkey)
                    print('',value[kkey])
                print()
            elif value is not None:
                if key == 'wf':
                    print('Key: ',key)
                    for kkey,vvalue in vars(value).items():
                        print('',kkey.ljust(16,' '),'  ',vvalue)
                    print()
                else:
                    print('Key: ',key)
                    print(value)
                    print()
        print(sepl)
        print('Printing network done.')
        print(sepl)
        print()

    def print_detectors(self):
        sepl='--------------------------------------------------------------------------------------'
        sepl1='-------------------------------------------'
        print()
        print(sepl)
        print('Printing detectors.')
        print(sepl)
        for det in self.detectors:
            print(sepl1)
            print(det.det_key)
            print(sepl1)
            det.print_detector(0)
        print(sepl)
        print('Printing detectors done.')
        print(sepl)
        print()
