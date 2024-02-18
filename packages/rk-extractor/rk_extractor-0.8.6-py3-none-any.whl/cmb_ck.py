import os
import math
import numpy
import pprint
import jacobi            as jac
import matplotlib.pyplot as plt

from logzero import logger as log
#----------------------------------------
class combiner:
    '''
    Class used to combine CK values from multiple datasets into
    a combined one
    '''
    #----------------------------------------
    def __init__(self, rk=None, eff=None, yld=None):
        '''
        rk (float): Value of RK for which the toy test is made
        eff (dict): Holds the muon and electron full efficiencies, e.g. {'r1_TOS' : (eff_mu, eff_ee)}
        yld (dict): Holds the yields of rare decays of B mesons, before any selection, e.g. {'r1_TOS' : yld}
        '''

        self._rk     = rk 
        self._d_eff  = eff
        self._d_yld  = yld 
        self._l_dset = ['r1', 'r2p1', '2017', '2018']
        self._l_trig = ['TOS', 'TIS']

        self._out_dir     = None
        self._initialized = False
    #----------------------------------------
    def _initialize(self):
        if self._initialized:
            return

        self._pad_yields()

        right_sizes = len(self._d_yld)       == len(self._d_eff) 
        right_keys  =     self._d_yld.keys() ==     self._d_eff.keys()

        if not right_sizes:
            log.error(f'Sizes of inputs is wrong:')
            pprint.pprint(self._d_yld)
            pprint.pprint(self._d_eff)
            raise

        if not right_keys:
            log.error(f'Sizes of input dictionaries are different')
            raise

        self._initialized = True
    #----------------------------------------
    def _pad_yields(self):
        d_yld = {}
        for key, val in self._d_yld.items():
            d_yld[f'{key}_TOS'] = val
            d_yld[f'{key}_TIS'] = val

        self._d_yld = d_yld
    #----------------------------------------
    @property
    def out_dir(self):
        return self._out_dir

    @out_dir.setter
    def out_dir(self, value):
        try:
            os.makedirs(value, exist_ok=True)
        except:
            log.error(f'Cannot make directory: {value}')
            raise
        self._out_dir = value
    #----------------------------------------
    def _get_ck(self):
        l_ck = []

        for trig in self._l_trig:
            tot_ee, tot_mm = 0, 0
            for dset in self._l_dset:
                key = f'{dset}_{trig}'
                eff_mm, eff_ee = self._d_eff[key]
                yld            = self._d_yld[key]

                tot_mm += eff_mm * yld
                tot_ee += eff_ee * yld

            ck   = self._rk * tot_ee / tot_mm
            l_ck.append(ck)

        return l_ck 
    #----------------------------------------
    def get_combination(self):
        '''
        Parameters
        ------------
        add_tis (bool): If true, will return TIS ck and 2x2 covariance, if false, TIS is dropped

        Returns
        ------------
        Tuple with dictionaries with the rjpsi and efficiencies, e.g:

        d_rjpsi, d_eff, cov = cmb.get_cobination()

        the values of the first two dictionaries themselves are not meaningful, but when used
        to calculate ck, they should provide the right combined value
        '''
        self._initialize()

        [ck_val_tos, ck_val_tis] = self._get_ck()

        eff_val = 1 - 1e-6
        ck_var  = 1e-4

        d_rjpsi = {'all_TOS' :                    1., 'all_TIS' :                    1. }
        d_eff   = {'all_TOS' : (eff_val, ck_val_tos), 'all_TIS' : (eff_val, ck_val_tis) }
        cov     = [[ck_var, 0], [0, ck_var]]

        return d_rjpsi, d_eff, numpy.array(cov)
#----------------------------------------

