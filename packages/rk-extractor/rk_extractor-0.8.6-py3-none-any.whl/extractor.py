import re
import ROOT
import zfit
import math
import numpy
import pprint
import pandas            as pnd
import utils_noroot      as utnr
import matplotlib.pyplot as plt

from logzero     import logger as log
from zutils.plot import plot   as zfp

#--------------------------------
class extractor:
    '''
    Class used to extract RK from data, model, constraints, etc
    '''
    def __init__(self, dset=None, drop_correlations=False):
        '''
        Parameters
        ------------------
        dset (list): What datasets should be used? e.g. [r1p2, 2018]
        drop_correlations (bool): Will diagonalize the covariance matrix used for constraints
        if set to True, default is False.
        '''
        self._l_dset      = dset 
        self._drop_corr   = drop_correlations

        self._preffix     = None 
        self._d_eff       = None
        self._cov         = None
        self._d_rjpsi     = None
        self._d_data      = None
        self._d_model     = None
        self._d_ck        = None 
        self._d_val       = None
        self._d_var       = None
        self._d_par       = None
        self._d_pref      = None
        self._l_fix       = None
        self._d_fix       = {'Name' : [], 'Value' : []} 
        self._l_dsname    = ['r1_TOS', 'r1_TIS', 'r2p1_TOS', 'r2p1_TIS', '2017_TOS', '2017_TIS', '2018_TOS', '2018_TIS']

        self._rk          = zfit.Parameter('rk', 1.0, 0.0, 2.0)

        self._plt_dir     = None

        self._is_combined = self._l_dset == ['all_TOS'] or self._l_dset == ['all_TOS', 'all_TIS']
        self._has_const   = False
        self._initialized = False
    #--------------------------------
    def _initialize(self):
        if self._initialized:
            return

        if self._l_dset is not None:
            self._l_dsname = self._l_dset

        self._check_inputs()
        self._d_ck = { dsname : zfit.Parameter(f'ck_{dsname}_{self._preffix}', 1.0, 0.0, 2.0) for dsname in self._l_dsname }

        self._d_par   = self._get_model_pars()
        self._d_pref  = { name : par.value().numpy() for name, par in self._d_par.items() }

        d_model = {}
        for ds, (mod_mm, mod_ee) in self._d_model.items():
            mod_mm = self._reparametrize_mm_pdf(ds, mod_mm, mod_ee)

            d_model[ds] = (mod_mm, mod_ee)

        self._d_model = d_model

        self._check_constraints()
        self._fix_pars()

        self._initialized = True
    #--------------------------------
    def _get_model_pars(self):
        d_par = {}
        for mod_mm, mod_ee in self._d_model.values():
            d_par_mm = { par.name : par for par in mod_mm.get_params() }
            d_par_ee = { par.name : par for par in mod_ee.get_params() }

            d_par.update(d_par_mm)
            d_par.update(d_par_ee)

        return d_par
    #--------------------------------
    def _fix_pars(self):
        if self._l_fix is None:
            log.info('Not fixing any parameters')
            return

        for fix_par in self._l_fix:
            l_par_name = []
            for par_name, par in self._d_par.items():
                if fix_par in par_name:
                    l_par_name.append(par_name)
                    self._add_fixed_par(par)

            if len(l_par_name) == 0:
                log.error(f'No parameters found to fix for: {fix_par}')
                l_par_name = list(self._d_par.keys())
                log.info(l_par_name)
                raise
    #--------------------------------
    def _check_constraints(self):
        '''
        Checks that every parameter constrained, exists in the model
        '''
        if not self._has_const:
            return

        for var_name in self._d_val.keys():
            if var_name not in self._d_par:
                log.error(f'Constraint for missing model variable: {var_name}')
                pprint.pprint(l_mod_var_name)
                raise
    #--------------------------------
    def _check_inputs(self):
        for ds, (eff_mm, eff_ee) in self._d_eff.items():
            self._check_eff(eff_mm)
            self._check_eff(eff_ee)

        for ds, (mod_mm, mod_ee) in self._d_model.items():
            self._check_model(mod_mm)
            self._check_model(mod_ee)

        for ds, (dat_mm, dat_ee) in self._d_data.items():
            self._check_data(dat_mm)
            self._check_data(dat_ee)

        self._check_keys(self._d_eff  , self._d_model)
        self._check_keys(self._d_model, self._d_data )
        self._check_keys(self._d_data , self._d_eff  )

        self._check_cov()
        self._check_rjpsi()
    #--------------------------------
    def _check_keys(self, d1, d2):
        if d1.keys() != d2.keys():
            log.error('Keys differ:')
            log.error(d1.keys())
            log.error(d2.keys())
            raise ValueError
    #--------------------------------
    def _check_cov(self):
        if self._cov is None:
            log.error(f'Covariance matrix not introduced')
            raise

        if not isinstance(self._cov, numpy.ndarray):
            log.error(f'Covariance matrix is not a numpy array')
            raise

        ndset = len(self._d_eff)

        if self._cov.shape != (ndset, ndset):
            log.error(f'Covariance matrix has wrong shape')
            log.error(f'Expected: {ndset} x {ndset}')
            log.error(f'Found: {self._cov.shape}')
            raise
    #--------------------------------
    def _check_rjpsi(self):
        if self._d_rjpsi is None:
            self._d_rjpsi = {dsname : 1 for dsname in self._l_dsname}
            log.warning('rjpsi not found, using 1 for all datasets')
    #--------------------------------
    def _reparametrize_mm_pdf(self, dsname, mod_mm, mod_ee):
        nsg_mm  = self._get_yld(mod_mm, 'nsg_mm')
        nsg_ee  = self._get_yld(mod_ee, 'nsg_ee')

        l_model = mod_mm.models
        s_param = mod_mm.get_params(is_yield=True)
        l_param = list(s_param)
        index   = l_param.index(nsg_mm)

        eff_mm, eff_ee = self._d_eff[dsname]

        try:
            rjpsi = self._d_rjpsi[dsname]
        except:
            log.error(f'Cannot extract rjpsi for {dsname} only found:')
            log.info(self._d_rjpsi.keys())
            raise

        ck=self._d_ck[dsname]
        ck.set_value( (eff_ee / eff_mm) / rjpsi )

        nsg_mm = zfit.ComposedParameter(f'nsg_mm_rk_{dsname}', lambda a, b, c: a * b / c, params=[self._rk, nsg_ee, ck])

        log.debug(f'nsg_mm_rk_{dsname} -> {nsg_ee.name} * {self._rk.name} / {ck.name}')

        l_param[index] = nsg_mm

        l_model_ext  = [ model.copy().create_extended(nevt, name=model.name) for model, nevt in zip(l_model, l_param) ]

        mod_mm = zfit.pdf.SumPDF(l_model_ext)

        return mod_mm
    #--------------------------------
    def _add_fixed_par(self, par):
        par.floating          = False
        self._d_fix['Name']  += [par.name]
        self._d_fix['Value'] += [float(par.numpy())]

        log.warning(f'{par.name:<20}{"=":20}{par.value():<20.3e}')
    #--------------------------------
    def _get_yld(self, model, preffix):
        l_param   = model.get_params(is_yield=True)

        l_sig_yld = [ param for param in l_param if param.name.startswith(preffix)]
        [sig_yld] = l_sig_yld

        return sig_yld
    #--------------------------------
    @property
    def plt_dir(self):
        return self._plt_dir 

    @plt_dir.setter
    def plt_dir(self, value):
        try:
            self._plt_dir = utnr.make_dir_path(value)
        except:
            log.error(f'Cannot create: {value}')
            raise
    #--------------------------------
    @property
    def fix(self):
        return self._l_fix

    @fix.setter
    def fix(self, value):
        self._l_fix = value
    #--------------------------------
    @property
    def rjpsi(self):
        return self._d_rjpsi

    @rjpsi.setter
    def rjpsi(self, value):
        self._d_rjpsi = self._filter_values(value)
    #--------------------------------
    def _filter_cov(self, mat):
        if   self._l_dset is None:
            log.info(f'Using all datasets, not filtering covariance')
            return mat
        elif self._is_combined:
            log.info(f'Using combined dataset, not filtering covariance')
            return mat

        log.info(f'Filtering covariance for: {self._l_dset}')
        if set(self._l_dsname) == set(self._l_dset):
            return mat

        l_dset_drop  = [ dset_drop for dset_drop in self._l_dsname if dset_drop not in self._l_dset ]
        l_index_drop = [ self._l_dsname.index(dset_drop) for dset_drop in l_dset_drop ]

        mat=numpy.delete(mat, obj=l_index_drop, axis=0)
        mat=numpy.delete(mat, obj=l_index_drop, axis=1)

        return mat
    #--------------------------------
    def _filter_const(self, value):
        if self._l_dset is None:
            return value

        d_data = {}
        for key, val in value.items():
            keep=False
            for dset in self._l_dset:
                if dset in key:
                    keep=True
                    break

            if keep:
                d_data[key] = val

        return d_data
    #--------------------------------
    def _filter_values(self, value):
        if self._l_dset is None:
            return value

        d_data = {}
        for key, val in value.items():
            if key not in self._l_dset:
                continue

            d_data[key] = val

        return d_data
    #--------------------------------
    @property
    def eff(self):
        return self._d_eff

    @eff.setter
    def eff(self, value):
        self._d_eff = self._filter_values(value)
    #--------------------------------
    @property
    def cov(self):
        return self._cov

    @cov.setter
    def cov(self, value):
        if value is None:
            return
        self._cov = self._filter_cov(value)
    #--------------------------------
    @property
    def data(self):
        return self._d_data

    @data.setter
    def data(self, value):
        self._d_data = self._filter_values(value)
    #--------------------------------
    @property
    def model(self):
        return self._d_model

    @model.setter
    def model(self, value):
        self._d_model = self._filter_values(value)
    #--------------------------------
    @property
    def const(self):
        return self._d_val, self._d_var

    @const.setter
    def const(self, value):
        '''
        It will take the constraints on extra parameters. 
        All the variances that are None (in second dictionary of tuple) correspond to fixed parameters

        Parameters:
        --------------------
        tuple : Storing two dictionaries {par_name : par_value}, {par_name : par_variance}
        '''
        self._d_val = self._filter_const(value[0])
        self._d_var = self._filter_const(value[1])

        if self._d_val.keys() != self._d_var.keys():
            log.error(f'Keys of values and variances differ')
            raise ValueError

        self._has_const = True
    #--------------------------------
    def _check_data(self, obj):
        if not isinstance(obj, zfit.data.Data):
            log.error(f'Object introduced is not a zfit dataset')
            raise ValueError
    #--------------------------------
    def _check_model(self, obj):
        if not isinstance(obj, zfit.pdf.SumPDF):
            log.error(f'Object introduced is not a zfit PDF')
            raise ValueError

        pdf = obj
        if not pdf.is_extended:
            log.error(f'PDF is not extended:')
            print(pdf)
            raise ValueError

        l_yld = pdf.get_params(is_yield=True)
        l_yld_name = [ yld.name for yld in l_yld if yld.name.startswith('nsg_') ]

        try:
            [yld_name] = l_yld_name
        except:
            log.error('Not found one and only one signal yield:')
            print(l_yld_name)
            raise ValueError

        self._check_preffix(yld_name)

        log.debug(f'Picking up component with signal yield: {yld_name}')
    #--------------------------------
    def _check_preffix(self, yld_name):
        regex= r'n[a-z]+_(ee|mm)_[a-z0-9]+_(TOS|TIS)_(.*)'
        mtch = re.match(regex, yld_name)
        if not mtch:
            log.error(f'Cannot match yield name: {yld_name} with {regex}')
            raise

        if   self._preffix is None:
            self._preffix = mtch.group(3)
        elif self._preffix != mtch.group(3):
            log.error(f'Found different prefixes: {self._preffix} -> {mtch.group(3)}')
            raise
    #--------------------------------
    def _check_eff(self, eff):
        if not isinstance(eff, float):
            log.error(f'Efficiency is not a float: {eff}')
            raise ValueError

        if not ( 0 < eff < 1 ):
            log.error(f'Efficiency is not in (0, 1): {eff:.3f}')
            raise ValueError
    #--------------------------------
    def _get_nsig(self, model):
        s_par_flt = model.get_params(floating=True)
        s_par_fix = model.get_params(floating=False)
        s_par     = s_par_flt.union(s_par_fix)

        d_par = { par.name : par.value().numpy() for par in s_par if par.name == 'rk' or par.name.startswith('ck_') or par.name.startswith('nsg_ee_')}
        if len(d_par) == 1:
            [(nam, val)] = d_par.items()
            return val, nam
        elif len(d_par) != 3:
            log.error('Cannot find right parameters in model:')
            pprint.pprint(d_par)
            raise

        rk   = d_par['rk']
        [ck] = [ val for nam, val in d_par.items() if nam.startswith('ck_'    ) ]
        [ne] = [ val for nam, val in d_par.items() if nam.startswith('nsg_ee_') ]
        val  = ne * rk / ck

        [nam] = [ par.name for par in s_par if par.name.startswith('nsg_ee_') ]
        nam   = nam.replace('_ee_', '_mm_').replace('_TIS_', '_TOS_')

        return val, nam
    #--------------------------------
    def _get_stats(self, model, data, is_muon):
        arr_dat      = data.numpy().flatten()
        pst_fit, nam = self._get_nsig(model)
        pre_fit      = self._d_pref[nam]
        gen_val      = float(arr_dat.size)

        v1 = f'True: {pre_fit:.0f}'
        v2 = f'Genr: {gen_val:.0f}'
        v3 = f'Post: {pst_fit:.0f}'

        stats_str = f'{v1}\n{v2}\n{v3}' if  is_muon else  f'{v1}\n{v3}'

        return stats_str
    #--------------------------------
    def _get_legend(self):
        d_leg         = {}
        d_leg['prc']  = r'$\psi(2S) + c\bar{c}$'
        d_leg['bpks'] = r'$B^+\to K^{*+}e^+e^-$'
        d_leg['bdks'] = r'$B^0\to K^{*0}e^+e^-$'
        d_leg['bsph'] = r'$B_s\to \phi e^+e^-$'
        d_leg['bpk1'] = r'$B^+\to K_{1}e^+e^-$'
        d_leg['bpk2'] = r'$B^+\to K_{2}e^+e^-$'

        return d_leg
    #--------------------------------
    def _plot(self, data, model, results, component, stacked=None):
        if self._plt_dir is None:
            return

        stats = self._get_stats(model, data, is_muon = component.startswith('mm_') )

        obj=zfp(data=data, model=model, result=results)
        obj.plot(nbins=60, d_leg = self._get_legend(), stacked=stacked, ext_text=stats) 
        if   'ee'in component and 'TOS' in component:
            obj.axs[0].set_ylim(0, 120)
        elif 'mm'in component and 'TOS' in component:
            obj.axs[0].set_ylim(0, 250)
        elif 'ee'in component and 'TIS' in component:
            obj.axs[0].set_ylim(0,  70)

        obj.axs[0].grid()
        obj.axs[1].set_ylim(-5, 5)
        obj.axs[1].axhline(0, color='r')

        plt_path = f'{self._plt_dir}/fit_{component}.png'
        log.info(f'Saving to: {plt_path}')
        plt.savefig(plt_path, bbox_inches='tight')
    #--------------------------------
    def _finalize(self):
        self._delete_par('rk')

        for ck in self._d_ck.values():
            self._delete_par(ck.name)

        for dsname in self._l_dsname:
            self._delete_par(f'nsg_ee_rk_{dsname}')

        df_fix=pnd.DataFrame(self._d_fix)
        df_fix.to_json(f'{self._plt_dir}/fixed_pars.json', indent=4)
    #--------------------------------
    def _delete_par(self, par_name):
        if par_name in zfit.Parameter._existing_params:
            del zfit.Parameter._existing_params[par_name]
    #--------------------------------
    def _randomize(self, l_ck_val, cov):
        l_ck_val_rdm = numpy.random.multivariate_normal(l_ck_val, cov, 1)[0]

        log.warning(f'Randomizing Gaussian mean: {l_ck_val} -> {l_ck_val_rdm}')

        return l_ck_val_rdm.tolist()
    #--------------------------------
    def _randomize_ck(self):
        if self._l_fix is not None and 'ck' in self._l_fix:
            log.info(f'CK was already fixed, not randomizing and fixing it')
            return

        l_ck_par=[]
        l_ck_val=[]
        for dsname in self._l_dsname:
            eff_mm, eff_ee = self._d_eff[dsname]
            rjpsi          = self._d_rjpsi[dsname]

            ck_val         = (eff_ee / eff_mm) / rjpsi
            ck_par         = self._d_ck[dsname]

            l_ck_val.append(ck_val)
            l_ck_par.append(ck_par)

        l_ck_val = self._randomize(l_ck_val, self._cov)

        self._print_const(l_ck_par, l_ck_val, self._cov)

        log.info('Fixing CK')
        for par, val in zip(l_ck_par, l_ck_val):
            par.set_value(val)
            par.floating = False
    #--------------------------------
    def _get_ex_const(self):
        if not self._has_const:
            log.info('No extra constraints found')
            return 

        log.info('Getting extra constraints')
        l_par    = [ self._d_par[parname] for parname in self._d_val.keys() ]
        l_val    = [ self._d_val[parname] for parname in self._d_val.keys() ]
        l_var    = [ self._d_var[parname] for parname in self._d_val.keys() ]
        cov      = numpy.diag(l_var)
        l_val    = self._randomize(l_val, cov)

        return l_par, l_val, cov 
    #--------------------------------
    def _print_const(self, l_par, l_val, cov):
        eq_size = len(l_par) == len(l_val) == len(cov)
        if not eq_size:
            log.error(f'Invalid sizes for constraints')
            print(l_par)
            print(l_val)
            print(cov)
            raise

        nconst = len(l_par)
        log.debug('-' * 30)
        log.debug(f'{"Parameter":<20}{"Value":>15}{"Error":>15}')
        log.debug('-' * 30)
        for i_const in range(nconst):
            par_name = l_par[i_const].name
            par_val  = l_val[i_const]
            par_err  = math.sqrt(cov[i_const][i_const])

            log.debug(f'{par_name:<20}{par_val:>15.3e}{par_err:>15.3e}')
        log.debug('-' * 30)
    #--------------------------------
    def _plot_fit(self):
        if self._plt_dir is None:
            return

        for dsname in self._l_dsname:
            mod_mm, mod_ee = self._d_model[dsname]
            dat_mm, dat_ee = self._d_data [dsname]

            self._plot(dat_mm, mod_mm, None, f'mm_{dsname}_stk', stacked=True)
            self._plot(dat_ee, mod_ee, None, f'ee_{dsname}_stk', stacked=True)

            self._plot(dat_mm, mod_mm, None, f'mm_{dsname}_ovr', stacked=False)
            self._plot(dat_ee, mod_ee, None, f'ee_{dsname}_ovr', stacked=False)
    #--------------------------------
    def _combine_matrices(self, mat_1, mat_2):
        rows = mat_1.shape[0] + mat_2.shape[0]
        cols = mat_1.shape[1] + mat_2.shape[1]
        
        mat_3 = numpy.zeros((rows, cols))
        
        mat_3[:mat_1.shape[0], :mat_1.shape[1]] = mat_1
        mat_3[mat_1.shape[0]:, mat_1.shape[1]:] = mat_2

        return mat_3
    #--------------------------------
    def _merge_constraints(self, ex_cns, ck_cns):
        if   ex_cns is None: 
            l_par = ck_cns[0]
            l_val = ck_cns[1]
            cov   = ck_cns[2]
        elif ck_cns is None:
            l_par = ex_cns[0]
            l_val = ex_cns[1]
            cov   = ex_cns[2]
        else:
            l_par = ex_cns[0] + ck_cns[0]
            l_val = ex_cns[1] + ck_cns[1]
            cov   = self._combine_matrices(ex_cns[2], ck_cns[2])

        if self._drop_corr:
            log.warning('Using covariance matrix with correlations removed')
            cov_no_diag=numpy.matrix.copy(cov)
            numpy.fill_diagonal(cov_no_diag, 0)
            cov = cov - cov_no_diag

        return l_par, l_val, cov
    #--------------------------------
    def _build_const(self):
        ex_cns            = self._get_ex_const()
        if ex_cns is None: 
            return

        l_par, l_val, cov = ex_cns
        cns   = zfit.constraint.GaussianConstraint(params     = l_par,
                                                   observation= l_val,
                                                   uncertainty= cov)

        self._dump_constraints(l_par, l_val, cov)

        return cns
    #--------------------------------
    def _dump_constraints(self, l_par, l_val, cov):
        npar   = len(l_par)
        l_name = [par.name           for par   in l_par]
        l_cov  = [ cov[i_par][i_par] for i_par in range(npar)] 
        l_err  = [ math.sqrt(cov)    for cov   in l_cov ]
        df     = pnd.DataFrame({'Name' : l_name, 'Value' : l_val, 'Error' : l_err})

        df.to_json(f'{self._plt_dir}/constraints.json', indent=4)
    #--------------------------------
    @utnr.timeit
    def get_fit_result(self):
        self._initialize()

        log.info('Creating likelihoods')
        nll = None 
        for dsname in self._l_dsname:
            mod_mm, mod_ee = self._d_model[dsname]
            dat_mm, dat_ee = self._d_data [dsname]

            nll_mm = zfit.loss.ExtendedUnbinnedNLL(model=mod_mm, data=dat_mm)
            nll_ee = zfit.loss.ExtendedUnbinnedNLL(model=mod_ee, data=dat_ee)

            if nll is None:
                nll = nll_mm + nll_ee
            else:
                nll+= nll_mm + nll_ee

        self._randomize_ck()
        cns = self._build_const()
        if cns is not None:
            nll = nll.create_new(constraints=cns)

        mnm = zfit.minimize.Minuit()
        log.info('Running minimization')
        res = mnm.minimize(nll)

        #self._plot_fit()

        log.info('Finalizing')
        self._finalize()

        return res 
#--------------------------------

