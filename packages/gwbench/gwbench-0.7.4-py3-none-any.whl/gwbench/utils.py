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


import logging
import os
import sys
from logging import getLevelName

import numpy as np

################################################################################
# available detectors technologies and locations
################################################################################

available_tecs = (
    'aLIGO', 'A+', 'V+', 'K+',
    'A#', 'Voyager-CBO', 'Voyager-PMO',
    'ET', 'ET-10-XYL', 'CEwb',
    'CE-40', 'CE-40-LF', 'CE-20', 'CE-20-PM',
    'CE1-10-CBO', 'CE1-20-CBO', 'CE1-30-CBO', 'CE1-40-CBO',
    'CE2-10-CBO', 'CE2-20-CBO', 'CE2-30-CBO', 'CE2-40-CBO',
    'CE1-10-PMO', 'CE1-20-PMO', 'CE1-30-PMO', 'CE1-40-PMO',
    'CE2-10-PMO', 'CE2-20-PMO', 'CE2-30-PMO', 'CE2-40-PMO',
    'LISA-17', 'LISA-Babak17', 'LISA-Robson18'
    )

available_locs = (
    'H', 'L', 'V', 'K', 'I', 'LHO', 'LLO', 'LIO',
    'ET1', 'ET2', 'ET3', 'ETS1', 'ETS2', 'ETS3',
    'C', 'N', 'S', 'CEA', 'CEB', 'CES'
    )

################################################################################
# constants
################################################################################

#-----constants in SI units-----
GNewton    = 6.6743e-11
cLight     = 2.99792458e8
Msun       = 1.9884099021470415e+30
Mpc        = 3.085677581491367e+22
REarth     = 6378136.6
AU         = 1.4959787066e11
year       = 3.1536e7
hPlanck    = 6.62607015e-34
TEarth     = 86400.
halfTEarth = TEarth / 2

#-----convert mass in solar masses to seconds-----
MTsun    = Msun * GNewton/cLight**3.
time_fac = MTsun
#-----convert mass/distance in solar mass/Mpc to dimensionless-----
strain_fac = GNewton/cLight**2.*Msun/Mpc


################################################################################
# basic functions
################################################################################

#-----combine two sympy symbols strings without duplicates-----
def reduce_symbols_strings(string1,string2):
    # combine the two lists
    symbols_list = string1.split(' ') + string2.split(' ')
    # remove duplicates
    symbols_list = list(dict.fromkeys(symbols_list))

    # recreate a string of symbols and return it
    return ' '.join(symbols_list)

#-----delete symbols in sympy symbols strings, if not present in the other-----
def remove_symbols(string1,string2,keep_same=1):
    symbs_list1 = string1.split(' ')
    symbs_list2 = string2.split(' ')
    # remove unwanted symbols from 1
    if keep_same:
        symbols_list = [x for x in symbs_list1 if x in symbs_list2]
    else:
        symbols_list = [x for x in symbs_list1 if x not in symbs_list2]

    # recreate a string of symbols and return it
    return ' '.join(symbols_list)

#-----get subarray-----
def get_sub_array_ids(arr,sub_arr):
    return np.logical_and(arr>=sub_arr[0],arr<=sub_arr[-1])

#-----use only subset of dictionary-----
def get_sub_dict(dic,key_list,keep_in_list=1):
    if type(key_list) == str:
        key_list = key_list.split(' ')

    if keep_in_list:
        return {k:v for k,v in dic.items() if k in key_list}
    else:
        return {k:v for k,v in dic.items() if k not in key_list}

#-----check if list is subset of another list-----
def is_subset_lists(sub, sup):
    return all([el in sup for el in sub])


################################################################################
# waveform manipluations
################################################################################

#-----get amp/pha for pl and cr polarizations (since they are complex)-----
def transform_hfpc_to_amp_pha(hfpc, f, params_list):
    hfp, hfc = hfpc(f, *params_list)
    return pl_cr_to_amp_pha(hfp, hfc)

def pl_cr_to_amp_pha(hfp, hfc):
    hfp_amp, hfp_pha = amp_pha_from_z(hfp)
    hfc_amp, hfc_pha = amp_pha_from_z(hfc)
    return hfp_amp, hfp_pha, hfc_amp, hfc_pha

