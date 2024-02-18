import os
os.environ['ZFIT_DISABLE_TF_WARNINGS']='1'

import zfit
zfit.settings.changed_warnings.all = False

import logzero
from log_store import log_store

import zutils.utils as zut

log_store.set_level('rk_extractor:rk_model'      , logzero.INFO)
log_store.set_level('rk_extractor:rkex_model'    , logzero.INFO)
log_store.set_level('rk_extractor:scales'        , logzero.WARNING)
log_store.set_level('rk_extractor:scale_reader'  , logzero.WARNING)
log_store.set_level('rk_selection:read_selection', logzero.WARNING)
log_store.set_level('cb_calculator:builder'      , logzero.WARNING)
log_store.set_level('scripts:zutils/utils'       , logzero.INFO)

from model_manager import manager
from rk_model      import rk_model  as model

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
def test_simple():
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
    mod.bdt_bin = [1, 2]
    mod.com_par = ['mu_ee']
    d_dat       = mod.get_data()
    d_mod       = mod.get_model()

    for _, (_, pdf) in d_mod.items():
        zut.print_pdf(pdf)
#----------------------------------------------------
def test_real():
    d_eff       = model.get_eff()
    d_yld       = {'d1' :          2e2, 'd2' :            2e2, 'd3' :            2e2, 'd4' :            2e2} 
    d_mcmu      = {'d1' : (5000, 4900), 'd2' :   (5100, 4900), 'd3' :   (5100, 4800), 'd4' :   (5200, 5100)}
    d_mcsg      = {'d1' :    (10,  40), 'd2' :       (10, 18), 'd3' :       (20, 30), 'd4' :       (30, 40)} 

    d_eff       = rename_keys(d_eff)
    d_yld       = rename_keys(d_yld, use_txs=False)
    d_mcmu      = rename_keys(d_mcmu)
    d_mcsg      = rename_keys(d_mcsg)

    mod         = manager(preffix='simple', d_eff=d_eff, d_nent=d_yld, dset='all_TOS')
    mod.fake    = False 
    mod.bdt_bin = [4, 5]
    d_dat       = mod.get_data()
    d_mod       = mod.get_model()
#----------------------------------------------------
def test_fit():
    d_eff       = model.get_eff()
    d_yld       = {'d1' :          2e2, 'd2' :            2e2, 'd3' :            2e2, 'd4' :            2e2} 
    d_mcmu      = {'d1' : (5000, 4900), 'd2' :   (5100, 4900), 'd3' :   (5100, 4800), 'd4' :   (5200, 5100)}
    d_mcsg      = {'d1' :    (10,  40), 'd2' :       (10, 18), 'd3' :       (20, 30), 'd4' :       (30, 40)} 

    d_eff       = rename_keys(d_eff)
    d_yld       = rename_keys(d_yld, use_txs=False)
    d_mcmu      = rename_keys(d_mcmu)
    d_mcsg      = rename_keys(d_mcsg)

    mod         = manager(preffix='fit', d_eff=d_eff, d_nent=d_yld, dset='all_TOS')
    mod.fake    = True
    mod.bdt_bin = [1, 2, 3, 4, 5]
    d_dat       = mod.get_data()
    d_mod       = mod.get_model()

    sim_fit(d_dat, d_mod)
#----------------------------------------------------
def sim_fit(d_dat, d_mod):
    nll = None
    for key in d_dat:
        _, ee_dat = d_dat[key]
        _, ee_mod = d_mod[key]

        nll_ee = zfit.loss.ExtendedUnbinnedNLL(model=ee_mod, data=ee_dat)

        nll = nll_ee if nll is None else nll + nll_ee

    minimizer    = zfit.minimize.Minuit()
    result       = minimizer.minimize(nll)
    result.hesse()

    print(result)
#----------------------------------------------------
def main():
    test_simple()
    return
    test_real()
    test_fit()
#----------------------------------------------------
if __name__ == '__main__':
    main()

