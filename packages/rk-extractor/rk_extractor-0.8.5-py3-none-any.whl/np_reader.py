import os
import numpy
import tarfile
import utils_noroot as utnr

from importlib.resources import files
from ndict               import ndict
from rk.eff_yld_loader   import eff_yld_loader as eyl
from log_store           import log_store

log = log_store.add_logger('rk_extractor:np_reader')
#----------------------------------------
class np_reader:
    '''
    Class used to read nuisance parameters to calculate RK
    '''
    #------------------------
    def __init__(self, sys=None, sta=None, yld=None):
        '''
        sys (str): Version of efficiencies obtained when assessing systematics
        sta (str): Version of efficiencies obtained when assessing statistical uncertainties with bootstrapping
        yld (str): Version of fitted data yields (only Jpsi and Psi2S)
        '''
        self._sys         = sys 
        self._sta         = sta
        self._yld         = yld

        self._cov_dir     = None
        self._d_yld       = ndict()
        self._d_eff       = ndict()
        self._sys_flg     = 'pall_tall_gall_lall_hall_rall_qall_bnom_snom'
        self._l_ds_lab    = ['r1_TOS', 'r1_TIS', 'r2p1_TOS', 'r2p1_TIS', '2017_TOS', '2017_TIS', '2018_TOS', '2018_TIS']

        self._initialized = False 
    #------------------------
    def _initialize(self):
        if self._initialized:
            return

        self._cache_dir = files('extractor_data').joinpath(f'npr_data/{self._sys}_{self._sta}_{self._yld}')
        os.makedirs(self._cache_dir, exist_ok=True)

        self._cache_data(channel='ee')
        self._cache_data(channel='mm')
        self._check_data()

        self._initialized = True
    #------------------------
    def _check_data(self):
        for key, l_yld in self._d_yld.items():
            if len(l_yld) == len(self._l_ds_lab):
                continue

            log.error(f'Lengths of yields for {key} does not align with labels: {self._l_ds_lab} <=> {l_yld}')
            raise

        for key, l_eff in self._d_eff.items():
            if len(l_eff) == len(self._l_ds_lab):
                continue

            log.error(f'Lengths of efficiencies for {key} does not align with labels: {self._l_ds_lab} <=> {l_eff}')
            raise
    #------------------------
    def _find_cached(self, path):
        if not os.path.isfile(path):
            log.debug(f'File not cached: {path}')
            return False 

        log.debug(f'File cached: {path}')

        return True
    #------------------------
    def _cache_data(self, channel=None):
        '''
        For a given channel, ee or mm, it will fill the dictionary of efficiencies for each
        dataset and trigger.
        '''
        if channel not in ['ee', 'mm']:
            log.error(f'Wrong channel: {channel}')
            raise ValueError

        eff_cache_path = f'{self._cache_dir}/eff_{channel}.json'
        yld_cache_path = f'{self._cache_dir}/yld_{channel}.json'
        sys_cache_path = f'{self._cache_dir}/sys_{channel}.json'
        sta_cache_path = f'{self._cache_dir}/sta_{channel}.json'

        is_cov = self._find_cached(sys_cache_path) and self._find_cached(sta_cache_path)
        is_eyl = self._find_cached(eff_cache_path) and self._find_cached(yld_cache_path) 

        if is_eyl and is_cov:
            log.info(f'Cached data found for channel: {channel}')
            self._d_eff = utnr.load_json(eff_cache_path, decoder=ndict.json_decoder)
            self._d_yld = utnr.load_json(yld_cache_path, decoder=ndict.json_decoder)
            self._cvsys = utnr.load_json(sys_cache_path)
            self._cvsta = utnr.load_json(sta_cache_path)

            return

        log.info(f'Cached data not found caching for channel: {channel}')
        l_trg = ['ETOS', 'GTIS'] if channel == 'ee' else ['MTOS', 'MTOS']
        for proc in ['sign', 'ctrl']:
            l_eff = []
            l_yld = []
            for year in ['r1', 'r2p1', '2017', '2018']:
                for trig in l_trg:
                    eff, yld = self._get_eff_yld(f'{proc}_{channel}', year, trig)

                    l_eff.append(eff)
                    l_yld.append(yld)

            self._d_eff[proc, channel] = l_eff
            self._d_yld[proc, channel] = l_yld

        eff_dir       = os.environ['EFFDIR']
        self._cov_dir = f'{eff_dir}/../covariance'
        self._cvsys   = self._get_cov(kind='sys')
        self._cvsta   = self._get_cov(kind='sta')

        utnr.dump_json(self._d_eff, eff_cache_path, encoder=ndict.json_encoder)
        utnr.dump_json(self._d_yld, yld_cache_path, encoder=ndict.json_encoder)
        utnr.dump_json(self._cvsys, sys_cache_path)
        utnr.dump_json(self._cvsta, sta_cache_path)
    #------------------------
    def _get_eff_yld(self, proc, year, trig):
        '''
        Will return numerical value of efficiency and fitted yield, for a specifi process
        in a year and trigger
        '''
        obj        = eyl(proc, trig, year, self._sys_flg)
        obj.eff_var= 'B_PT'
        t_yld, d_eff = obj.get_values(eff_version = self._sys, yld_version=self._yld)

        ctf  = d_eff['nom', 'B_PT']
        deff = ctf.efficiency
        oeff = deff.efficiency()
        eff  = oeff.val[0]
        yld  = t_yld[0]

        return eff, yld
    #------------------------
    def get_cov(self, kind=None):
        '''
        Will return covariance matrix (nxn numpy array)
        '''
        self._initialize()

        if kind not in ['sys', 'sta']:
            log.error(f'Invalid covariance kind: {kind}')
            raise ValueError

        cov_mat = self._cvsys if kind == 'sys' else self._cvsta

        return numpy.array(cov_mat)
    #------------------------
    def _get_cov(self, kind=None):
        if kind not in ['sys', 'sta']:
            log.error(f'Invalid uncertainty: {kind}')
            raise ValueError

        eff_ver  = self._sys if kind == 'sys' else self._sta
        pkl_path = f'{self._cov_dir}/{eff_ver}_{self._yld}/rx/matrix_abs_rc/tot.pkl'
        log.info(f'Picking up covariance from: {pkl_path}')
        cov      = utnr.load_pickle(pkl_path)

        return cov.tolist()
    #------------------------
    def get_eff(self):
        '''
        Will return rare mode efficiencies

        d_eff (dict): Dictionary {ds : (eff_mm, eff_ee)} with efficiency objects
        '''
        self._initialize()

        l_eff_rare_mm = self._d_eff['sign', 'mm'] 
        l_eff_rare_ee = self._d_eff['sign', 'ee'] 

        d_eff = {}
        for ds_lab, eff_mm, eff_ee in zip(self._l_ds_lab, l_eff_rare_mm, l_eff_rare_ee):
            d_eff[ds_lab] = eff_mm, eff_ee

        return d_eff 
    #------------------------
    def get_byields(self):
        '''
        Will return dictionary with efficiency corrected yields {ds : yld}
        e.g. {'r1_TIS_ee': 40021323}
        '''
        self._initialize()

        arr_eff_jpsi_mm = numpy.array(self._d_eff['ctrl', 'mm'])
        arr_eff_jpsi_ee = numpy.array(self._d_eff['ctrl', 'ee'])

        arr_yld_jpsi_mm = numpy.array(self._d_yld['ctrl', 'mm'])
        arr_yld_jpsi_ee = numpy.array(self._d_yld['ctrl', 'ee'])

        arr_yld_jpsi_mm = arr_yld_jpsi_mm / arr_eff_jpsi_mm
        arr_yld_jpsi_ee = arr_yld_jpsi_ee / arr_eff_jpsi_ee 

        d_byld_ee = {f'{ds}_ee' : byld for ds, byld in zip(self._l_ds_lab, arr_yld_jpsi_ee)}
        d_byld_mm = {f'{ds}_mm' : byld for ds, byld in zip(self._l_ds_lab, arr_yld_jpsi_mm)}

        d_byld= {}
        d_byld.update(d_byld_ee)
        d_byld.update(d_byld_mm)

        return d_byld
    #------------------------
    def get_rjpsi(self):
        '''
        Will return an array with rjpsi for every trigger and dataset 
        '''
        self._initialize()

        arr_eff_jpsi_mm = numpy.array(self._d_eff['ctrl', 'mm'])
        arr_eff_jpsi_ee = numpy.array(self._d_eff['ctrl', 'ee'])

        arr_yld_jpsi_mm = numpy.array(self._d_yld['ctrl', 'mm'])
        arr_yld_jpsi_ee = numpy.array(self._d_yld['ctrl', 'ee'])

        arr_rjpsi = (arr_yld_jpsi_mm / arr_yld_jpsi_ee) * (arr_eff_jpsi_ee / arr_eff_jpsi_mm)

        d_rjpsi   = {ds : rjpsi for ds, rjpsi in zip(self._l_ds_lab, arr_rjpsi)}

        return d_rjpsi
#----------------------------------------

