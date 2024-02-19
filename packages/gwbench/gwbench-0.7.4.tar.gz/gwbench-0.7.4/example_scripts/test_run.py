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
from lal import GreenwichMeanSiderealTime

from gwbench import Network, injections_CBC_params_redshift, M_of_Mc_eta, f_isco_Msolar

np.set_printoptions(linewidth=200)

############################################################################
### User Choices
############################################################################

# injection ID
inj_id = 0

# user's choice: waveform to use
wf_model_name       = 'tf2'
wf_other_var_dic    = None
deriv_symbs_string  = 'Mc eta chi1z chi2z DL tc phic iota ra dec psi'
conv_log            = ('Mc','DL')
use_rot             = 1
only_net            = 1
step                = 1e-9
method              = 'central'
order               = 2
cosmo_dict          = {'zmin':0, 'zmax':0.2, 'sampler':'uniform_comoving_volume_inversion'}
mass_dict           = {'dist':'uniform', 'mmin':5, 'mmax':100}
spin_dict           = {'dim':1, 'geom':'cartesian', 'chi_lo':-0.75, 'chi_hi':0.75}
redshifted          = 1
num_injs            = 100
seed                = 29378
file_path           = None
injections_data     = injections_CBC_params_redshift(cosmo_dict,mass_dict,spin_dict,redshifted,num_injs,seed,file_path)

############################################################################
### injection parameters
############################################################################

inj_params = {
    'Mc'    : injections_data[0][inj_id],
    'eta'   : injections_data[1][inj_id],
    'chi1x' : injections_data[2][inj_id],
    'chi1y' : injections_data[3][inj_id],
    'chi1z' : injections_data[4][inj_id],
    'chi2x' : injections_data[5][inj_id],
    'chi2y' : injections_data[6][inj_id],
    'chi2z' : injections_data[7][inj_id],
    'DL'    : injections_data[8][inj_id],
    'tc'    : 0.,
    'phic'  : 0.,
    'iota'  : injections_data[9][inj_id],
    'ra'    : injections_data[10][inj_id],
    'dec'   : injections_data[11][inj_id],
    'psi'   : injections_data[12][inj_id],
    'gmst0' : GreenwichMeanSiderealTime(1247227950.),
    'z'     : injections_data[13][inj_id],
    }

print('injections parameter: ', inj_params)
print()

f_lo = 1.
f_hi = f_isco_Msolar(M_of_Mc_eta(inj_params['Mc'],inj_params['eta']))
df   = 2.**-4
f    = np.arange(f_lo,f_hi+df,df)

print('f_lo:', f_lo, '   f_hi:', f_hi, '   df:', df)
print()

############################################################################
### Network specification
############################################################################

network_spec = ['CE2-40-CBO_C','CE2-40-CBO_N','CE2-40-CBO_S']
print('network spec: ', network_spec)
print()

############################################################################
### Numeric GW Benchmarking
############################################################################

# initialize Network and do general setup
net = Network(network_spec, logger_name='3_40km_CE', logger_level='WARNING')
net.set_net_vars(wf_model_name=wf_model_name, f=f, inj_params=inj_params,
                 deriv_symbs_string=deriv_symbs_string, conv_log=conv_log, use_rot=use_rot)
net.calc_errors(only_net=only_net, derivs='num', step=1e-9, method='central', order=2)

############################################################################
### Check results
############################################################################

# stored from previous evaluation for tf2 waveform and inj_id=0
snr  = 2557
errs = {
    'log_Mc'      : 0.00193,
    'eta'         : 0.081,
    'chi1z'       : 1.396,
    'chi2z'       : 2.076,
    'log_DL'      : 0.0318,
    'tc'          : 0.0059,
    'phic'        : 16.527,
    'iota'        : 0.133,
    'ra'          : 0.000923,
    'dec'         : 0.000515,
    'psi'         : 0.543,
    'sky_area_90' : 0.00709,
    }

rtol = 1e-2
atol = 0
print(f'Check if calculated and stored values agree up to a relative error of {rtol}.')
print(f'{"Network SNR".ljust(19)} calculated={str(net.snr).ljust(22)} stored={str(snr).ljust(18)} agree={np.isclose(net.snr, snr, atol=atol, rtol=rtol)}.')
for key in errs:
    cval = net.errs[key]
    sval = errs[key]
    print(f'Error {key.ljust(13)} calculated={str(cval).ljust(22)} stored={str(sval).ljust(18)} agree={np.isclose(cval, sval, atol=atol, rtol=rtol)}.')
