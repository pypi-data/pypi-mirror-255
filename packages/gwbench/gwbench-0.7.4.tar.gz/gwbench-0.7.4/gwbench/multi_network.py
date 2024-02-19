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

import gwbench.network as nc
import gwbench.utils as utils

# logger
glob_logger = logging.getLogger('multi_network_module')
glob_logger.setLevel('INFO')

class MultiNetwork:

    ###
    #-----Init methods-----
    def __init__(self, network_specs=None, logger_name='MultiNetwork', logger_level='WARNING', logger_level_network='WARNING'):
        ##-----logger-----
        self.logger = utils.get_logger(name=logger_name, level=logger_level)

        ##-----initialize network object-----
        if network_specs is None:
            # network_specs list and list of networks
            self.network_specs = None
            self.networks = None
            # dummy networks for unique locations
            self.loc_net  = None
        elif isinstance(network_specs, list):
            self.set_multi_network_from_specs(network_specs, logger_level_network=logger_level_network)

        if self.networks is None: self.logger.debug('Empty MultiNetwork initialized.')
        else:                     self.logger.debug('MultiNetwork initialized.')

    ###
    #-----Setter methods-----
    #
    # it is best practice to always change the instance variables using these setter methods
    #
    def set_logger_level(self, level):
        utils.set_logger_level(self.logger, level)

    def set_multi_network_from_specs(self, network_specs, logger_level_network='WARNING'):
        # copy network_specs
        self.network_specs = copy(network_specs)
        # prepare list of all networks specified in network_specs
        self.networks = [ nc.Network(network_spec, logger_name='..'.join(network_spec), logger_level=logger_level_network)
                          for network_spec in network_specs ]
        # find unique locations and initialize Network for these with dummy technologies
        self.loc_net = nc.Network(
            list(dict.fromkeys([ f'tec_{det_key.split("_")[1]}' for network_spec in network_specs for det_key in network_spec ])),
            logger_name='loc_net', logger_level=logger_level_network)

    def set_wf_vars(self, wf_model_name, wf_other_var_dic=None, user_waveform=None, cosmo=None):
        for net in [self.loc_net, *self.networks]:
            net.set_wf_vars(wf_model_name, wf_other_var_dic=wf_other_var_dic, user_waveform=user_waveform, cosmo=cosmo)

    def set_net_vars(self, wf_model_name=None, wf_other_var_dic=None, user_waveform=None, cosmo=None,
                     f=None, inj_params=None, deriv_symbs_string=None, conv_cos=None, conv_log=None,
                     use_rot=None, user_locs=None, user_psds=None, user_lambdified_functions_path=None, ana_deriv_symbs_string=None):
        for net in [self.loc_net, *self.networks]:
            net.set_net_vars(wf_model_name=wf_model_name, wf_other_var_dic=wf_other_var_dic, user_waveform=user_waveform, cosmo=cosmo,
                             f=f, inj_params=inj_params, deriv_symbs_string=deriv_symbs_string, conv_cos=conv_cos, conv_log=conv_log,
                             use_rot=use_rot, user_locs=user_locs, user_psds=user_psds, ana_deriv_symbs_string=ana_deriv_symbs_string,
                             user_lambdified_functions_path=user_lambdified_functions_path)


    ###
    #-----Resetter methods for instance variables-----
    def reset_ant_pat_lpf_psds(self):
        for net in [self.loc_net, *self.networks]:
            net.reset_ant_pat_lpf_psds()

    def reset_wf_polarizations(self):
        for net in [self.loc_net, *self.networks]:
            net.reset_wf_polarizations()

    def reset_det_responses(self):
        for net in [self.loc_net, *self.networks]:
            net.reset_det_responses()

    def reset_snrs(self):
        for net in [self.loc_net, *self.networks]:
            net.reset_snrs()

    def reset_errors(self):
        for net in [self.loc_net, *self.networks]:
            net.reset_errors()


    ###
    #-----Helper-----
    def check_none_vars_det(self, labels, ret_bool, tag=''):
        for net in [self.loc_net, *self.networks]:
            if net.check_none_vars_det(labels, ret_bool, tag=''): return True
        return False


    ###
    #-----PSDs and antenna patterns-----
    def setup_ant_pat_lpf_psds(self, F_lo=-np.inf, F_hi=np.inf):
        for net in [self.loc_net, *self.networks]:
            net.setup_ant_pat_lpf_psds(F_lo=F_lo, F_hi=F_hi)
        self.logger.info('PSDs, antenna patterns, and LPFs loaded.')


    ###
    #-----Waveform polarizations-----
    def calc_wf_polarizations(self):
        self.loc_net.calc_wf_polarizations()

    def calc_wf_polarizations_derivs_num(self, step=1e-9, method='central', order=2, d_order_n=1):
        self.loc_net.calc_wf_polarizations_derivs_num(step=step, method=method, order=order, d_order_n=d_order_n)

    def load_wf_polarizations_derivs_sym(self, return_bin=0):
        self.loc_net.load_wf_polarizations_derivs_sym(return_bin=return_bin)

    def calc_wf_polarizations_derivs_sym(self):
        self.loc_net.calc_wf_polarizations_derivs_sym()

    def dist_wf_polarizations(self):
        for net in self.networks:
            net.hfp             =     copy(self.loc_net.hfp)
            net.hfc             =     copy(self.loc_net.hfc)
            net.del_hfpc        = deepcopy(self.loc_net.del_hfpc)
            net.del_hfpc_expr   = deepcopy(self.loc_net.del_hfpc_expr)
            net.inj_params      = deepcopy(self.loc_net.inj_params)
            net.deriv_variables =     copy(self.loc_net.deriv_variables)
        self.logger.info('Polarizations distributed among all networks.')


    ###
    #-----Detector responses-----
    def calc_det_responses(self):
        self.loc_net.calc_det_responses()

    def calc_det_responses_derivs_num(self, step=1e-9, method='central', order=2, d_order_n=1, num_cores=None):
        self.loc_net.calc_det_responses_derivs_num(step=step, method=method, order=order, d_order_n=d_order_n, num_cores=num_cores)

    def load_det_responses_derivs_sym(self, return_bin=0):
        self.loc_net.load_det_responses_derivs_sym(return_bin=return_bin)

    def calc_det_responses_derivs_sym(self, num_cores=None):
        self.loc_net.calc_det_responses_derivs_sym(num_cores=num_cores)

    def dist_det_responses(self):
        if self.check_none_vars_det(['psd'], True): self.setup_ant_pat_lpf_psds()
        for net in self.networks:
            net.inj_params          = deepcopy(self.loc_net.inj_params)
            net.deriv_variables     =     copy(self.loc_net.deriv_variables)
            for det in net.detectors:
                loc_det             = self.loc_net.get_detector(f'tec_{det.loc}')
                f_ids               = np.logical_and(loc_det.f >= det.f[0], loc_det.f <= det.f[-1])
                det.hf              = copy(loc_det.hf[f_ids])
                if loc_det.del_hf is not None:
                    det.del_hf = { deriv : copy(del_hf_deriv[f_ids]) for deriv,del_hf_deriv in loc_det.del_hf.items() }
                det.del_hf_expr     = deepcopy(loc_det.del_hf_expr)
        self.logger.info('Detector responses distributed among all networks.')


    ###
    #-----SNR calculations-----
    def calc_snrs(self, only_net=0):
        if self.check_none_vars_det(['hf'], True):
            self.calc_det_responses()
            self.dist_det_responses()
        for net in self.networks:
            net.calc_snrs(only_net=only_net)
        self.logger.info('SNRs calculated.')

    def calc_snr_sq_integrand(self):
        if self.check_none_vars_det(['hf'], True): self.calc_det_responses()
        for net in self.networks:
            net.calc_snr_sq_integrand()
        self.logger.info('SNR integrands calculated.')


    ###
    #-----Error calculation and Fisher analysis-----
    def calc_errors(self, cond_sup=None, only_net=0, derivs=None, step=None, method=None, order=None, num_cores=None):
        if self.check_none_vars_det(['del_hf'], True):
            if not self.loc_net.check_none_vars_det(['del_hf'], True):
                self.dist_det_responses()
            elif derivs == 'num' and None not in [step, method, order]:
                self.calc_det_responses_derivs_num(step=step, method=method, order=order, d_order_n=1, num_cores=num_cores)
                self.dist_det_responses()
            elif derivs == 'sym':
                self.load_det_responses_derivs_sym()
                self.calc_det_responses_derivs_sym(num_cores=num_cores)
                self.dist_det_responses()
            else: utils.log_msg('calc_errors: Neither detector response derivatives have been pre-calculated, nor was ' +
                                'the differentiation method specified. Calculate the derivatives beforehand ' +
                                'or specify the derivative type (derivs=[num, sym]) and [step, method, order] for ' +
                                'the numerical differentiation.', logger=self.logger, level='ERROR')
        self.logger.info('Calculate errors (Fisher & cov matrices).')
        for net in self.networks:
            net.calc_errors(cond_sup=cond_sup, only_net=only_net)
        self.logger.info('Errors calculated.')


    ###
    #-----IO methods-----
    def save_multi_network(self, filename_path):
        '''Save the network under the given path using *dill*.'''
        with open(filename_path, "wb") as fi:
            dill.dump(self, fi, recurse=True)
        self.logger.info('MultiNetwork pickled.')
        return

    def load_multi_network(filename_path):
        '''Loading the network from the given path using *dill*.'''
        with open(filename_path, "rb") as fi:
            mul_net = dill.load(fi)
        mul_net.logger.info('MultiNetwork loaded.')
        return mul_net
