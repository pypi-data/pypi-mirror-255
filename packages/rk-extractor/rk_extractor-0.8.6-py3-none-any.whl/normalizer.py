import os
import re
import glob
import ROOT
import math
import zfit
import numpy
import pprint
import extset
import utils_noroot      as utnr
import zutils.utils      as zut
import matplotlib.pyplot as plt

from zutils.plot   import plot     as zfp
from fitter        import zfitter
from log_store     import log_store

log = log_store.add_logger(name='rk_extractor:normalizer')
#--------------------------------------
class normalizer:
    '''
    Class used to find normalizations for combinatorial and PRec components
    in the high-q2 signal model
    '''
    #--------------------------------------
    def __init__(self, dset=None, trig=None, d_model=None, d_val=None, d_var=None):
        self._d_model = d_model 
        self._dset    = dset
        self._trig    = trig
        self._d_val   = d_val
        self._d_var   = d_var

        self._l_flt_par= ['lm_cb', 'mu_cb', 'a', 'b', 'ncb', 'npr_ee', 'nsg_ee']
        self._dat_path = f'{os.environ["CASDIR"]}/tools/apply_selection/blind_fits/data/v10.21p2'

        self._d_const  = {}
        self._nbins    = 64 
        self._rng_mm   = 5180, 5600 
        self._rng_ee   = 4500, 6100 
        self._bln_ee   = 5000, 5450
        self._bln_mm   = 5200, 5360

        self._d_data      = None
        self._s_par       = None
        self._d_pre       = None
        self._out_dir     = None
        self._l_bdt_bin   = None 
        self._custom_data = False
        self._initialized = False 
    #--------------------------------------
    def _initialize(self):
        if self._initialized:
            return

        os.makedirs(f'{self._out_dir}/pdf', exist_ok=True)

        self._l_bdt_bin = self._get_bdt_bins()
        self._s_par     = self._get_parameters() 
        self._d_pre     = {par.name : par.value().numpy() for par in self._s_par}
        self._d_const   = self._prepare_pars()
        self._d_data    = self._get_data()

        self._initialized = True 
    #--------------------------------------
    def _get_parameters(self):
        s_par = set()
        for pdf_mm, pdf_ee in self._d_model.values():
            s_mod_par_mm = pdf_mm.get_params()
            s_mod_par_ee = pdf_ee.get_params()
            s_par        = s_par.union(s_mod_par_mm)
            s_par        = s_par.union(s_mod_par_ee)

        return s_par
    #--------------------------------------
    @property
    def data(self):
        return self._d_data

    @data.setter
    def data(self, value):
        self._custom_data = True
        self._d_data      = value
    #--------------------------------------
    def _get_bdt_bins(self):
        l_mod_key  = [ key for key in self._d_model ]
        l_bdt_sbin = [ re.match('.*_(\d)$', mod_key).groups()[0] for mod_key in l_mod_key ]
        l_bdt_ibin = [ int(sbin) for sbin in l_bdt_sbin ]

        return l_bdt_ibin
    #--------------------------------------
    def _get_data_paths(self):
        if   self._dset == 'r1':
            l_dset = [f'{self._dat_path}/2011_{self._trig}', f'{self._dat_path}/2012_{self._trig}']
        elif self._dset == 'r2p1':
            l_dset = [f'{self._dat_path}/2015_{self._trig}', f'{self._dat_path}/2016_{self._trig}']
        elif self._dset == 'all':
            l_dset = [f'{self._dat_path}/{year}_{self._trig}' for year in [2011, 2012, 2015, 2016, 2017, 2018] ]
        else:
            l_dset = [f'{self._dat_path}/{self._dset}_{self._trig}']

        l_wc = [f'{dset}/*.root' for dset in l_dset]

        l_l_path = [ glob.glob(wc) for wc in l_wc ]
        for l_path, wc in zip(l_l_path, l_wc):
            if len(l_path) == 0:
                log.error(f'No file found in {wc}')
                raise

        return l_wc
    #-------------------------------------
    def _filter(self, rdf, ibin):
        d_bdt_wp, _, _ = extset.get_bdt_bin_settings(ibin)

        [lo_cmb, hi_cmb] = d_bdt_wp['BDT_cmb']
        [lo_prc, hi_prc] = d_bdt_wp['BDT_prc']

        hi_cmb = +10 if hi_cmb is None else hi_cmb
        hi_prc = +10 if hi_prc is None else hi_prc

        lo_cmb = -10 if lo_cmb is None else lo_cmb
        lo_prc = -10 if lo_prc is None else lo_prc

        rdf = rdf.Filter(f'(BDT_cmb > {lo_cmb}) && (BDT_cmb < {hi_cmb})', 'CMB')
        rdf = rdf.Filter(f'(BDT_prc > {lo_prc}) && (BDT_prc < {hi_prc})', 'PRC')

        rep = rdf.Report()
        rep.Print()

        return rdf
    #-------------------------------------
    def _get_mass(self, l_dpath, ibin):
        rdf = ROOT.RDataFrame(self._trig, l_dpath)
        rdf = self._filter(rdf, ibin)

        arr_mass = rdf.AsNumpy(['B_M'])['B_M']

        return arr_mass.tolist()
    #--------------------------------------
    @utnr.timeit
    def _get_data(self):
        dat_path = f'{self._out_dir}/data/{self._dset}_{self._trig}.json'
        if   self._d_data is not None:
            log.warning(f'Using data passed by user')
            return self._d_data
        elif os.path.isfile(dat_path):
            log.info(f'Loading cached data from: {dat_path}')
            d_dat = utnr.load_json(dat_path)
            return d_dat 

        log.info(f'Caching data: {dat_path}')

        os.makedirs(f'{self._out_dir}/data', exist_ok=True)

        l_dpath = self._get_data_paths()
        d_dat   = { f'bdt_{ibin}' : self._get_mass(l_dpath, ibin) for ibin in self._l_bdt_bin}

        log.info(f'Saving to: {dat_path}')
        utnr.dump_json(d_dat, dat_path) 

        return d_dat 
    #--------------------------------------
    def _plot_data(self, arr_mass):
        if not self._out_dir:
            return

        rng_ee = 4800, 6000
        rng_mm = 5100, 5600
        rng = rng_mm if self._trig == 'MTOS' else rng_ee
        plt.hist(arr_mass, range=rng, bins=50, histtype='step')
        plot_path = f'{self._out_dir}/data/{self._dset}_{self._trig}.png'
        log.info(f'Saving to: {plot_path}')
        plt.savefig(plot_path)
        plt.close('all')
    #--------------------------------------
    def _prepare_pars(self):
        for par in self._s_par:
            par.floating = False

        d_const = {}
        for par in self._s_par:
            for flt_par in self._l_flt_par:
                if par.name.startswith(flt_par):
                    par.floating = True
                else:
                    continue

                if par.name in self._d_val:
                    var = self._d_var[par.name]
                    val = self._d_val[par.name]
                    d_const[par.name] = val, math.sqrt(var)

        return d_const
    #--------------------------------------
    @property
    def out_dir(self):
        return self._out_dir

    @out_dir.setter
    def out_dir(self, value):
        try:
            os.makedirs(value, exist_ok=True)
        except:
            log.error(f'Cannot create directory: {value}')
            raise

        self._out_dir = value
    #--------------------------------------
    def _get_stats(self, arr_dat):
        if self._trig != 'MTOS':
            return ''

        arr_flg = (arr_dat > 5180) & (arr_dat < 5400)
        arr_dat = arr_dat[arr_flg]
        ndata   = float(arr_dat.size)

        s_par     = self._model.get_params(floating=False)
        [pst_val] = [ par.value().numpy() for par      in s_par               if par.name.startswith('nsg_mm_') ]
        [pre_val] = [ val                 for nam, val in self._d_pre.items() if nam.startswith('nsg_mm_')      ]

        v1 = f'Data: {ndata:.0f} $m\in [5180, 5400]$'
        v2 = f'Fitted: {pst_val:.0f}'
        v3 = f'Expected: {pre_val:.0f}'

        return f'{v1}\n{v2}\n{v3}'
    #--------------------------------------
    def _get_pdf_names(self):
        d_leg         = {}
        d_leg['prc']  = r'$\psi(2S) + c\bar{c}$'
        d_leg['bpks'] = r'$B^+\to K^{*+}e^+e^-$'
        d_leg['bdks'] = r'$B^0\to K^{*0}e^+e^-$'
        d_leg['bsph'] = r'$B_s\to \phi e^+e^-$'
        d_leg['bpk1'] = r'$B^+\to K_{1}e^+e^-$'
        d_leg['bpk2'] = r'$B^+\to K_{2}e^+e^-$'

        return d_leg
    #--------------------------------------
    def _get_blinding(self):
        if self._trig == 'MTOS':
            return

        low, hig= self._bln_ee
        l_blnd  = [extset.sig_name, low, hig]

        return l_blnd
    #--------------------------------------
    def _plot_fit(self, data=None, model=None, name=None, result=None, stacked=None):
        stats   = self._get_stats(data)
        rng     = self._rng_mm if self._trig == 'MTOS' else self._rng_ee
        l_blnd  = self._get_blinding()

        obj= zfp(data=data, model=model, result=None)
        obj.plot(skip_pulls=False, blind=l_blnd, nbins=self._nbins, ranges=[rng], d_leg=self._get_pdf_names(), stacked=stacked, ext_text=stats)
        obj.axs[0].grid()

        if not self._custom_data:
            if   '_all_' in name and 'MTOS' in name:
                obj.axs[0].set_ylim(0,  250)
            elif '_all_' in name and 'ETOS' in name:
                obj.axs[0].set_ylim(0,  120)
            elif '_all_' in name and 'GTIS' in name:
                obj.axs[0].set_ylim(0,   50)

        obj.axs[1].set_ylim(-5, 5)
        obj.axs[1].axhline(0, color='r')

        os.makedirs(f'{self._out_dir}/fits', exist_ok=True)
        plot_path = f'{self._out_dir}/fits/{name}.png'
        log.info(f'Saving to: {plot_path}')
        plt.savefig(plot_path)
        plt.close('all')
    #--------------------------------------
    @utnr.timeit
    def _fit(self, d_mod, d_dat):
        tot_nll = None
        d_fdat  = {}
        d_fmod  = {}
        for bdt_bin in self._l_bdt_bin:
            _, mod = d_mod[f'bdt_{bdt_bin}']
            l_dat  = d_dat[f'bdt_{bdt_bin}']
            arr_mas= numpy.array(l_dat)
            obs    = mod.space
            dat    = zfit.Data.from_numpy(obs=obs, array=arr_mas)

            d_fdat[f'bdt_{bdt_bin}'] = dat
            d_fmod[f'bdt_{bdt_bin}'] = mod

            rng    = self._rng_mm if self._trig == 'MTOS' else self._rng_ee
            log.info(f'Adding nll for bin {bdt_bin} in range {rng}')
            nll    = zfit.loss.ExtendedUnbinnedNLL(model=mod, data=dat, fit_range=rng)

            tot_nll = nll if tot_nll is None else nll + tot_nll

        minimizer = zfit.minimize.Minuit()
        log.debug('Minimizing')
        result    = minimizer.minimize(tot_nll)

        return result, d_fdat, d_fmod
    #--------------------------------------
    def _print_pdfs(self, prefix):
        for key, (mod_mm, mod_ee) in self._d_model.items():
            zut.print_pdf(mod_mm, txt_path=f'{self._out_dir}/pdf/{prefix}_mm_{key}_{self._dset}_{self._trig}.txt', d_const=self._d_const)
            zut.print_pdf(mod_ee, txt_path=f'{self._out_dir}/pdf/{prefix}_ee_{key}_{self._dset}_{self._trig}.txt', d_const=self._d_const)
    #--------------------------------------
    def _plot_fits(self, d_fdat, d_fmod):
        for ibin in self._l_bdt_bin:
            key = f'bdt_{ibin}'
            arr_mass = d_fdat[key]
            model    = d_fmod[key]

            self._plot_fit(data=arr_mass, model=model, name=f'{self._trig}_{self._dset}_{key}_stk', stacked= True)
    #--------------------------------------
    @utnr.timeit
    def get_fit_result(self):
        self._initialize()

        self._print_pdfs('pre')
        res, d_fdat, d_fmod = self._fit(self._d_model, self._d_data)
        self._print_pdfs('pos')

        self._plot_fits(d_fdat, d_fmod)

        res.hesse()
        res.freeze()

        return res
#--------------------------------------

