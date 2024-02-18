from logzero           import logger         as log
import os
import numpy
import pprint
import tarfile
import jacobi       as jac
import utils_noroot as utnr

from stats import average as stav

#----------------------------------------
class cs_reader:
    '''
    Class used to MC version of parameters used in rare fit model
    '''
    #------------------------
    def __init__(self, version=None, preffix=None): 
        '''
        version (str): Version of fit to rare mode 
        '''
        self._ver         = version 
        self._preffix     = preffix 

        self._l_ds_lab    = ['r1_TOS', 'r1_TIS', 'r2p1_TOS', 'r2p1_TIS', '2017_TOS', '2017_TIS', '2018_TOS', '2018_TIS']
        self._l_trig      = ['MTOS', 'ETOS', 'GTIS']
        self._l_year      = ['2011', '2012', '2015', '2016', '2017', '2018']
        self._l_dset      = ['r1', 'r2p1', '2017', '2018']
        self._l_brem      = ['0', '1', '2']
        self._l_params    = ['mu', 'sg']
        self._d_val       = {}
        self._d_var       = {}

        self._d_d_d_mc    = None 
        self._d_d_d_dt    = None 
        self._cache_dir   = None
        self._cache       = False
        self._initialized = False 
    #------------------------
    @property
    def cache(self):
        return self._cache

    @cache.setter
    def cache(self, value):
        if value not in [True, False]:
            log.error(f'Invalid cache value: {value}')
            raise ValueError

        self._cache = value
    #------------------------
    @property
    def cache_dir(self):
        if self._cache_dir is None:
            return

        return cache_dir

    @cache_dir.setter
    def cache_dir(self, value):
        cache_dir = f'{value}'
        try:
            os.makedirs(cache_dir, exist_ok=True)
        except:
            log.error(f'Cannot create: {cache_dir}')
            raise ValueError

        self._cache_dir = cache_dir
    #------------------------
    def _initialize(self):
        if self._initialized:
            return

        if self._cache_dir is None:
            self.cache_dir = '/tmp/cs_reader'
            log.warning(f'Using default caching directory: {self._cache_dir}')

        self._set_paths()
        self._cache_data('signal')
        self._cache_data('data')
        self._tar_data()

        self._initialized = True
    #------------------------
    def _set_paths(self):
        if self._cache_dir is not None:
            log.info(f'Cache dir: {self._cache_dir}')
        else: 
            self._cache_dir = f'/tmp/cs_reader/{self._vers}'
            log.debug(f'Cache dir: {self._cache_dir}')

        os.makedirs(self._cache_dir, exist_ok=True)
    #------------------------
    def _merge_brem(self, d_d_par_brem):
        d_par = {}
        for param in self._l_params:
            l_val = []
            l_err = []
            for brem in self._l_brem:
                val, err  = d_d_par_brem[brem][param]
                l_val.append(val)
                l_err.append(err)

            arr_val = numpy.array(l_val)
            arr_err = numpy.array(l_err)

            avg, err, pval = stav.average(arr_val, arr_err)

            d_par[param] = avg, err

        return d_par
    #------------------------
    def _merge_runs(self, d_d_par_year):
        d_r1   = self._merge_years('2011', '2012', d_d_par_year)
        d_r2p1 = self._merge_years('2015', '2016', d_d_par_year)

        d_d_par_dset         = {}
        d_d_par_dset['r1']   = d_r1
        d_d_par_dset['r2p1'] = d_r2p1
        d_d_par_dset['2017'] = d_d_par_year['2017']
        d_d_par_dset['2018'] = d_d_par_year['2018']

        return d_d_par_dset
    #------------------------
    def _merge_years(self, y1, y2, d_d_par_year):
        d_par_y1 = d_d_par_year[y1]
        d_par_y2 = d_d_par_year[y2]
        d_par_ds = {}
        for param in self._l_params:
            val_y1, err_y1 = d_par_y1[param]
            val_y2, err_y2 = d_par_y2[param]

            arr_val = numpy.array([val_y1, val_y2])
            arr_err = numpy.array([err_y1, err_y2])

            avg, err, pval = stav.average(arr_val, arr_err)

            d_par_ds[param] =  avg, err

        return d_par_ds
    #------------------------
    def _is_cached(self, json_path, name):
        if self._cache and os.path.isfile(json_path):
            log.info(f'Loading cached parameters from: {json_path}')

            if name == 'signal':
                self._d_d_d_mc = utnr.load_json(json_path)
            else:
                self._d_d_d_dt = utnr.load_json(json_path)

            return True

        return False
    #------------------------
    def _cache_data(self, name):
        json_path = f'{self._cache_dir}/constraints_{name}.json'
        if self._is_cached(json_path, name):
            return

        log.info('Reloading parameters')
        d_d_d_par_year_trig = {} 
        for trig in self._l_trig:
            d_d_par_year = {}
            for year in self._l_year:
                d_d_par_brem = {}
                l_brem = ['0'] if trig == 'MTOS' else self._l_brem
                for brem in l_brem:
                    d_par = self._get_pars(trig, year, brem, name)
                    d_d_par_brem[brem] = d_par

                d_d_par_year[year] = d_d_par_brem['0'] if trig == 'MTOS' else self._merge_brem(d_d_par_brem)

            d_d_d_par_year_trig[trig] = self._merge_runs(d_d_par_year)

        d_val = self._format_data(d_d_d_par_year_trig)
        if name == 'signal':
            self._d_d_d_mc = d_val 
        else:
            self._d_d_d_dt = d_val 

        log.info(f'Saving to: {json_path}')
        utnr.dump_json(d_val, json_path)
    #------------------------
    def _tar_data(self):
        tar_path = f'{self._cache_dir}.tar.gz'

        if os.path.isfile(tar_path):
            return

        json_dir = os.path.basename(self._cache_dir)
        with tarfile.open(tar_path, 'w:gz') as tar:
            tar.add(self._cache_dir, arcname=json_dir)

        log.info(f'Making: {tar_path}')
    #------------------------
    def _format_data(self, d_d_d_par_year_trig):
        d_d_d_dset_parm_trig = {}
        for dset in self._l_dset:
            d_d_parm_trig= {}
            for param in self._l_params:
                d_trig = {}
                v_mtos, e_mtos = d_d_d_par_year_trig['MTOS'][dset][param]
                v_etos, e_etos = d_d_d_par_year_trig['ETOS'][dset][param]
                v_gtis, e_gtis = d_d_d_par_year_trig['GTIS'][dset][param]

                d_trig['MTOS'] = v_mtos, e_mtos
                d_trig['ETOS'] = v_etos, e_etos
                d_trig['GTIS'] = v_gtis, e_gtis

                d_d_parm_trig[param] = d_trig

            d_d_d_dset_parm_trig[dset] = d_d_parm_trig

        return d_d_d_dset_parm_trig
    #------------------------
    def _get_pars(self, trig, year, brem, name):
        cas_dir = os.environ['CASDIR']

        jsn_path= f'{cas_dir}/monitor/mass_scales/{self._ver}/{year}_{trig}/pars/cat_{brem}/{name}.json'
        d_data  = utnr.load_json(jsn_path)

        d_par       = {}
        d_par['mu'] = d_data['mu']
        d_par['sg'] = d_data['sg']

        return d_par
    #------------------------
    def _compute_const(self):
        for trig in self._l_trig:
            for dset in self._l_dset:
                for par in self._l_params:
                    val_mc = self._d_d_d_mc[dset][par][trig]
                    val_dt = self._d_d_d_dt[dset][par][trig]


                    val, var         = self._get_val(par, val_mc, val_dt)
                    key              = self._get_key(par, trig, dset)
                    self._d_val[key] = val
                    self._d_var[key] = var
    #------------------------
    def _get_key(self, par, trig, dset):
        chan = 'mm'  if trig == 'MTOS' else 'ee'
        trig = 'TIS' if trig == 'GTIS' else 'TOS'
        par  = {'mu' : 'dmu', 'sg' : 'rsg'}[par]

        return f'{par}_{chan}_{dset}_{trig}_{self._preffix}'
    #------------------------
    def _get_val(self, name, val_mc, val_dt):
        if name == 'mu':
            val, var = jac.propagate(lambda x : x[0] - x[1], [val_dt[0], val_mc[0]], [[val_dt[1] ** 2, 0], [0, val_mc[1] ** 2]])
        elif name == 'sg':
            val, var = jac.propagate(lambda x : x[0] / x[1], [val_dt[0], val_mc[0]], [[val_dt[1] ** 2, 0], [0, val_mc[1] ** 2]])
        else:
            log.error(f'Invalid parameter: {name}')
            raise ValueError

        return float(val), float(var)
    #------------------------
    def get_constraints(self):
        '''
        Will return a dictionary with values in MC for a given fitting parameter

        Returns
        ------------------
        x, y (tuple) : Tuple with x and y where

        x: Dictionary mapping parameter name and value to which to constrain it {name : val} 
        x: Dictionary mapping parameter name and variance to which to constrain it {name : var} 
        '''
        self._initialize()

        self._compute_const()

        return self._d_val, self._d_var
#----------------------------------------

