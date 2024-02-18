from rk_model  import rk_model as model
from log_store import log_store

import zutils.utils as zut
import pprint
import zfit
import re

log = log_store.add_logger('rk_extractor:model_manager')
#---------------------------------------------------------------------------
class manager:
    reparametrize=True
    #---------------------------------------------------------------------------
    def __init__(self, preffix=None, d_eff=None, d_nent=None, dset=None):
        self._preffix = preffix
        self._d_eff   = d_eff 
        self._d_nent  = d_nent
        self._dset    = dset

        self._cmb_pref  = 'ncb_ee'

        self._d_data     = None
        self._d_mode     = None
        self._a          = zfit.param.Parameter('a', -100,-1e5,   0)  
        self._b          = zfit.param.Parameter('b', 1000,   0, 1e5)
        self._l_bdt_bin  = [1, 2, 3, 4, 5]
        self._fake_model = False

        self._initialized = False
    #---------------------------------------------------------------------------
    def _initialize(self):
        if self._initialized:
            return

        self._set_instances()
        self._set_data_model()
        self._reparametrize_cmb_yield()
        self._print_model()
        self._print_data()

        self._initialized = True
    #---------------------------------------------------------------------------
    @property
    def bdt_bin(self):
        return self._l_bdt_bin

    @bdt_bin.setter
    def bdt_bin(self, value):
        self._l_bdt_bin = value
    #---------------------------------------------------------------------------
    @property
    def fake(self):
        return self._fake_model

    @fake.setter
    def fake(self, value):
        self._fake_model = value
    #---------------------------------------------------------------------------
    def _get_comb_yield_info(self, pdf):
        s_par = pdf.get_params(is_yield=True)
        [par] = [ par for par in s_par if par.name.startswith(self._cmb_pref) ]

        name  = par.name
        try:
            [sbin]= re.match('.*_(\d)$', name).groups()
        except:
            log.error(f'Cannot extract bin index from: {name}')
            raise

        ibin = int(sbin)

        return name, ibin
    #---------------------------------------------------------------------------
    def _reparametrize_cmb_yield(self):
        if not manager.reparametrize:
            log.warning(f'Not reparametrizing combinatorial yield')
            return

        d_mode = {}
        for x, (y, ee_mod) in self._d_mode.items(): 
            name, ibin = self._get_comb_yield_info(ee_mod)
            d_par      = self._get_yields({f'{name}_rep' : ibin})
            ee_mod     = self._reparametrize(ee_mod, d_par)
            d_mode[x]  = y, ee_mod

        self._d_mode = d_mode
    #------------------------------------
    def _get_yields(self, d_par_in):
        d_par_ot = {}
        for name, ibin in d_par_in.items():
            d_par_ot[name] = zfit.ComposedParameter(name, lambda a, b: ibin * a + b, params={'a' : self._a, 'b' : self._b })

        return d_par_ot 
    #------------------------------------
    def _reparametrize(self, pdf, d_par):
        l_pdf   = []
        pdf_name= pdf.name
        for pdf_com in pdf.pdfs:
            nev  = pdf_com.get_yield()
            name = f'{nev.name}_rep'
            if name in d_par:
                par     = d_par[name]
                pdf_com = pdf_com.copy()
                pdf_com.set_yield(par)
    
            l_pdf.append(pdf_com)

        return zfit.pdf.SumPDF(l_pdf, name=pdf_name)
    #---------------------------------------------------------------------------
    def _set_instances(self):
        self._d_inst = {}
        for bdt_bin in self._l_bdt_bin:
            mod          = model(preffix=f'{self._preffix}_{bdt_bin}', d_eff=self._d_eff, d_nent=self._d_nent, l_dset=[self._dset])
            mod.bdt_bin  = bdt_bin
            mod.fake     = self._fake_model 

            self._d_inst[bdt_bin] = mod
    #---------------------------------------------------------------------------
    def _get_data(self, bdt_bin):
        d_data = self._d_inst[bdt_bin].get_data()
        data   = d_data[self._dset]

        return data
    #---------------------------------------------------------------------------
    def _get_model(self, bdt_bin):
        d_mode = self._d_inst[bdt_bin].get_model()
        mode   = d_mode[self._dset]

        return mode 
    #---------------------------------------------------------------------------
    def _set_data_model(self):
        bdt_bin    = self._l_bdt_bin[-1]
        mm_data, _ = self._get_data(bdt_bin)
        mm_mode, _ = self._get_model(bdt_bin)

        d_data = {}
        d_mode = {}
        for bdt_bin in self._l_bdt_bin:
            log.debug(f'Processing BDT bin: {bdt_bin}')
            _, ee_data = self._get_data(bdt_bin)
            _, ee_mode = self._get_model(bdt_bin)

            d_data[f'bdt_{bdt_bin}'] = mm_data, ee_data
            d_mode[f'bdt_{bdt_bin}'] = mm_mode, ee_mode

        self._d_mode = d_mode
        self._d_data = d_data
    #---------------------------------------------------------------------------
    def _print_data(self):
        log.debug('-' * 40)
        log.debug(f'{"Name":<20}{"mm entries":<20}{"ee entries":<20}')
        log.debug('-' * 40)
        for name, (dat_mm, dat_ee) in self._d_data.items():
            nent_mm = dat_mm.numpy().flatten().size
            nent_ee = dat_ee.numpy().flatten().size
            log.debug(f'{name:<20}{nent_mm:<20}{nent_ee:<20}')
        log.debug('-' * 40)
    #---------------------------------------------------------------------------
    def _print_model(self):
        for _, (pdf_mm, pdf_ee) in self._d_mode.items():
            zut.print_pdf(pdf_mm, level='debug')
            zut.print_pdf(pdf_ee, level='debug')
    #---------------------------------------------------------------------------
    def get_data(self):
        self._initialize()

        return self._d_data
    #---------------------------------------------------------------------------
    def get_model(self):
        self._initialize()

        return self._d_mode
#---------------------------------------------------------------------------

