import ROOT
import zfit
import numpy

from normalizer    import normalizer
from rk_model      import rk_model
from model_manager import manager
from np_reader     import np_reader as np_rdr
from rk_model      import rk_model  as model

import utils_noroot      as utnr
import zutils.utils      as zut
import matplotlib.pyplot as plt
import rk.utilities      as rkut
import math
import pytest
import pprint
import os

#----------------------------------------------------
def rename_keys(d_data, use_txs=True):
    d_rename = {}
    if use_txs:
        d_rename[  'r1_TOS'] = d_data['d1']
        d_rename[  'r1_TIS'] = d_data['d1']

        d_rename['r2p1_TOS'] = d_data['d2']
        d_rename['r2p1_TIS'] = d_data['d2']

        d_rename['2017_TOS'] = d_data['d3']
        d_rename['2017_TIS'] = d_data['d3']
    
        d_rename['2018_TOS'] = d_data['d4']
        d_rename['2018_TIS'] = d_data['d4']
    else:
        d_rename[  'r1']     = d_data['d1']
        d_rename['r2p1']     = d_data['d2']
        d_rename['2017']     = d_data['d3']
        d_rename['2018']     = d_data['d4']

    return d_rename
#-----------------------------
def delete_all_pars():
    d_par = zfit.Parameter._existing_params
    l_key = list(d_par.keys())

    for key in l_key:
        del(d_par[key])
#----------------------------------------------------
def rename_keys(d_data, use_txs=True):
    d_rename = {}
    if use_txs:
        d_rename[  'r1_TOS'] = d_data['d1']
        d_rename[  'r1_TIS'] = d_data['d1']

        d_rename['r2p1_TOS'] = d_data['d2']
        d_rename['r2p1_TIS'] = d_data['d2']

        d_rename['2017_TOS'] = d_data['d3']
        d_rename['2017_TIS'] = d_data['d3']

        d_rename['2018_TOS'] = d_data['d4']
        d_rename['2018_TIS'] = d_data['d4']
    else:
        d_rename[  'r1']     = d_data['d1']
        d_rename['r2p1']     = d_data['d2']
        d_rename['2017']     = d_data['d3']
        d_rename['2018']     = d_data['d4']

    return d_rename
#-----------------------------
def skip_test():
    try:
        uname = os.environ['USER']
    except:
        pytest.skip()

    if uname in ['angelc', 'campoverde']:
        return

    pytest.skip()
#----------------------
def get_const(d_val, d_var):
    d_err = { name : math.sqrt(var) for name, var in d_var.items() }

    d_con = {}
    for name in d_val:
        val = d_val[name]
        err = d_err[name]

        d_con[name] = [val, err]

    return d_con
#----------------------
def print_models(d_mod, d_val, d_var):
    d_const = get_const(d_val, d_var)

    dir_path = 'tests/normalizer/simple'
    os.makedirs(dir_path, exist_ok=True)
    for name, (model_mm, model_ee) in d_mod.items():
        zut.print_pdf(model_mm, txt_path=f'{dir_path}/{name}_mm.txt', d_const=d_const)
        zut.print_pdf(model_ee, txt_path=f'{dir_path}/{name}_ee.txt', d_const=d_const)
#----------------------
def get_model(dset, bdt_bin=None):
    rdr          = np_rdr(sys='v65', sta='v63', yld='v24')
    rdr.cache    = True
    rdr.cache_dir= './v65_v63_v24' 
    d_eff        = rdr.get_eff()
    d_byld       = rdr.get_byields()
    d_nent       = rkut.average_byields(d_byld, l_exclude=['TIS'])
    d_rare_yld   = rkut.reso_to_rare(d_nent, kind='jpsi')

    mod         = rk_model(preffix='simple', d_eff=d_eff, d_nent=d_rare_yld, l_dset=[dset])
    mod.bdt_bin = bdt_bin 
    d_mod       = mod.get_model()
    d_val, d_var= mod.get_cons() 

    return d_mod, d_val, d_var
#----------------------
def get_fake_inputs():
    d_eff       = model.get_eff()
    d_yld       = {'d1' :          2e2, 'd2' :            2e2, 'd3' :            2e2, 'd4' :            2e2}
    d_mcmu      = {'d1' : (5000, 4900), 'd2' :   (5100, 4900), 'd3' :   (5100, 4800), 'd4' :   (5200, 5100)}
    d_mcsg      = {'d1' :    (10,  40), 'd2' :       (10, 18), 'd3' :       (20, 30), 'd4' :       (30, 40)}

    d_eff       = rename_keys(d_eff)
    d_yld       = rename_keys(d_yld, use_txs=False)
    d_mcmu      = rename_keys(d_mcmu)
    d_mcsg      = rename_keys(d_mcsg)

    mod         = manager(preffix='simple', d_eff=d_eff, d_nent=d_yld, dset='all_TOS')
    mod.fake    = True
    d_dat       = mod.get_data()
    d_mod       = mod.get_model()

    return d_mod, d_dat
#---------------------
def test_simple():
    d_mod, d_dat   = get_fake_inputs() 

    obj         = normalizer(dset='all', trig='ETOS', d_model=d_mod, d_val={}, d_var={})
    obj.out_dir = 'tests/normalizer/simple'
    obj.data    = d_dat
    res         = obj.get_fit_result()

    delete_all_pars()
#----------------------
def test_all_dset():
    dset = 'all_TOS'
    d_mod, d_val, d_var = get_model(dset)
    mod_mm, mod_ee      = d_mod[dset]

    obj = normalizer(dset='all', trig='ETOS', model=mod_ee, d_val=d_val, d_var=d_var)
    obj.out_dir = 'tests/normalizer/all'
    res = obj.get_fit_result()

    delete_all_pars()
#----------------------
def main():
    test_simple()
    test_wp()
    test_all_dset()
#----------------------
if __name__ == '__main__':
    main()

