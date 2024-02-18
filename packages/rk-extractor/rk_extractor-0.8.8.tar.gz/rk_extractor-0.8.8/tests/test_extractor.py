from extractor import extractor as ext

import os
import numpy
import zfit
import math
import pprint
import pytest
import utils_noroot as utnr
import rk.utilities as rkut

from logzero    import logger    as log
from cmb_ck     import combiner  as cmb_ck
from np_reader  import np_reader as np_rdr
from mc_reader  import mc_reader as mc_rdr
from cs_reader  import cs_reader as cs_rdr
from rk_model   import rk_model  as model
from cmb_ck     import combiner  as cmb_ck

#-----------------------------
def delete_all_pars():
    d_par = zfit.Parameter._existing_params
    l_key = list(d_par.keys())

    for key in l_key:
        del(d_par[key])
#-----------------------------
def skip_test():
    try:
        uname = os.environ['USER']
    except:
        pytest.skip()

    if uname in ['angelc', 'campoverde']:
        return
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
#----------------------------------------------------
def check_close(value, target, abs_tol=1e-4):
    pas_val = math.isclose(value, target, abs_tol = abs_tol)
    if not pas_val:
        log.error(f'{value:.6f} != {target:.6f}')
        raise
#----------------------------------------------------
def test_simple():
    log.info('Running: test_simple')
    d_eff       = model.get_eff()
    d_yld       = {'d1' :          2e2, 'd2' :            2e2, 'd3' :            2e2, 'd4' :            2e2} 
    d_mcmu      = {'d1' : (5000, 4900), 'd2' :   (5100, 4900), 'd3' :   (5100, 4800), 'd4' :   (5200, 5100)}
    d_mcsg      = {'d1' :    (10,  40), 'd2' :       (10, 18), 'd3' :       (20, 30), 'd4' :       (30, 40)} 

    d_eff       = rename_keys(d_eff)
    d_yld       = rename_keys(d_yld, use_txs=False)
    d_mcmu      = rename_keys(d_mcmu)
    d_mcsg      = rename_keys(d_mcsg)

    mod         = model(preffix='simple', d_eff=d_eff, d_nent=d_yld, l_dset=['2018_TOS'])
    d_dat       = mod.get_data()
    d_mod       = mod.get_model()

    obj         = ext(dset=['2018_TOS'])
    obj.eff     = d_eff 
    obj.data    = d_dat
    obj.model   = d_mod 
    obj.plt_dir = 'tests/extractor/simple'

    result      = obj.get_fit_result()
    result.hesse()

    print(result)

    delete_all_pars()
#----------------------------------------------------
def test_fix_pars():
    skip_test()
    log.info('Running: test_const')
    l_dset = ['all_TOS']

    rdr          = np_rdr(sys='v65', sta='v63', yld='v24')
    rdr.cache_dir= './v65_v63_v24' 
    rdr.cache    = True
    cv_sys       = rdr.get_cov(kind='sys')
    cv_sta       = rdr.get_cov(kind='sta')
    d_eff        = rdr.get_eff()
    d_rjpsi      = rdr.get_rjpsi()
    d_byld       = rdr.get_byields()
    d_nent       = rkut.average_byields(d_byld, l_exclude=['TIS'])
    d_rare_yld   = rkut.reso_to_rare(d_nent, kind='jpsi')

    mod          = model(preffix='const', d_eff=d_eff, d_nent=d_rare_yld, l_dset=l_dset)
    d_mod        = mod.get_model()
    d_dat        = mod.get_data()
    d_val, d_var = mod.get_cons()

    if l_dset == ['all_TOS'] or l_dset == ['all_TOS', 'all_TIS']:
        cmb                 = cmb_ck(rk=1, eff=d_eff, yld=d_rare_yld)
        cmb.out_dir         = 'plots/combination'
        t_comb              = cmb.get_combination()
        d_rjpsi, d_eff, cov = t_comb
    else:
        cov = cv_sys + cv_sta

    cov = numpy.array([[cov[0][0]]])

    obj          = ext(dset=l_dset)
    obj.rjpsi    = d_rjpsi
    obj.eff      = d_eff
    obj.data     = d_dat
    obj.model    = d_mod 
    obj.cov      = cov 
    obj.fix      = ['dmu_ee', 'dmu_mm', 'ssg_ee', 'ssg_mm', 'r0_ee', 'r1_ee', 'r2_ee', 'ncb_mm', 'ncb_ee', 'npr_ee'] 
    obj.const    = d_val, d_var
    obj.plt_dir  = 'tests/extractor/fix_pars'
    result       = obj.get_fit_result()

    log.info(f'Calculating errors')
    result.hesse()
    result.freeze()
    print(result)

    delete_all_pars()
