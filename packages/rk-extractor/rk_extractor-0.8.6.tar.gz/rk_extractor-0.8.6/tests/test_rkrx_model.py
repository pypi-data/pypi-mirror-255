import ROOT
import zfit

from rkex_model import model
from mc_reader  import mc_reader as mc_rdr
from np_reader  import np_reader as np_rdr
from cs_reader  import cs_reader as cs_rdr

import rk.utilities as rkut
import pytest
import pprint
import os

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
def test_simple():
    d_eff = {'d1' :   (0.5, 0.4), 'd2' :   (0.4, 0.3), 'd3' :   (0.3, 0.2), 'd4' :   (0.2, 0.1)}
    d_nent= {'d1' :          1e4, 'd2' :          1e4, 'd3' :          1e4, 'd4' :          1e4}
    d_mcmu= {'d1' : (5000, 4900), 'd2' : (5100, 4900), 'd3' : (5100, 4800), 'd4' : (5200, 5100)}
    d_mcsg= {'d1' :      (2,  4), 'd2' :     (1, 1.8), 'd3' :       (2, 3), 'd4' :       (3, 4)}

    d_eff =rename_keys(d_eff)
    d_nent=rename_keys(d_nent, use_txs=False)
    d_mcmu=rename_keys(d_mcmu)
    d_mcsg=rename_keys(d_mcsg)

    mod         = model(preffix='simple', d_eff=d_eff, d_mcmu=d_mcmu, d_mcsg=d_mcsg, d_nent=d_nent)
    d_mod       = mod.get_model()

    delete_all_pars()
#----------------------
def test_print():
    d_eff = {'d1' :   (0.5, 0.4), 'd2' :   (0.4, 0.3), 'd3' :   (0.3, 0.2), 'd4' :   (0.2, 0.1)}
    d_nent= {'d1' :          1e4, 'd2' :          1e4, 'd3' :          1e4, 'd4' :          1e4}
    d_mcmu= {'d1' : (5000, 4900), 'd2' : (5100, 4900), 'd3' : (5100, 4800), 'd4' : (5200, 5100)}
    d_mcsg= {'d1' :      (2,  4), 'd2' :     (1, 1.8), 'd3' :       (2, 3), 'd4' :       (3, 4)}

    d_eff =rename_keys(d_eff)
    d_nent=rename_keys(d_nent, use_txs=False)
    d_mcmu=rename_keys(d_mcmu)
    d_mcsg=rename_keys(d_mcsg)

    mod         = model(preffix='simple', d_eff=d_eff, d_mcmu=d_mcmu, d_mcsg=d_mcsg, d_nent=d_nent)
    d_mod       = mod.get_model()
    model.show(d_mod)

    delete_all_pars()
#----------------------
def test_data():
    d_eff = {'d1' :   (0.5, 0.4), 'd2' :   (0.4, 0.3), 'd3' :   (0.3, 0.2), 'd4' :   (0.2, 0.1)}
    d_nent= {'d1' :          1e4, 'd2' :          1e4, 'd3' :          1e4, 'd4' :          1e4}
    d_mcmu= {'d1' : (5000, 4900), 'd2' : (5100, 4900), 'd3' : (5100, 4800), 'd4' : (5200, 5100)}
    d_mcsg= {'d1' :      (2,  4), 'd2' :     (1, 1.8), 'd3' :       (2, 3), 'd4' :       (3, 4)}

    d_eff =rename_keys(d_eff)
    d_nent=rename_keys(d_nent, use_txs=False)
    d_mcmu=rename_keys(d_mcmu)
    d_mcsg=rename_keys(d_mcsg)

    mod         = model(preffix='simple', d_eff=d_eff, d_mcmu=d_mcmu, d_mcsg=d_mcsg, d_nent=d_nent, d_dtmu=d_mcmu, d_dtsg=d_mcsg)
    mod.out_dir = 'tests/rkex_model/simple' 
    d_dat       = mod.get_data()
    d_mod       = mod.get_model()

    delete_all_pars()
