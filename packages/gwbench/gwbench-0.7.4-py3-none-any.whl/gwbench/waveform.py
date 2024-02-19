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

import importlib.util
import os

import sympy as sp

from gwbench.utils import log_msg

from gwbench.wf_models import lal_bbh_np
from gwbench.wf_models import lal_bns_np
from gwbench.wf_models import tf2_np
from gwbench.wf_models import tf2_sp
from gwbench.wf_models import tf2_tidal_np
from gwbench.wf_models import tf2_tidal_sp

###
#-----Get waveform functions for np, sp and the symbols string based on the model name-----
def select_wf_model_quants(wf_model_name, user_waveform=None, cosmo=None, logger=None):

    if user_waveform is None:
        if wf_model_name == 'lal_bbh':
            np_mod = lal_bbh_np
            sp_mod = None
        elif wf_model_name == 'lal_bns':
            np_mod = lal_bns_np
            sp_mod = None
        elif wf_model_name == 'tf2':
            np_mod = tf2_np
            sp_mod = tf2_sp
        elif wf_model_name == 'tf2_tidal':
            np_mod = tf2_tidal_np
            sp_mod = tf2_tidal_sp
        else: log_msg(f'select_wf_model_quants: wf_model_name {wf_model_name} is not known!', logger=logger, level='ERROR')
    else:
        if 'np' in user_waveform: np_mod = load_module_from_file(user_waveform['np'])
        else: log_msg('select_wf_model_quants: user_waveform does not contain key = "np": numpy version of the waveform is needed!',
                      logger=logger, level='ERROR')

        if 'sp' in user_waveform: sp_mod = load_module_from_file(user_waveform['sp'])
        else:                     sp_mod = None

    if sp_mod is None: sp_hfpc = None
    else:              sp_hfpc = sp_mod.hfpc

    return np_mod.wf_symbs_string, np_mod.hfpc, sp_hfpc

def load_module_from_file(file_path):
    spec   = importlib.util.spec_from_file_location(os.path.splitext(os.path.basename(file_path))[0], file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Waveform(object):

    ###
    #-----Init methods-----
    def __init__(self, wf_model_name=None, wf_other_var_dic=None, user_waveform=None, cosmo=None, logger=None):
        if wf_model_name is None:
            wf_symbs_string = None
            hfpc_np         = None
            hfpc_sp         = None
        else:
            wf_symbs_string, hfpc_np, hfpc_sp = \
                select_wf_model_quants(wf_model_name, user_waveform=user_waveform, cosmo=cosmo, logger=logger)

        self.wf_model_name    = wf_model_name
        self.wf_other_var_dic = wf_other_var_dic
        self.user_waveform    = user_waveform
        self.wf_symbs_string  = wf_symbs_string
        self.hfpc_np          = hfpc_np
        self.hfpc_sp          = hfpc_sp


    ###
    #-----Getter methods-----
    def get_sp_expr(self):
        if self.hfpc_sp is None: log_msg('get_sp_expr: Waveform does not have a sympy expression!', level='ERROR')

        symb_dic = {}
        for name in self.wf_symbs_string.split(' '):
            symb_dic[name] = sp.symbols(name,real=True)

        if self.wf_other_var_dic is None: return self.hfpc_sp(*list(symb_dic.values()))
        else:                             return self.hfpc_sp(*list(symb_dic.values()), *list(self.wf_other_var_dic.values()))

    def eval_np_func(self, f, inj_params):
        if isinstance(inj_params, dict):
            if self.wf_other_var_dic is None: return self.hfpc_np(f, **inj_params)
            else:                             return self.hfpc_np(f, **inj_params, **self.wf_other_var_dic)
        elif isinstance(inj_params, list):
            if self.wf_other_var_dic is None: return self.hfpc_np(f, *inj_params)
            else:                             return self.hfpc_np(f, *inj_params, **self.wf_other_var_dic)


    ###
    #-----IO methods-----
    def print_waveform(self):
        for key,value in vars(self).items():
            print(key.ljust(16,' '),'  ',value)
            print()