#----------------------------------------------------
def test_json():
    log.info('Running: test_json')
    d_eff       = model.get_eff()
    d_yld       = {'d1' :          2e3, 'd2' :            2e3, 'd3' :            2e3, 'd4' :            2e3} 
    d_mcmu      = {'d1' : (5000, 4900), 'd2' :   (5100, 4900), 'd3' :   (5100, 4800), 'd4' :   (5200, 5100)}
    d_mcsg      = {'d1' :    (10,  40), 'd2' :       (10, 18), 'd3' :       (20, 30), 'd4' :       (30, 40)} 

    d_eff       = rename_keys(d_eff)
    d_yld       = rename_keys(d_yld, use_txs=False)
    d_mcmu      = rename_keys(d_mcmu)
    d_mcsg      = rename_keys(d_mcsg)

    mod         = model(preffix='simple', d_eff=d_eff, d_mcmu=d_mcmu, d_mcsg=d_mcsg, d_nent=d_yld)
    d_dat       = mod.get_data()
    d_mod       = mod.get_model()
    d_pre       = mod.get_prefit_pars()

    obj         = ext(dset=['2017_TOS', '2018_TOS'])
    obj.eff     = d_eff 
    obj.data    = d_dat
    obj.model   = d_mod 
    obj.plt_dir = 'tests/extractor/json'

    result      = obj.get_fit_result()
    result.hesse()
    d_pos = rkut.result_to_dict(result)

    utnr.dump_json({'pre' : d_pre, 'pos' : d_pos}, 'tests/extractor/json/pars.json')

    delete_all_pars()
#----------------------------------------------------
def test_efficiency():
    log.info('Running: test_efficiency')
    d_eff        = model.get_eff(kind='diff')
    d_yld        = {'d1' : 2e3, 'd2' : 2e3, 'd3' : 2e3, 'd4' : 2e3} 
    d_mcmu       = {'d1' :   (50, 49), 'd2' :   (51, 49), 'd3' :   (51, 48), 'd4' :   (52, 51)}
    d_mcsg       = {'d1' :    (2,  4), 'd2' :   (1, 1.8), 'd3' :     (2, 3), 'd4' :     (3, 4)} 

    mod          = model(preffix='efficiency', d_eff=d_eff, d_mcmu=d_mcmu, d_mcsg=d_mcsg)
    d_dat        = mod.get_data(d_nent=d_yld)
    d_mod        = mod.get_model()

    obj          = ext()
    obj.eff      = d_eff 
    obj.data     = d_dat
    obj.model    = d_mod 
    obj.plt_dir  = 'tests/extractor/efficiency'

    result       = obj.get_fit_result()
    result.hesse()

    d_rk   = result.params['rk']
    rk_val = d_rk['value']
    rk_err = d_rk['hesse']['error']

    delete_all_pars()