#----------------------
def test_real():
    skip_test()

    rdr           = np_rdr(sys='v65', sta='v63', yld='v24')
    rdr.cache     = True 
    rdr.cache_dir = 'tests/np_reader/cache'
    d_eff         = rdr.get_eff()
    d_byld        = rdr.get_byields()
    d_byld_avg    = rkut.average_byields(d_byld, l_exclude=['TIS'])
    d_rare_yld    = rkut.reso_to_rare(d_byld_avg, kind='jpsi')

    rdr           = mc_rdr(version='v4')
    rdr.cache     = False 
    d_mcmu        = rdr.get_parameter(name='mu')
    d_mcsg        = rdr.get_parameter(name='sg')

    mod           = model(preffix='real', d_eff=d_eff, d_mcmu=d_mcmu, d_mcsg=d_mcsg, d_nent=d_rare_yld)
    mod.out_dir   = 'tests/rkex_model/real' 
    d_dat         = mod.get_data()
    d_mod         = mod.get_model()

    delete_all_pars()
#----------------------
def test_pars():
    d_eff = {'d1' :   (0.5, 0.4), 'd2' :   (0.4, 0.3), 'd3' :   (0.3, 0.2), 'd4' :   (0.2, 0.1)}
    d_nent= {'d1' :          1e4, 'd2' :          1e4, 'd3' :          1e4, 'd4' :          1e4}
    d_mcmu= {'d1' : (5280, 5270), 'd2' : (5280, 5275), 'd3' : (5278, 5282), 'd4' : (5270, 5260)}
    d_mcsg= {'d1' :    (20,  40), 'd2' :     (10, 18), 'd3' :     (20, 30), 'd4' :     (30, 40)}

    d_eff =rename_keys(d_eff)
    d_nent=rename_keys(d_nent, use_txs=False)
    d_mcmu=rename_keys(d_mcmu)
    d_mcsg=rename_keys(d_mcsg)
    d_dtmu=d_mcmu
    d_dtsg=d_mcsg

    mod         = model(preffix='pars', d_eff=d_eff, d_mcmu=d_mcmu, d_mcsg=d_mcsg, d_dtmu=d_dtmu, d_dtsg=d_dtsg, d_nent=d_nent)
    mod.out_dir = 'tests/rkex_model/pars' 
    d_dat       = mod.get_data()
    d_mod       = mod.get_model()
    d_par       = mod.get_prefit_pars()

    pprint.pprint(d_par)

    delete_all_pars()
#----------------------
def test_const():
    d_eff = {'d1' :   (0.5, 0.4), 'd2' :   (0.4, 0.3), 'd3' :   (0.3, 0.2), 'd4' :   (0.2, 0.1)}
    d_nent= {'d1' :          1e4, 'd2' :          1e4, 'd3' :          1e4, 'd4' :          1e4}
    d_mcmu= {'d1' : (5280, 5270), 'd2' : (5280, 5275), 'd3' : (5278, 5282), 'd4' : (5270, 5260)}
    d_mcsg= {'d1' :    (20,  40), 'd2' :     (10, 18), 'd3' :     (20, 30), 'd4' :     (30, 40)}

    d_eff =rename_keys(d_eff)
    d_nent=rename_keys(d_nent, use_txs=False)
    d_mcmu=rename_keys(d_mcmu)
    d_mcsg=rename_keys(d_mcsg)
    d_dtmu=d_mcmu
    d_dtsg=d_mcsg

    rdr         = cs_rdr(version='v4', preffix='const')
    _, d_var    = rdr.get_constraints()

    rdr         = np_rdr(sys='v65', sta='v63', yld='v24')
    rdr.cache   = True
    cv_sys      = rdr.get_cov(kind='sys')
    cv_sta      = rdr.get_cov(kind='sta')

    mod         = model(preffix='const', d_eff=d_eff, d_mcmu=d_mcmu, d_mcsg=d_mcsg, d_dtmu=d_dtmu, d_dtsg=d_dtsg, d_nent=d_nent)
    d_par       = mod.get_prefit_pars(d_var=d_var, ck_cov=cv_sys + cv_sta)

    pprint.pprint(d_par)

    delete_all_pars()
#----------------------
def main():
    test_print()
    test_simple()
    test_const()
    test_data()
    test_real()
    test_pars()
#----------------------
if __name__ == '__main__':
    main()

