from model_analyzer import analyzer  as mana
from np_reader      import np_reader as np_rdr
from logzero        import logger    as log
from rk_model       import rk_model

import rk.utilities as rkut
import math
import zfit

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
#---------------------------------------------
def delete_all_pars():
    d_par = zfit.Parameter._existing_params
    l_key = list(d_par.keys())

    for key in l_key:
        del(d_par[key])
#---------------------------------------------
def get_model():
    obs          = zfit.Space('x', limits=(-10, 10))
    mu           = zfit.Parameter("mu", 2.4, -1, 5)
    sg           = zfit.Parameter("sg", 1.3,  0, 5)
    ne           = zfit.Parameter('ne', 100, 0, 1000)
    gauss        = zfit.pdf.Gauss(obs=obs, mu=mu, sigma=sg)

    return gauss.create_extended(ne) 
#---------------------------------------------
def test_fit():
    model = get_model()
    
    obj                    = mana(pdf=model, d_const={'mu' : [2.4, 0.5]})
    obj.out_dir            = 'tests/model_analyzer/pulls'
    df_ini, df_val, df_err = obj.fit(nfit=10)

    delete_all_pars()
#---------------------------------------------
def get_rk_model(kind):
    d_eff = {'d1' :   (0.5, 0.4), 'd2' :   (0.4, 0.3), 'd3' :   (0.3, 0.2), 'd4' :   (0.2, 0.1)}
    d_nent= {'d1' :          1e3, 'd2' :          1e3, 'd3' :          1e3, 'd4' :          1e3}
    d_eff =rename_keys(d_eff)
    d_nent=rename_keys(d_nent, use_txs=False)

    mod   = rk_model(preffix='perf', d_eff=d_eff, d_nent=d_nent, l_dset=[kind])
    d_mod = mod.get_model()

    return d_mod[kind]
#---------------------------------------------
def get_cb_model(preffix, obs):
    mu = zfit.Parameter(f'{preffix}_mu', 5200, 5000, 5600)
    sg = zfit.Parameter(f'{preffix}_sg',   10,  0.1,  500)

    al = zfit.Parameter(f'{preffix}_al', 1, 0,  20)
    nl = zfit.Parameter(f'{preffix}_nl', 1, 0, 150)

    ar = zfit.Parameter(f'{preffix}_ar', 1, 0,  20)
    nr = zfit.Parameter(f'{preffix}_nr', 1, 0, 120)

    nev= zfit.Parameter(f'{preffix}_nev', 1000, 0, 2000)
    dscb = zfit.pdf.DoubleCB(
        mu    = mu,
        sigma = sg,
        alphal= al,
        nl    = nl,
        alphar= ar,
        nr    = nr,
        obs   = obs,
    )    

    pdf = dscb.create_extended(nev)

    return pdf 
#---------------------------------------------
def test_perf_sum():
    obs= zfit.Space('obs', limits=(5000, 5600))
    m1 = get_cb_model('m1', obs)
    m2 = get_cb_model('m2', obs)
    m3 = get_cb_model('m3', obs)
    sm = zfit.pdf.SumPDF([m1, m2, m3])

    obj         = mana(pdf=sm) 
    obj.out_dir = 'tests/model_analyzer/sum_perf'
    obj.sampling_speed(nsample=10)

    delete_all_pars()
#---------------------------------------------
def test_perf_rk():
    _, model = get_rk_model('all_TOS')

    obj         = mana(pdf=model) 
    obj.out_dir = 'tests/model_analyzer/rk_perf'
    obj.sampling_speed(nsample=10)

    delete_all_pars()
#---------------------------------------------
def test_rk():
    log.info('Getting nuisance parameters')
    rdr          = np_rdr(sys='v65', sta='v63', yld='v24')
    rdr.cache    = True
    rdr.cache_dir= './v65_v63_v24'
    d_eff        = rdr.get_eff()
    d_byld       = rdr.get_byields()
    d_nent       = rkut.average_byields(d_byld, l_exclude=['TIS'])
    d_rare_yld   = rkut.reso_to_rare(d_nent, kind='jpsi')

    log.info('Building model')
    mod         = rk_model(preffix='all_tos', d_eff=d_eff, d_nent=d_rare_yld, l_dset=['all_TOS'])
    mod.bdt_bin = 2 
    d_mod       = mod.get_model()
    d_val, d_var= mod.get_cons()
    _, mod_ee   = d_mod['all_TOS']

    d_const = { key : [val, math.sqrt(var)] for key, val, var in zip(d_val, d_val.values(), d_var.values())}

    log.info('Analyzing model')
    obj            = mana(pdf=mod_ee, d_const = d_const, nev_fac=1)
    obj.out_dir    = 'tests/model_analyzer/rk'
    obj.sampling_speed(nsample=100)

    delete_all_pars()
#---------------------------------------------
def main():
    test_rk()
    return
    test_perf_sum()
    test_fit()
#---------------------------------------------
if __name__ == '__main__':
    main()