#----------------------------------------------------
def test_constraint():
    log.info('Running: test_constraint')
    d_eff        = model.get_eff(kind='half')
    d_yld        = {'d1' :          2e3, 'd2' :            2e3, 'd3' :            2e3, 'd4' :            2e3} 
    d_mcmu       = {'d1' : (5000, 4900), 'd2' :   (5100, 4900), 'd3' :   (5100, 4800), 'd4' :   (5200, 5100)}
    d_mcsg       = {'d1' :    (10,  40), 'd2' :       (10, 18), 'd3' :       (20, 30), 'd4' :       (30, 40)} 

    d_eff        = rename_keys(d_eff)
    d_yld        = rename_keys(d_yld, use_txs=False)
    d_mcmu       = rename_keys(d_mcmu)
    d_mcsg       = rename_keys(d_mcsg)

    mod          = model(preffix='constraint', d_eff=d_eff, d_mcmu=d_mcmu, d_mcsg=d_mcsg, d_nent=d_yld)
    cvmat        = mod.get_cov(kind='random')
    d_dat        = mod.get_data()
    d_mod        = mod.get_model()

    obj          = ext(dset=['2017_TOS', '2018_TOS'])
    obj.eff      = d_eff 
    obj.cov      = cvmat
    obj.data     = d_dat
    obj.model    = d_mod 
    obj.plt_dir  = 'tests/extractor/constraint'

    result       = obj.get_fit_result()
    result.hesse()
    print(result)

    delete_all_pars()
#----------------------------------------------------
def test_rjpsi():
    log.info('Running: test_rjpsi')
    d_eff        = model.get_eff(kind='half')
    d_yld        = {'d1' : 2e3, 'd2' : 2e3, 'd3' : 2e3, 'd4' : 2e3} 
    d_mcmu       = {'d1' :   (50, 49), 'd2' :   (51, 49), 'd3' :   (51, 48), 'd4' :   (52, 51)}
    d_mcsg       = {'d1' :    (2,  4), 'd2' :   (1, 1.8), 'd3' :     (2, 3), 'd4' :     (3, 4)} 

    mod          = model(preffix='rjpsi', d_eff=d_eff, d_mcmu=d_mcmu, d_mcsg=d_mcsg)
    cvmat        = mod.get_cov(kind='diag_eq', c=0.001)
    d_rjpsi      = mod.get_rjpsi(kind='eff_bias')
    d_dat        = mod.get_data(d_nent=d_yld)
    d_mod        = mod.get_model()

    obj          = ext()
    obj.rjpsi    = d_rjpsi
    obj.eff      = d_eff
    obj.cov      = cvmat
    obj.data     = d_dat
    obj.model    = d_mod 
    obj.plt_dir  = 'tests/extractor/rjpsi'

    result       = obj.get_fit_result()

    result.hesse()

    d_rk   = result.params['rk']
    rk_val = d_rk['value']
    rk_err = d_rk['hesse']['error']

    delete_all_pars()
#----------------------------------------------------
def test_real():
    skip_test()
    log.info('Running: test_real')

    rdr          = np_rdr(sys='v65', sta='v63', yld='v24')
    rdr.cache    = True
    rdr.cache_dir='./v65_v63_v24'
    cv_sys       = rdr.get_cov(kind='sys')
    cv_sta       = rdr.get_cov(kind='sta')
    d_eff        = rdr.get_eff()
    d_rjpsi      = rdr.get_rjpsi()
    d_byld       = rdr.get_byields()
    d_nent       = rkut.average_byields(d_byld, l_exclude=['TIS'])
    d_rare_yld   = rkut.reso_to_rare(d_nent, kind='jpsi')

    mod          = model(preffix='real', d_eff=d_eff, d_nent=d_rare_yld, l_dset=['all_TOS'])
    mod.out_dir  = 'tests/extractor/real/model'
    mod.bdt_bin  = 0
    d_mod        = mod.get_model()
    d_dat        = mod.get_data()
    d_val, d_var = mod.get_cons()

    return

    obj          = ext(dset=['all_TOS'])
    obj.rjpsi    = d_rjpsi
    obj.eff      = d_eff
    obj.cov      = cv_sys + cv_sta
    obj.data     = d_dat
    obj.const    = d_val, d_var
    obj.model    = d_mod 
    obj.plt_dir  = 'tests/extractor/real'
    result       = obj.get_fit_result()

    log.info(f'Calculating errors')
    result.hesse()
    result.freeze()
    utnr.dump_pickle(result, 'tests/extractor/real/result.pkl')

    delete_all_pars()
