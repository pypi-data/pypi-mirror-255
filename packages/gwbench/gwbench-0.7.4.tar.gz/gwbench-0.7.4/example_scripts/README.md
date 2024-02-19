## Examples:

- Basic script to calculate antenna patterns, location phase factors, and PSDs:  
`python compute_ant_pat_lpf_psd.py`  

- Basic GW benchmarking with numeric derivatives:  
`python quick_start.py`  

- More elaborate GW benchmarking with numeric derivatives:  
`python num_gw_benchmarking.py`  

- Needed before symbolic GW benchmarking:  
`python generate_lambdified_functions.py`  

- More elaborate GW benchmarking with symbolic derivatives (otherwise the same as the numeric example):  
`python sym_gw_benchmarking.py`  

- Multi network GW benchmarking, setup with symbolic derivatives (can be switched to numeric):  
`python multi_network.py`  


**Available detector locations:**  
- standard sites:  
'H', 'L', 'V', 'K', 'I', 'LHO', 'LLO', 'LIO'  

- fiducial sites:  
'ET1', 'ET2', 'ET3', 'U', 'A', 'W', 'B', 'C', 'N', 'S', 'ETS1', 'ETS2', 'ETS3', 'CEA', 'CEB', 'CES'  

**Available detector technologies (PSDs):**  
- 2G/2G+/2G#:  
'aLIGO', 'A+', 'V+', 'K+', 'A#'  

- Voyager:  
'Voyager-CBO', 'Voyager-PMO'  

- 3G:  
'ET', 'ET-10-XYL', 'CEwb',  
'CE-40', 'CE-40-LF', 'CE-20', 'CE-20-PM',  
'CE1-10-CBO', 'CE1-20-CBO', 'CE1-30-CBO', 'CE1-40-CBO'  
'CE1-10-PMO', 'CE1-20-PMO', 'CE1-30-PMO', 'CE1-40-PMO'  
'CE2-10-CBO', 'CE2-20-CBO', 'CE2-30-CBO', 'CE2-40-CBO'  
'CE2-10-PMO', 'CE2-20-PMO', 'CE2-30-PMO', 'CE2-40-PMO'  

- LISA:  
'LISA-17', 'LISA-Babak17', 'LISA-Robson18'  
