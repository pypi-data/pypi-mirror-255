from importlib.resources import files
from rk.calc_utility     import getGeomEff          as geo_eff
from datetime            import datetime
from log_store           import log_store

import os
import re
import math
import glob
import ROOT
import numpy
import utils
import mplhep
import pprint
import pandas            as pnd
import jacobi            as jac
import utils_noroot      as utnr
import matplotlib.pyplot as plt

log=log_store.add_logger(name='rk_extractor:scales')
#------------------------------------------
def get_proc_labels():
    d_proc_lab         = dict() 
    d_proc_lab['bpkp'] = r'$B^+\to K^+ e^+e^-$'
    d_proc_lab['bpks'] = r'$B^+\to K^{*+}(\to K\pi^0) e^+e^-$'
    d_proc_lab['bdks'] = r'$B^+\to K^{*0}(\to K\pi) e^+e^-$'
    d_proc_lab['bsph'] = r'$B_s\to \phi(\to K K) e^+e^-$'
    d_proc_lab['bpk1'] = r'$B^+\to K_1(\to K \pi\pi) e^+e^-$'
    d_proc_lab['bpk2'] = r'$B^+\to K_2(\to K \pi\pi) e^+e^-$'

    return d_proc_lab
#------------------------------------------
class eff_calc:
    def __init__(self, proc=None, year=None, trig=None):
        self._l_proc = ['bpkp', 'bpks', 'bdks', 'bsph', 'bpk1', 'bpk2']  if proc is None else proc
        self._l_trig = ['ETOS', 'GTIS']                                  if trig is None else trig
        self._l_year = ['2011', '2012', '2015', '2016', '2017', '2018']  if year is None else year

        self._d_proc_lab = get_proc_labels()
        self._d_geo_eff  = {}
        self._d_sel_tis  = {} 
        self._d_sel_tos  = {} 
        self._dvers      = 'v10.21p2'
        self._min_date   = '01.09.23'
        self._out_dir    = None

        plt.style.use(mplhep.style.LHCb2)

        self._initialized=False
    #------------------------------------------
    @property
    def out_dir(self):
        return self._out_dir

    @out_dir.setter
    def out_dir(self, value):
        try:
            os.makedirs(value, exist_ok=True)
        except:
            log.error(f'Cannot make: {value}')
            raise

        self._out_dir = value
    #------------------------------------------
    def get_efficiencies(self, d_sel=None):
        '''
        Parameters
        ---------------------
        d_sel (dict): If set, it will read the original files and apply the selection, e.g. {'BDT_cmb' : 'BDT_cmb > 0.977'}
        '''
        d_eff = {}
        log.info('-' * 20)
        log.info(f'{"Process":<15}{"Trigger":<15}{"Year":<15}')
        log.info('-' * 20)
        for proc in self._l_proc: 
            d_eff[proc] = {}
            for trig in self._l_trig: 
                d_eff[proc][trig] = {}
                for year in self._l_year: 
                    log.info(f'{proc:<15}{trig:<15}{year:<15}')
                    d_eff[proc][trig][year] = self._get_efficiency(proc=proc, trig=trig, year=year, d_sel=d_sel)
        log.info('-' * 20)

        self._plot_geo_eff()
        self._plot_sel_eff()

        return d_eff
    #------------------------------------------
    def _get_df_from_dict(self, d_data, ext_name=''):
        df = pnd.DataFrame(columns=['Process', 'Year', 'Value', 'Error'])
        for proc in self._l_proc:
            for year in self._l_year:
                key      = f'{proc}{ext_name}_{year}'
                val, err = d_data[key] 

                df = utnr.add_row_to_df(df, [proc, year, val, err] )

        return df
    #------------------------------------------
    def _plot_geo_eff(self):
        if self._out_dir is None:
            return

        df = self._get_df_from_dict(self._d_geo_eff, ext_name='_ee')

        plt_dir = f'{self._out_dir}/plots'
        os.makedirs(plt_dir, exist_ok=True)

        ax=None
        for proc, df_p in df.groupby('Process'):
            ax=df_p.plot(x='Year', y='Value', yerr='Error', ax=ax, label=self._d_proc_lab[proc], marker='o')

        plt_path = f'{plt_dir}/geo_eff.png'
        plt.grid()
        plt.ylim(0.00, 0.40)
        plt.savefig(plt_path)
        plt.close('all')
    #------------------------------------------
    def _plot_sel_eff(self):
        if self._out_dir is None:
            return

        plt_dir = f'{self._out_dir}/plots'
        os.makedirs(plt_dir, exist_ok=True)
        for trig, d_data in {'GTIS' : self._d_sel_tis , 'ETOS' : self._d_sel_tos}.items():
            if trig not in self._l_trig:
                continue
            df = self._get_df_from_dict(d_data)

            ax=None
            for proc, df_p in df.groupby('Process'):
                ax=df_p.plot(x='Year', y='Value', yerr='Error', ax=ax, label=self._d_proc_lab[proc], marker='o')

            plt_path = f'{plt_dir}/sel_eff_{trig}.png'
            plt.grid()
            plt.savefig(plt_path)
            plt.close('all')
    #------------------------------------------
    def _switch_sample(self, proc, year):
        '''
        Switch samples for unavailable sim08 generator efficiencies
        '''
        if  proc in ['bpk1_ee', 'bpk2_ee'] and year in ['2011', '2012', '2015', '2016']:
            new_year = '2017'
            log.warning(f'Gen efficiency using {year} -> {new_year} for {proc}')
            year = new_year 

        return proc, year
    #------------------------------------------
    def _get_geo_eff(self, proc, year):
        key        = f'{proc}_{year}'
        proc, year = self._switch_sample(proc, year)

        if key in self._d_geo_eff:
            return self._d_geo_eff[key]
            
        self._d_geo_eff[key] = geo_eff(proc, year)

        return self._d_geo_eff[key]
    #------------------------------------------
    def _get_efficiency(self, proc=None, trig=None, year=None, d_sel=None):
        sel_eff  = self._get_rec_eff(d_sel,  proc, trig, year)
        geo_acc  = self._get_geo_eff(f'{proc}_ee',       year)

        val, var = jac.propagate(lambda x : x[0] * x[1], [geo_acc[0], sel_eff[0]], [[geo_acc[1] ** 2, 0], [0, sel_eff[1] ** 2]]) 
        val      = float(val)
        err      = math.sqrt(var)

        if trig == 'GTIS':
            self._d_sel_tis[f'{proc}_{year}'] = val, err
        else:
            self._d_sel_tos[f'{proc}_{year}'] = val, err

        return val, err
    #------------------------------------------
    def _get_sel_yield(self, proc, trig, year, d_sel):
        cas_dir  = os.environ['CASDIR']
        root_wc  = f'{cas_dir}/tools/apply_selection/rare_backgrounds/{proc}/{self._dvers}/{year}_{trig}/*.root'
        rdf      = ROOT.RDataFrame(trig, root_wc)

        if d_sel is None:
            return rdf.Count().GetValue()

        for key, cut in d_sel.items():
            rdf = rdf.Filter(cut, key)

        rep=rdf.Report()
        rep.Print()

        return rdf.Count().GetValue()
    #------------------------------------------
    def _get_date_flag(self, date):
        l_date = re.findall('\d{2}\.\d{2}\.\d{2}', date)
        if len(l_date) == 0:
            return False

        dstr = datetime.strptime

        return any( dstr(self._min_date, '%d.%m.%y') < dstr(date, '%d.%m.%y') for date in l_date)
    #------------------------------------------
    def _switch_yields(self, proc, year):
        if   proc in ['bpk1', 'bpk2'] and year in ['2015', '2016']:
            new_year = '2017'
            log.warning(f'Reco yields using {year} -> {new_year} for {proc}')
            year = new_year
        elif proc == 'bpk2' and year == '2011':
            new_year = '2012'
            log.warning(f'Reco yields using {year} -> {new_year} for {proc}')
            year = new_year

        return proc, year
    #------------------------------------------
    def _get_year_entries(self, df, proc, year):
        proc, year = self._switch_yields(proc, year)

        df_y = df[df.Year == int(year)]
        if len(df_y) not in [1, 2]:
            log.error(f'Found more than two or fewer than one entries (polarities) after fully filtering')
            log.info(df)
            log.info('--->')
            log.info(df_y)
            raise

        l_pol=df_y.Polarity.tolist()
        s_pol=set(l_pol)
        if   len(df_y) == 2 and s_pol != {'MagUp', 'MagDown'}:
            log.error(f'Wrong polarities: {s_pol}')
            raise ValueError
        elif len(df_y) == 1:
            log.warning(f'Found only polarity: {s_pol}')

        return df_y.Events.sum()
    #------------------------------------------
    def _get_rec_yield(self, proc, year):
        ganga_dir = os.environ['GANDIR']
        json_path = f'{ganga_dir}/job_stats/{proc}.json'

        df = pnd.read_json(json_path)
        df = df.loc[[ self._get_date_flag(date) for date in df.Dates ]]

        yld= self._get_year_entries(df, proc, year)

        return yld 
    #------------------------------------------
    def _get_rec_eff(self, d_sel, proc, trig, year):
        sel = self._get_sel_yield(proc, trig, year, d_sel)
        rec = self._get_rec_yield(proc,       year)

        eff, eup, edn = utils.get_eff_err(sel, rec)

        err = (eup + edn) / 2.

        return eff, err