#----------------------------------------------------
def test_all_years():
    skip_test()
    log.info('Running: test_real')

    rdr          = np_rdr(sys='v65', sta='v63', yld='v24')
    rdr.cache    = True
    cv_sys       = rdr.get_cov(kind='sys')
    cv_sta       = rdr.get_cov(kind='sta')
    d_eff        = rdr.get_eff()
    d_rjpsi      = rdr.get_rjpsi()
    d_byld       = rdr.get_byields()
    d_nent       = rkut.average_byields(d_byld, l_exclude=['TIS'])
    d_rare_yld   = rkut.reso_to_rare(d_nent, kind='jpsi')

    mod          = model(preffix='real', d_eff=d_eff, d_nent=d_rare_yld, l_dset=['all_TOS'])
    mod.out_dir  = 'tests/extractor/all_years/model'
    d_mod        = mod.get_model()
    d_dat        = mod.get_data()
    d_val, d_var = mod.get_cons()

    obj          = ext()
    #--------------------------
    obj.rjpsi    = d_rjpsi
    obj.eff      = d_eff
    obj.cov      = cv_sys + cv_sta
    #--------------------------
    obj.data     = d_dat
    obj.const    = d_val, d_var
    obj.model    = d_mod 
    #--------------------------
    obj.plt_dir  = 'tests/extractor/all_years'
    result       = obj.get_fit_result()

    log.info(f'Calculating errors')
    result.hesse()
    result.freeze()
    utnr.dump_pickle(result, 'tests/extractor/all_years/result.pkl')

    delete_all_pars()
#----------------------------------------------------
def test_combined():
    skip_test()
    log.info('Running: test_real')

    rdr          = np_rdr(sys='v65', sta='v63', yld='v24')
    rdr.cache    = True
    cv_sys       = rdr.get_cov(kind='sys')
    cv_sta       = rdr.get_cov(kind='sta')
    d_eff        = rdr.get_eff()
    d_rjpsi      = rdr.get_rjpsi()
    d_byld       = rdr.get_byields()
    d_nent       = rkut.average_byields(d_byld, l_exclude=['TIS'])
    d_rare_yld   = rkut.reso_to_rare(d_nent, kind='jpsi')

    mod          = model(preffix='real', d_eff=d_eff, d_nent=d_rare_yld, l_dset=['all_TOS', 'all_TIS'])
    mod.out_dir  = 'tests/extractor/combined/model'
    d_mod        = mod.get_model()
    d_dat        = mod.get_data()
    d_val, d_var = mod.get_cons()

    cmb                 = cmb_ck(rjp=d_rjpsi, eff=d_eff, cov=cv_sys + cv_sta)
    cmb.out_dir         = 'tests/extractor/combined/combination'
    d_rjpsi, d_eff, cov = cmb.get_combination(add_tis=True)

    obj          = ext(dset=['all_TOS', 'all_TIS'])
    #--------------------------
    obj.rjpsi    = d_rjpsi
    obj.eff      = d_eff
    obj.cov      = cov 
    #--------------------------
    obj.model    = d_mod 
    obj.data     = d_dat
    obj.const    = d_val, d_var
    #--------------------------
    obj.plt_dir  = 'tests/extractor/combined'
    result       = obj.get_fit_result()

    log.info(f'Calculating errors')
    result.hesse()
    result.freeze()
    utnr.dump_pickle(result, 'tests/extractor/combined/result.pkl')

    delete_all_pars()
