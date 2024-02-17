import os
import re
import glob
import ROOT
import tqdm
import math
import numpy
import pprint
import pandas            as pnd
import utils_noroot      as utnr
import matplotlib.pyplot as plt
import read_selection    as rs

from importlib.resources import files
from scipy.interpolate   import griddata as spy_grid
from log_store           import log_store

log = log_store.add_logger(name='rk_extractor:scale_reader')
#------------------------------------------------------------
class scale_reader:
    '''
    Class used to read efficiencies under different BDT working points and
    return scale factor
    '''
    #--------------------------
    def __init__(self, wp=None, version=None, dset=None, trig=None):
        '''
        Parameters
        --------------------------
        wp (dict): Stores working point ends for the scan, i.e. {'BDT_cmb' : (0.5, 1.0)} 
        version (str): Version of efficiency file

        dset (str): Dataset, e.g. r1
        trig (str): Trigger, e.g. MTOS
        '''
        self._d_wp        = wp 
        self._dset        = dset
        self._trig        = trig
        self._vers        = version

        self._d_lumi_wgt  = {'2011' : 1/8.7, '2012' : 2/8.7, '2015' : 0.3/8.7, '2016' : 1.6/8.7, '2017' : 1.7/8.7, '2018' : 2.1/8.7} 
        self._df          = None

        self._cmb_nom     = None
        self._prc_nom     = None

        self._cmb_new     = self._d_wp['BDT_cmb'] 
        self._prc_new     = self._d_wp['BDT_prc'] 
        self._regex       = 'BDT_cmb > ([\.,\d]+) && BDT_prc > ([\.,\d]+)'

        self._cmb_rng     = None
        self._prc_rng     = None

        self._initialized = False
    #--------------------------
    def _initialize(self):
        if self._initialized:
            return

        self._load_data()
        self._get_min_max()
        self._check_wp()
        self._read_nominal_wp()

        self._initialized = True 
    #--------------------------
    def _get_min_max(self):
        min_cmb = self._df.BDT_cmb.min()
        max_cmb = self._df.BDT_cmb.max()

        min_prc = self._df.BDT_prc.min()
        max_prc = self._df.BDT_prc.max()

        self._cmb_rng = min_cmb, max_cmb
        self._prc_rng = min_prc, max_prc
    #--------------------------
    def _check_wp(self):
        try:
            low, hig = self._cmb_new
            assert hig > low
        except:
            log.error(f'Expected tuple of two ordered elements, got: {self._cmb_new}')
            raise

        try:
            low, hig = self._prc_new
            assert hig > low
        except:
            log.error(f'Expected tuple of two ordered elements, got: {self._prc_new}')
            raise
    #--------------------------
    def _read_nominal_wp(self):
        selection = rs.get('bdt', self._trig, q2bin='high', year = 'none')
        mch = re.match(self._regex, selection)
        if not mch:
            log.error(f'Cannot find WP in: {selection}')
            raise

        [cmb_str, prc_str] = mch.groups()

        self._cmb_nom = float(cmb_str), 100 
        self._prc_nom = float(prc_str), 100 

        log.debug(f'Using nominal WP: {self._cmb_nom}, {self._prc_nom}')
    #--------------------------
    def _load_data(self):
        if   self._dset == 'r1':
            l_year = ['2011', '2012']
        elif self._dset == 'r2p1':
            l_year = ['2015', '2016']
        elif self._dset in ['2017', '2018']:
            l_year = [self._dset]
        elif self._dset == 'all':
            l_year = ['2011', '2012', '2015', '2016', '2017', '2018']
        else:
            log.error(f'Invalid dataset: {self._dset}')
            raise

        l_df     = [ self._load_year(year) for year in l_year ]

        self._df = pnd.concat(l_df, axis=0)
    #--------------------------
    def _load_year(self, year):
        file_path = files('extractor_data').joinpath(f'sig_wgt/{self._vers}/{self._trig}_{year}.json')
        if not os.path.isfile(file_path):
            log.error(f'File not found: {file_path}')
            raise

        df        = pnd.read_json(file_path)
        df['wgt'] = df['wgt'] * self._d_lumi_wgt[year]

        return df
    #--------------------------
    def _check_range(self, t_wpt, t_bound, kind):
        if (t_wpt[0] - t_bound[0]) < -0.01:
            log.warning(f'For WP of kind {kind}, {t_wpt[0]} < {t_bound[0]}')
    #--------------------------
    def _read_yield(self, t_cmb=None, t_prc=None):
        self._check_range(t_cmb, self._cmb_rng, 'BDT_cmb')
        self._check_range(t_prc, self._prc_rng, 'BDT_prc')

        cmb_lo, cmb_hi = t_cmb
        prc_lo, prc_hi = t_prc

        df = self._df
        value_init = df.wgt.sum()

        cmb_cut = f'(BDT_cmb > {cmb_lo:.3f}) & (BDT_cmb < {cmb_hi:.3f})'
        prc_cut = f'(BDT_prc > {prc_lo:.3f}) & (BDT_prc < {prc_hi:.3f})'

        df = df.query(cmb_cut)
        df = df.query(prc_cut)

        value_final = df.wgt.sum()

        log.debug(f'BDT cmb: {cmb_cut}')
        log.debug(f'BDT prc: {prc_cut}')
        log.debug(f'Yield: {value_init:.0f} -> {value_final:.0f}')

        return value_final
    #--------------------------
    def get_scale(self):
        '''
        Returns
        -------------------
        scale (float): Yield ratio between WP and nominal.
        '''
        self._initialize()

        yld_nom = self._read_yield(t_cmb=self._cmb_nom, t_prc=self._prc_nom)
        yld_new = self._read_yield(t_cmb=self._cmb_new, t_prc=self._prc_new)
        scale   = yld_new / yld_nom
        log.debug(f'{scale:.3f}= {yld_new:.0f}/{yld_nom:.0f}')

        if scale == 0:
            new_scale = 1e-3
            log.warning(f'Found a scale of {scale}, using {new_scale}')
            return new_scale 

        return scale
#------------------------------------------------------------