#------------------------------------------
class scales:
    def __init__(self, dset=None, trig=None, kind=None, vers=None, d_sel=None):
        self._dset = dset
        self._trig = trig 
        self._kind = kind 
        self._vers = vers
        self._d_sel= d_sel

        self._l_kind = ['bpks', 'bdks', 'bsph', 'bpk1', 'bpk2']
        self._l_trig = ['ETOS', 'GTIS']
        self._l_dset = ['2011', '2012', '2015', '2016', '2017', '2018']

        self._d_frbf = None
        self._d_eff  = None

        self._initialized = False
    #------------------------------------------
    def _check_arg(self, l_val, val, name):
        if val not in l_val:
            log.error(f'{name} {val} not allowed')
            raise ValueError
        else:
            log.debug(f'{name:<20}{"->":20}{val:<20}')
    #------------------------------------------
    def _initialize(self):
        if self._initialized:
            return

        log.debug('Initializing')

        if self._vers is None:
            log.error('Version not specified')
            raise

        log.debug(f'Using rare-signal scales version: {self._vers}')
        frbf_path    = files('extractor_data').joinpath(f'rare_sf/{self._vers}/fr_bf.json')
        self._d_frbf = utnr.load_json(frbf_path)

        self._d_eff  = self._get_efficiencies() 

        self._check_arg(self._l_kind, self._kind, 'Background')
        self._check_arg(self._l_dset, self._dset, 'Dataset')
        self._check_arg(self._l_trig, self._trig, 'Trigger')

        self._initialized = True
    #------------------------------------------
    def _get_efficiencies(self):
        log.debug('Getting efficiencies')

        eff_path     = files('extractor_data').joinpath(f'rare_sf/{self._vers}/eff_real.json'  )
        if not os.path.isfile(eff_path):
            log.debug('Not found efficiencies file, remaking it')
            calc   = eff_calc()
            d_eff  = calc.get_efficiencies(d_sel=self._d_sel)
            utnr.dump_json(d_eff, eff_path)
            log.debug(f'Efficiencies file saved to: {eff_path}')
        else:
            d_eff  = utnr.load_json(eff_path)
            log.debug('Found efficiencies file, not remaking it')

        return d_eff
    #------------------------------------------
    def _get_fr(self, kind):
        key= 'bpkp' if kind == 'sig' else self._kind
        fx = {'bpkp' : 'fu', 'bpks' : 'fu', 'bdks' : 'fd', 'bsph' : 'fs', 'bpk1' : 'fu', 'bpk2' : 'fu'}[key]
        fx = self._d_frbf['fr'][fx]

        return fx
    #------------------------------------------
    def _mult_brs(self, br_1, br_2):
        l_br_val = [br_1[0], br_2[0]]
        br_cov   = [[br_1[1] ** 2, 0], [0, br_2[1] ** 2]]
        val, var = jac.propagate(lambda x : x[0] * x[1], l_br_val, br_cov)

        return val, math.sqrt(var)
    #------------------------------------------
    def _get_br(self, kind):
        key= 'bpkp' if kind == 'sig' else self._kind

        if   key in ['bpkp', 'bpk1', 'bpk2']:
            br = self._d_frbf['bf'][key]
        elif key == 'bpks':
            br = self._mult_brs(self._d_frbf['bf'][key], self._d_frbf['bf']['k+kp'])
        elif key == 'bdks':
            br = self._mult_brs(self._d_frbf['bf'][key], self._d_frbf['bf']['kokp'])
        elif key == 'bsph':
            br = self._mult_brs(self._d_frbf['bf'][key], self._d_frbf['bf']['phkk'])
        else:
            log.error(f'Invalid key: {key}')
            raise

        return br
    #------------------------------------------
    def _get_ef(self, kind):
        key = 'bpkp' if kind == 'sig' else self._kind

        return self._d_eff[key][self._trig][self._dset]
    #------------------------------------------
    def _print_vars(self, l_tup):
        log.debug('-' * 20)
        log.debug(f'{"Var":<20}{"Value":<20}{"Error":<20}')
        log.debug('-' * 20)
        for (val, err), name in zip(l_tup, ['fr sig', 'br sig', 'eff sig', 'fr bkg', 'br bkg', 'eff bkg']):
            log.debug(f'{name:<20}{val:<20.3e}{err:<20.3e}')
        log.debug('-' * 20)
    #------------------------------------------
    def get_scale(self):
        self._initialize()

        fr_sig = self._get_fr('sig') 
        br_sig = self._get_br('sig') 
        ef_sig = self._get_ef('sig') 

        fr_bkg = self._get_fr('bkg') 
        br_bkg = self._get_br('bkg') 
        ef_bkg = self._get_ef('bkg') 

        l_tup = [fr_sig, br_sig, ef_sig, fr_bkg, br_bkg, ef_bkg]
        l_val = [ tup[0] for tup in l_tup]
        l_err = [ tup[1] for tup in l_tup]
        cov   = numpy.diag(l_err) ** 2

        self._print_vars(l_tup)

        val, var = jac.propagate(lambda x : (x[3] * x[4] * x[5]) / (x[0] * x[1] * x[2]), l_val, cov) 
        val = float(val)
        err = math.sqrt(var)

        return val, err 
#------------------------------------------