#----------------------------------------------------
def test_real_const():
    skip_test()
    log.info('Running: test_const')

    rdr          = cs_rdr(version='v4', preffix='const')
    d_val, d_var = rdr.get_constraints()

    rdr          = np_rdr(sys='v65', sta='v63', yld='v24')
    rdr.cache    = True
    cv_sys       = rdr.get_cov(kind='sys')
    cv_sta       = rdr.get_cov(kind='sta')
    d_eff        = rdr.get_eff()
    d_rjpsi      = rdr.get_rjpsi()
    d_byld       = rdr.get_byields()
    d_nent       = rkut.average_byields(d_byld, l_exclude=['TIS'])
    d_rare_yld   = rkut.reso_to_rare(d_nent, kind='jpsi')

    rdr          = mc_rdr(version='v4')
    rdr.cache    = True 
    d_mcmu       = rdr.get_parameter(name='mu')
    d_mcsg       = rdr.get_parameter(name='sg')

    mod                  = model(preffix='const', d_eff=d_eff, d_mcmu=d_mcmu, d_mcsg=d_mcsg, d_nent=d_rare_yld)
    d_mod                = mod.get_model()
    d_dat                = mod.get_data()
    d_val_mod, d_var_mod = mod.get_cons()

    d_val.update(d_val_mod)
    d_var.update(d_var_mod)

    obj          = ext(dset=['r2p1_TOS', '2017_TOS', '2018_TOS'])
    obj.rjpsi    = d_rjpsi
    obj.eff      = d_eff
    obj.cov      = cv_sys + cv_sta
    obj.data     = d_dat
    obj.model    = d_mod 
    obj.const    = d_val, d_var
    obj.plt_dir  = 'tests/extractor/const'
    result       = obj.get_fit_result()

    log.info(f'Calculating errors')
    result.hesse()
    result.freeze()
    print(result)

    delete_all_pars()
#----------------------------------------------------
def test_real_const_dset():
    skip_test()
    log.info('Running: test_dset')

    rdr          = cs_rdr(version='v4', preffix='dset')
    rdr.cache_dir= 'tests/extractor/real_const_dset/v4_csrdr'
    d_val, d_var = rdr.get_constraints()

    rdr          = np_rdr(sys='v65', sta='v63', yld='v24')
    rdr.cache    = True
    rdr.cache_dir= 'tests/extractor/real_const_dset/v65_v63_v24'
    cv_sys       = rdr.get_cov(kind='sys')
    cv_sta       = rdr.get_cov(kind='sta')
    d_eff        = rdr.get_eff()
    d_rjpsi      = rdr.get_rjpsi()
    d_byld       = rdr.get_byields()
    d_nent       = rkut.average_byields(d_byld, l_exclude=['TIS'])
    d_rare_yld   = rkut.reso_to_rare(d_nent, kind='jpsi')

    rdr_mc          = mc_rdr(version='v4', real_data=False)
    rdr_mc.cache    = False
    rdr_mc.cache_dir= 'tests/extractor/real_const_dset/v4_mcrdr'
    d_mcmu          = rdr_mc.get_parameter(name='mu')
    d_mcsg          = rdr_mc.get_parameter(name='sg')

    rdr_dt          = mc_rdr(version='v4', real_data=True)
    rdr_dt.cache    = False
    rdr_dt.cache_dir= 'tests/extractor/real_const_dset/v4_dtrdr'
    d_dtmu          = rdr_dt.get_parameter(name='mu')
    d_dtsg          = rdr_dt.get_parameter(name='sg')

    mod          = model(preffix='dset', d_eff=d_eff, d_mcmu=d_mcmu, d_mcsg=d_mcsg)
    d_mod        = mod.get_model()
    d_dat        = mod.get_data(d_nent=d_rare_yld, d_dtmu=d_dtmu, d_dtsg=d_dtsg)

    obj          = ext(dset=['2018_TOS'])
    obj.cov      = cv_sys + cv_sta
    obj.const    = d_val, d_var
    obj.model    = d_mod 
    obj.eff      = d_eff
    obj.data     = d_dat
    obj.rjpsi    = d_rjpsi
    obj.plt_dir  = 'tests/extractor/dset'
    result       = obj.get_fit_result()

    log.info(f'Calculating errors')
    result.hesse()
    result.freeze()
    utnr.dump_pickle(result, 'tests/extractor/dset/result.pkl')

    print(result)
    delete_all_pars()
