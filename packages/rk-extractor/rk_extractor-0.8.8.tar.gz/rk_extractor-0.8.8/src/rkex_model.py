import numpy
import zfit
import math
import re
import os
import pprint
import extset
import matplotlib.pyplot as plt

from scipy.stats        import poisson
from bdt_scale          import scale_reader as scl_rdr
#from hqm.model.settings import settings     as hqm_set
from log_store          import log_store

log = log_store.add_logger(name='rk_extractor:rkex_model')
#----------------------------------------------------
class model:
    def __init__(self, rk=1, preffix='', d_eff=None, d_nent=None, l_dset=None):
        '''
        Parameters
        -----------------------
        rk     (float): Value used in model, will impact toy data produced 
        preffix(str)  : Used to name parameters in case multiple models used
        d_eff  (dict): Stores full efficiency (selection + reco + acceptance) for each dataset processed
        d_nent (dict): Stores number of B -> llK entries, before selection, e.g. {r1 : 23235}
        l_dset (list): List of datasets for which the models should be created, if None, do it for all datasets i.e. r1_TOS, r2p1_TOS...
        '''
        self._obs        = zfit.Space('x', limits=(4500, 6100))
        self._rk         = rk
        self._preffix    = preffix
        self._d_eff      = d_eff 
        self._d_nent     = d_nent
        self._l_sub_dset = l_dset

        self._l_all_kind = None
        self._d_bdt_wp   = None
        self._bdt_bin    = None

        zfit.settings.changed_warnings.hesse_name = False

        self._nbin        = 80
        self._bdt_eff_vers= 'v1' #For correcting signal yield for BDT WP
        self._norm_vers   = 'v44'
        self._msid_vers   = 'v4'
        self._comb_vers   = 'v1'
        self._l_all_dset  = ['r1', 'r2p1', '2017', '2018'] 
        self._d_lumi      = {'r1' : 3, 'r2p1' : 1.9, '2017' : 1.7, '2018' : 2.1}
        self._scal_vers   = None #For scaling between signal and rare PRec
        self._l_dset      = None
        self._d_mod       = None
        self._out_dir     = None
        self._kind        = None
        self._initialized = False
    #----------------------------------------------------
    def _initialize(self):
        if self._initialized:
            return
        log.info('Starting initializing')

        if self._bdt_bin is None:
            log.error('No BDT bin was specified')
            raise

        if self._d_eff is None:
            log.error(f'No efficiencies found, cannot provide data')
            raise

        if self._d_nent is None:
            log.error(f'No B-> Jpsi K yields found')
            raise

        self._l_dset = self._d_eff.keys() if self._l_sub_dset is None else self._l_sub_dset

        self._set_kinds()
        self._check_kind()
        self._cache_model()

        log.info('Finished initializing')

        self._initialized = True
    #---------------------------------------------------------------
    def _set_kinds(self):
        log.debug(f'Setting model kinds')
        self._l_all_kind = []
        self._l_all_kind.append(r'sig_MTOS:sys\d{1}')
        self._l_all_kind.append(r'cmb_MTOS:sys\d{1}')

        self._l_all_kind.append(r'sig_ETOS:sys\d{1}')
        self._l_all_kind.append(r'cpr_ETOS:sys\d{1}')
        self._l_all_kind.append(r'cmb_ETOS:sys\d{1}')

        self._l_all_kind.append(r'rpr_ETOS:bts\d+')
        self._l_all_kind.append(r'cpr_ETOS:bts\d+')
    #---------------------------------------------------------------
    @property
    def bdt_bin(self):
        return self._bdt_bin

    @bdt_bin.setter
    def bdt_bin(self, value):
        '''
        Will take an integer and use it to configure the components for different BDT bins
        '''
        log.info(f'Using {value}th BDT bin')
        self._bdt_bin      = value

        d_bdt_wp, vra, vcc = extset.get_bdt_bin_settings(bdt_bin = value)
        self._scal_vers    = vra
        self._d_bdt_wp     = d_bdt_wp 
        #hqm_set.version    = vcc 
    #---------------------------------------------------------------
    def _check_kind(self):
        log.debug(f'Checking model kinds')
        if self._kind == 'nom':
            log.debug('Using nominal model')
            return

        found = False
        for kind in self._l_all_kind:
            if re.match(kind, self._kind):
                found = True
                break

        if not found: 
            log.error(f'Model of kind {self._kind} not supported')
            raise
        else:
            log.debug(f'Using model of kind: {self._kind}')
    #----------------------------------------------------
    @property
    def out_dir(self):
        return self._out_dir

    @out_dir.setter
    def out_dir(self, value):
        try:
            os.makedirs(value, exist_ok=True)
        except:
            log.error(f'Cannot create: {value}')
            raise

        self._out_dir = value
        log.debug(f'Using output directory: {self._out_dir}')
    #----------------------------------------------------
    @property
    def kind(self):
        return self._kind

    @kind.setter
    def kind(self, value):
        '''
        Parameters
        -----------------
        kind (str): Will define the type of PDF, e.g. "signal:sys1", if not specified, will use nominal model
        '''
        self._kind = value
    #----------------------------------------------------
    def _get_ds_model(self, ds, nent_mm, nent_ee):
        log.info('Getting model')
        self._pdf_mm = self._get_pdf(preffix=f'mm_{ds}', nent=nent_mm)
        self._pdf_ee = self._get_pdf(preffix=f'ee_{ds}', nent=nent_ee)
    
        return self._pdf_mm, self._pdf_ee
    #----------------------------------------------------
    def _plot_data(self, key, dat):
        if self._out_dir is None:
            return

        plt_dir = f'{self._out_dir}/plots/data'
        os.makedirs(plt_dir, exist_ok=True)

        arr_dat = dat.value().numpy()

        plt.hist(arr_dat, bins=50)

        log.info(f'Saving to: {plt_dir}/{key}.png')
        plt.title(f'{key}; {dat.name}')
        plt.savefig(f'{plt_dir}/{key}.png')
        plt.close('all')
    #---------------------------------------------------------------
    def _update_efficiencies(self):
        if self._d_bdt_wp is None:
            log.info('Using nominal WP efficiencies')
            return

        log.debug('---------------------')
        log.info('Updating efficiencies')
        log.debug('---------------------')
        for dset_trig in self._l_dset:
            if dset_trig in ['all_TOS', 'all_TIS']:
                for single_ds in [ dset_trig.replace('all', dset) for dset in self._l_all_dset ]:
                    self._update_ds_efficiencies(single_ds)
            else:
                self._update_ds_efficiencies(dset_trig)

        log.debug('---------------------')
    #---------------------------------------------------------------
    def _update_ds_efficiencies(self, dset_trig):
        try:
            [dset, trg] = dset_trig.split('_')
        except:
            log.error(f'Cannot extract dataset and trigger from: {dset_trig}')
            raise

        trig    = 'ETOS' if trg == 'TOS' else 'GTIS'

        obj_ee  = scl_rdr(wp=self._d_bdt_wp, version=self._bdt_eff_vers, dset=dset, trig=  trig)
        scl_ee  = obj_ee.get_scale()

        obj_mm  = scl_rdr(wp=self._d_bdt_wp, version=self._bdt_eff_vers, dset=dset, trig='MTOS')
        scl_mm  = obj_mm.get_scale()

        eff_mm, eff_ee         = self._d_eff[dset_trig]
        EFF_mm, EFF_ee         = eff_mm * scl_mm, eff_ee * scl_ee
        self._d_eff[dset_trig] = EFF_mm         , EFF_ee

        log.debug(f'Dataset: {dset}')
        log.debug(f'(ee) {EFF_ee:.3e} = {scl_ee:.3e} * {eff_ee:.3e}')
        log.debug(f'(mm) {EFF_mm:.3e} = {scl_mm:.3e} * {eff_mm:.3e}')
        log.debug('')
    #----------------------------------------------------
    def _get_selected_entries(self):
        d_nent_sel = {}
        self._update_efficiencies()

        for ds in self._l_dset:
            nent_mm = 0
            nent_ee = 0
            if ds in ['all_TOS', 'all_TIS']:
                for single_ds in [ ds.replace('all', dset) for dset in self._l_all_dset ]:
                    nmm, nee = self._get_ds_sel_nent(single_ds)
                    nent_mm += nmm
                    nent_ee += nee
            else:
                nent_mm, nent_ee = self._get_ds_sel_nent(ds)

            d_nent_sel[ds] = nent_mm, nent_ee

        return d_nent_sel
    #----------------------------------------------------
    def _get_ds_sel_nent(self, dset):
        [ds_only, trig]= dset.split('_')
        nent           = self._d_nent[ds_only]

        eff_mm, eff_ee = self._d_eff[dset]
        nent_mm        = self._rk * nent * eff_mm
        nent_ee        =            nent * eff_ee 

        log.debug(f'{dset}:')
        log.debug(f'{nent_mm:15.0f}={self._rk:5.3e} * {nent:5.0f} * {eff_mm:5.3e}')
        log.debug(f'{nent_ee:15.0f}={       1:5.3e} * {nent:5.0f} * {eff_ee:5.3e}')
        log.debug('')

        return nent_mm, nent_ee
    #----------------------------------------------------
    def _cache_model(self):
        log.info('Caching models')
        d_nent_sel = self._get_selected_entries()
        d_mod      = {}

        mod_mm_tos = None
        for ds, (nent_mm, nent_ee) in d_nent_sel.items():
            if self._l_sub_dset is not None and ds not in self._l_sub_dset:
                continue

            mod_mm, mod_ee = self._get_ds_model(ds, nent_mm, nent_ee)
            if 'TIS' in ds:
                mod_mm = mod_mm_tos
            else:
                mod_mm_tos = mod_mm

            d_mod[ds]      = mod_mm, mod_ee

            self._plot_model(f'{ds}_mm', mod_mm)
            self._plot_model(f'{ds}_ee', mod_ee)

        self._d_mod = d_mod
    #----------------------------------------------------
    def get_model(self):
        '''
        Returns
        -----------------
        d_ent (dict): Returns a dictionary: {name : tup} where
            name (str)  : model identifier, e.g. r1_ETOS
            tup  (tuple): Tuple with muon and electron PDFs, e.g. pdf_mm, pdf_ee 

        For muon, TIS model is the TOS one.
        '''

        self._initialize()

        return self._d_mod
    #----------------------------------------------------
    def _add_ck(self, d_par):
        regex='nsg_ee_([0-9a-z]+_(TIS|TOS)_.*)'
        d_par_ck = {}
        for var_name in d_par:
            mtch = re.match(regex, var_name)
            if not mtch:
                continue

            suffix = mtch.group(1)

            ee_yld_name = var_name
            mm_yld_name = var_name.replace('_ee_', '_mm_').replace('_TIS_', '_TOS_')

            ee_yld, _   = d_par[ee_yld_name]
            mm_yld, _   = d_par[mm_yld_name]

            d_par_ck[f'ck_{suffix}'] = [ (self._rk * ee_yld) / mm_yld, 0]

        d_par.update(d_par_ck)

        return d_par
    #----------------------------------------------------
    def _add_ext_constraints(self, d_par, d_var):
        if d_var is None:
            log.warning(f'Not adding errors for constrained parameters in prefit dictionary')
            return d_par

        d_par_new = {}
        for name, var in d_var.items():
            if name not in d_par:
                log.error(f'Cannot find {name} in prefit dictionary:')
                pprint.pprint(d_par.keys())
                raise

            val = d_par[name][0]
            err = math.sqrt(var)

            d_par_new[name] = [val, err]

        d_par.update(d_par_new)

        return d_par
    #----------------------------------------------------
    def _add_ck_constraints(self, d_par, ck_cov):
        if ck_cov is None:
            log.warning(f'Not adding errors for ck parameters in prefit dictionary')
            return d_par

        d_par_new={}
        counter=0
        for name, [val, _] in d_par.items():
            if not name.startswith('ck_'):
                continue

            var = ck_cov[counter][counter]
            err = math.sqrt(var)

            d_par_new[name] = [val, err]
            counter+=1

        d_par.update(d_par_new)

        return d_par
    #----------------------------------------------------
    def get_prefit_pars(self, d_var=None, ck_cov=None):
        '''
        Used to get model parameters used to make the toy data

        Parameters
        --------------------
        d_var (dict): Dictionary with variances for parameters that are constrained. If pased the
        constraint widths will be added as errors in the prefit dictionary

        ck_cov (numpy.array): nxn numpy array representing covariance matrix for ck parameters

        Returns 
        --------------------
        d_par (dict): Dictionary storing the prefit parameters (used to build the model) and their
        errors, e.g. {'par_x' : (3, 1)}
        '''
        self._initialize()

        d_model = self.get_model()

        d_par = {}
        for mod_mm, mod_ee in d_model.values():
            d_par_mm = { par.name : [ par.value().numpy(), 0] for par in mod_mm.get_params() }
            d_par_ee = { par.name : [ par.value().numpy(), 0] for par in mod_ee.get_params() }

            d_par.update(d_par_ee)
            d_par.update(d_par_mm)

        d_par['rk'] = [self._rk, 0]
        d_par       = self._add_ck(d_par)
        d_par       = self._add_ext_constraints(d_par, d_var)
        d_par       = self._add_ck_constraints(d_par, ck_cov)

        return d_par
    #----------------------------------------------------
    def get_data(self, rseed=3):
        '''
        Returns toy data from model

        Parameters:
        -----------------
        rseed  (int):  Random seed

        Returns:
        -----------------
        d_data (dict): Dictionary with dataset and tuple of zfit data objects paired, i.e. {r1_TOS : (pdf_mm, pdf_ee) }

        For muon, TIS dataset is the TOS one.
        '''
        self._initialize()

        zfit.settings.set_seed(rseed)

        d_data     = {}
        dst_mm_tos = None
        for ds, (pdf_mm, pdf_ee) in self._d_mod.items():
            dst_mm         = pdf_mm.create_sampler(fixed_params=False)
            dst_ee         = pdf_ee.create_sampler(fixed_params=False)

            if 'TIS' in ds:
                dst_mm = dst_mm_tos
            else:
                dst_mm_tos = dst_mm

            d_data[ds]     = dst_mm, dst_ee

            self._plot_data(f'{ds}_mm', dst_mm)
            self._plot_data(f'{ds}_ee', dst_ee)

            log.debug(f'Electron data: {dst_ee.numpy().shape[0]}')
            log.debug(f'Muon data: {dst_mm.numpy().shape[0]}')

        return d_data
    #----------------------------------------------------
    @staticmethod
    def show(d_mod):
        s_dset = { key.split('_')[0] for key in d_mod }
        for dset in s_dset:
            pdf_mm_tos, pdf_ee_tos = d_mod[f'{dset}_TOS']
            pdf_mm_tis, pdf_ee_tis = d_mod[f'{dset}_TIS']

            l_par_name_mm_tos = ', '.join([ par.name for par in pdf_mm_tos.get_params() ])
            l_par_name_mm_tis = ', '.join([ par.name for par in pdf_mm_tis.get_params() ])
            l_par_name_ee_tos = ', '.join([ par.name for par in pdf_ee_tos.get_params() ])
            l_par_name_ee_tis = ', '.join([ par.name for par in pdf_ee_tis.get_params() ])

            log.info('')
            log.info(f'{dset}')
            log.info('-' * 20)
            log.info(f'{"mm TOS":<10}{l_par_name_mm_tos:<60}')
            log.info(f'{"mm TIS":<10}{l_par_name_mm_tis:<60}')
            log.info(f'{"ee TOS":<10}{l_par_name_ee_tos:<60}')
            log.info(f'{"ee TIS":<10}{l_par_name_ee_tis:<60}')
            log.info('-' * 20)
    #----------------------------------------------------
    @staticmethod
    def get_cov(kind='diag_eq', c = 0.01):
        if   kind == 'diag_eq':
            mat = numpy.diag([c] * 8)
        elif kind == 'random':
            mat = numpy.random.rand(8, 8)
            numpy.fill_diagonal(mat, 1)
            mat = mat * c
        else:
            log.error(f'Invalid kind: {kind}')
            raise
    
        return mat 
    #----------------------------------------------------
    @staticmethod
    def get_rjpsi(kind='one'):
        d_rjpsi = {}
    
        if   kind == 'one':
            d_rjpsi['d1'] = 1 
            d_rjpsi['d2'] = 1 
            d_rjpsi['d3'] = 1 
            d_rjpsi['d4'] = 1 
        elif kind == 'eff_bias':
            d_rjpsi['d1'] = 0.83333333 
            d_rjpsi['d2'] = 0.83333333 
            d_rjpsi['d3'] = 0.83333333 
            d_rjpsi['d4'] = 0.83333333 
        else:
            log.error(f'Wrong kind: {kind}')
            raise
    
        return d_rjpsi
    #----------------------------------------------------
    @staticmethod
    def get_eff(kind='equal'):
        d_eff = {}
        if   kind == 'diff':
            d_eff['d1'] = (0.6, 0.3)
            d_eff['d2'] = (0.5, 0.2)
            d_eff['d3'] = (0.7, 0.3)
            d_eff['d4'] = (0.8, 0.4)
        elif kind == 'half':
            d_eff['d1'] = (0.6, 0.3)
            d_eff['d2'] = (0.6, 0.3)
            d_eff['d3'] = (0.6, 0.3)
            d_eff['d4'] = (0.6, 0.3)
        elif kind == 'equal':
            d_eff['d1'] = (0.3, 0.3)
            d_eff['d2'] = (0.3, 0.3)
            d_eff['d3'] = (0.3, 0.3)
            d_eff['d4'] = (0.3, 0.3)
        elif kind == 'bias':
            d_eff['d1'] = (0.6, 0.25)
            d_eff['d2'] = (0.6, 0.25)
            d_eff['d3'] = (0.6, 0.25)
            d_eff['d4'] = (0.6, 0.25)
        else:
            log.error(f'Invalid kind: {kind}')
            raise
    
        return d_eff
#----------------------------------------------------