#-----convert amp/phase derivatives to re/im ones-----
def z_deriv_from_amp_pha(amp,pha,del_amp,del_pha):
    del_z = np.zeros(del_amp.shape,dtype=np.complex_)
    if len(del_amp.shape) == 2:
        for i in range(del_amp.shape[1]):
            del_z[:,i] = del_amp[:,i] * np.exp(1j*pha) + amp * np.exp(1j*pha) * 1j * del_pha[:,i]
        return del_z
    else:
        return del_amp * np.exp(1j*pha) + amp * np.exp(1j*pha) * 1j * del_pha

#-----re/im vs. amp/phase transformations-----
def re_im_from_amp_pha(amp,pha):
    return re_im_from_z(z_from_amp_pha(amp,pha))

def amp_pha_from_re_im(re,im):
    return amp_pha_from_z(z_from_re_im(re,im))

#-----re/im or amp/phase vs. complex number transformations-----
def re_im_from_z(z):
    return np.real(z), np.imag(z)

def z_from_re_im(re,im):
    return re + 1j * im

def amp_pha_from_z(z):
    return np.abs(z), np.unwrap(np.angle(z))

def z_from_amp_pha(amp,pha):
    return amp * np.exp(1j*pha)


################################################################################
# IO functions
################################################################################

#-----Block and unblock printing-----
def block_print(active=1):
    if active: sys.stdout = open(os.devnull, 'w')
    return

def unblock_print(active=1):
    if active: sys.stdout = sys.__stdout__
    return

#-----sending warning or error message-----
def log_msg(message, logger=None, level='INFO'):
    if logger is None: print(level + ': ' + message)
    else:              logger.log(getLevelName(level), message)
    if level in ['ERROR', 'CRITICAL']: sys.exit()

def get_logger(name, level='INFO', stdout=True, logfile=None):
    logging.basicConfig(format = '%(asctime)s - %(name)s - %(levelname)s : %(message)s')
    if stdout: logging.basicConfig(stream = sys.stdout)
    if logfile is not None: logging.basicConfig(filename = logfile, filemode = 'w')
    logger = logging.getLogger(name)
    set_logger_level(logger, level)
    return logger

def set_logger_level(logger, level):
    logger.setLevel(level)


################################################################################
# network_spec handlers
################################################################################

def read_det_keys_from_label(network_label):
    det_keys = []

    ##-----read the network label and find all detectors-----
    keys = list(network_label)

    # - in network list means that all 2G detectors up to that index are to be
    # taken at aLIGO sensitivity
    aLIGO = int('-' in keys)
    if aLIGO: aLIGO_id = keys.index('-')

    # + in network list means that all 2G detectors up to that index are to be
    # taken at A+ sensitivity
    a_pl = int('+' in keys)
    if a_pl: a_pl_id = keys.index('+')

    # v in network list means that all 2G detectors up to that index are to be
    # taken at Voyager sensitivity
    voy = int('v' in keys)
    if voy:
        voy_id = keys.index('v')
        tmp = int(keys[voy_id+1] == 'p')
        voy_pmo = tmp * 'PMO' + (1-tmp) * 'CBO'

    # find out which locations with which PSDs are in the network
    for loc in available_locs:
        if loc in keys:
            loc_id = keys.index(loc)

            if loc in ('H','L','V','K','I'):
                if aLIGO and loc_id < aLIGO_id:
                    name = 'aLIGO_'+loc
                elif a_pl and loc_id < a_pl_id:
                    if loc == 'V':
                        name = 'V+_'+loc
                    elif loc == 'K':
                        name = 'K+_'+loc
                    else:
                        name = 'A+_'+loc
                elif voy and loc_id < voy_id:
                    name = 'Voyager-{}_{}'.format(voy_pmo,loc)

            elif loc in ('C','N','S'):
                if keys[loc_id+1] == 'c':
                    name = f'CE-{keys[loc_id+2]}0'
                    if   keys[loc_id+2] == 'l': name += '-LF'
                    elif keys[loc_id+2] == 'p': name += '-PM'
                    name += f'_{loc}'
                else:
                    ce_a = int(keys[loc_id+1] == 'a') # 0 for i, 1 for a - CE1 as i, CE2 as a
                    ce_arm = int(keys[loc_id+2])*10  # arm length (n for n*10km)
                    tmp = int(keys[loc_id+3] == 'p')
                    ce_pmo = tmp * 'PMO' + (1-tmp) * 'CBO'
                    name = f'CE{ce_a+1}-{ce_arm}-{ce_pmo}_{loc}'

            det_keys.append(name)

    # add 3 ET detectors
    if 'E' in keys:
        for name in ['ET_ET1','ET_ET2','ET_ET3']:
            det_keys.append(name)

    return det_keys