#----------------------------------------------------
def test_diagonal():
    log.info('Running: test_constraint')
    d_eff        = model.get_eff(kind='half')
    d_yld        = {'d1' :          2e3, 'd2' :            2e3, 'd3' :            2e3, 'd4' :            2e3} 
    d_mcmu       = {'d1' : (5000, 4900), 'd2' :   (5100, 4900), 'd3' :   (5100, 4800), 'd4' :   (5200, 5100)}
    d_mcsg       = {'d1' :    (10,  40), 'd2' :       (10, 18), 'd3' :       (20, 30), 'd4' :       (30, 40)} 

    d_eff        = rename_keys(d_eff)
    d_yld        = rename_keys(d_yld, use_txs=False)
    d_mcmu       = rename_keys(d_mcmu)
    d_mcsg       = rename_keys(d_mcsg)

    mod          = model(preffix='constraint', d_eff=d_eff, d_mcmu=d_mcmu, d_mcsg=d_mcsg)
    cvmat        = mod.get_cov(kind='random')
    d_dat        = mod.get_data(d_nent=d_yld)
    d_mod        = mod.get_model()

    obj          = ext(dset=['2017_TOS', '2018_TOS'], drop_correlations=True)
    obj.eff      = d_eff 
    obj.cov      = cvmat
    obj.data     = d_dat
    obj.model    = d_mod 
    obj.plt_dir  = 'tests/extractor/constraint'

    result       = obj.get_fit_result()

    result.hesse()

    d_rk   = result.params['rk']
    rk_val = d_rk['value']
    rk_err = d_rk['hesse']['error']

    delete_all_pars()
#----------------------------------------------------
def test_dmodel():
    log.info('Running: test_simple')
    d_eff       = model.get_eff()
    d_yld       = {'d1' :          2e2, 'd2' :            2e2, 'd3' :            2e2, 'd4' :            2e2} 
    d_mcmu      = {'d1' : (5000, 4900), 'd2' :   (5100, 4900), 'd3' :   (5100, 4800), 'd4' :   (5200, 5100)}
    d_mcsg      = {'d1' :    (10,  40), 'd2' :       (10, 18), 'd3' :       (20, 30), 'd4' :       (30, 40)} 

    d_eff       = rename_keys(d_eff)
    d_yld       = rename_keys(d_yld, use_txs=False)
    d_mcmu      = rename_keys(d_mcmu)
    d_mcsg      = rename_keys(d_mcsg)

    mod         = model(preffix='simple', d_eff=d_eff, d_nent=d_yld, l_dset=['2018_TOS'])
    d_dat       = mod.get_data()
    d_mod       = mod.get_model()

    obj         = ext(dset=['2018_TOS'])
    obj.eff     = d_eff 
    obj.data    = d_dat
    obj.model   = d_mod 
    obj.plt_dir = 'tests/extractor/simple'

    result      = obj.get_fit_result()
    result.hesse()

    print(result)

    delete_all_pars()
#----------------------------------------------------
def main():
    utnr.timer_on=True
    test_real()
    return
    test_fix_pars()
    test_dmodel()
    test_simple()
    test_combined()
    test_all_years()
    test_real_const()
    test_json()
    test_constraint()
    test_diagonal()
    test_real_const_dset()
    test_rjpsi()
    test_efficiency()
#----------------------------------------------------
if __name__ == '__main__':
    main()

