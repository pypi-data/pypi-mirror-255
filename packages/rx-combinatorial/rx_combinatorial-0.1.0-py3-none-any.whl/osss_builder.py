import os
import zfit
import math
import glob
import tarfile
import shutil
import pprint
import utils_noroot as utnr

from log_store           import log_store
from importlib.resources import files
from zutils.pdf          import SUJohnson as zpdf_jh
from zutils.pdf          import modexp    as zpdf_me
from zutils.pdf          import hypexp    as zpdf_he

log=log_store.add_logger(name='cb_calculator:osss_builder')
#----------------------------------------------
class osss_builder:
    d_shared = dict()

    def __init__(self, dset=None, trigger=None, q2bin=None, vers=None, const=None):
        self._dset       = dset
        self._trigger    = trigger 
        self._q2bin      = q2bin
        self._vers       = vers
        self._mass_const = const

        self._const_pref = 'yconst' if const else 'nconst'
        self._d_par_full = {} 
        self._kind       = None
        self._scales_dir = None 
        self._cache_path = None

        self._intialized = False 
    #------------------------------
    @property
    def cache_path(self):
        return self._cache_path

    @cache_path.setter
    def cache_path(self, value):
        self._cache_path = value
    #------------------------------
    @property
    def kind(self):
        return self._kind

    @kind.setter
    def kind(self, value):
        '''
        Expected: cmb_etos:alt_001 for mtos or 002, 003 etc too
        '''
        if not value.startswith('cmb_'):
            return

        value = value.replace('cmb_', '')
        trigg = value.split(':')[0].upper()
        if trigg != self._trigger:
            return

        syst = value.split(':')[1]
        log.debug(f'Setting systematic: {syst}')

        self._kind = syst 
    #------------------------------
    def _initialize(self):
        if self._intialized:
            return

        if self._mass_const not in [True, False]:
            log.error(f'Invalid value for mass constraint flag: {self._mass_const}')
            raise

        self._check_none(self._dset   , 'dataset')
        self._check_none(self._trigger, 'trigger')
        self._check_none(self._vers   ,    'vers')

        self._load_pars()

        self._intialized = True
    #------------------------------
    def _check_none(self, var, name):
        if var is None:
            log.error(f'Variable {name} not specified')
            raise ValueError
    #------------------------------
    def _get_scales_dir(self):
        scales_dir = files('cb_data').joinpath(f'{self._vers}')
        if not os.path.isdir(scales_dir):
            log.error(f'Directory not found: {scales_dir}')
            raise

        return scales_dir
    #------------------------------
    def _load_pars(self):
        self._scales_dir = self._get_scales_dir()

        if not os.path.isdir(self._scales_dir):
            log.error(f'Directory with scales not found: {self._scales_dir}')
            raise FileNotFoundError

        scales_path = f'{self._scales_dir}/{self._q2bin}_{self._const_pref}_{self._trigger}_{self._dset}.json'
        try:
            log.info(f'Loading scales from: {scales_path}')
            d_par = utnr.load_json(scales_path)
        except:
            log.error(f'Cannot load scales from: {scales_path}')
            raise

        for key, tup in d_par.items():
            if key in ['ne_SS', 'ne_OS', 'd_ne', 'd_dne']:
                continue

            if   key.startswith('d_'):
                val, err, _ = tup 
                low, hig    = 0, 0
            else:
                low, hig, val, err = tup 

            self._d_par_full[key] = (low, hig, val, err)
    #------------------------------
    def _is_fixed_par(self, name):
        b1 = not name.endswith('_SS')
        b2 = not name.startswith('d_')

        return b1 and b2
    #------------------------------
    def _add_corrected_par(self, d_par, d_par_all, unc):
        log.debug(f'Applying corrections for unc: {unc}')

        log.debug(f'{"Param":<10}{"->":10}{"Value":>10}{"Correction":>15}')
        for name in d_par_all:
            if name.startswith('d_'):
                continue

            low , hig, val_sr, err_sr = d_par_all[name]
            if unc in [0, -1] or err_sr == 0:
                log.debug(f'{name:<10}{"->":10}{val_sr:>10.3e}{"0 ":>15}')
                d_par[name] = (low , hig, val_sr, err_sr)
                continue

            _   ,   _,   dval, err_cr = d_par_all[f'd_{name}' ]

            err = math.sqrt(err_cr ** 2 + err_sr ** 2)
            if   unc == None:
                val_sr = val_sr - dval
                log.debug(f'{name:<10}{"->":10}{val_sr:>10.3e}{dval:>15.3e}')
            elif isinstance(unc, dict):
                serr   = 0  if name not in unc else unc[name] * err
                val_sr = val_sr - dval + serr
                log.debug(f'{name:<10}{"->":10}{val_sr:>10.3e}{dval:>15.3e}{"+":10}{serr:>10.3e}')
            else:
                log.error(f'Invalid systematic: {unc}')
                raise

            d_par[name] = (low , hig, val_sr, err)

        return d_par
    #------------------------------
    def _pick_osss(self, name, unc):
        if   unc == -1 and '_OS' in name:
            return True 
        elif unc == -1 and '_SS' in name:
            return False
        elif unc != -1 and '_OS' in name:
            return False
        else:
            return True 
    #------------------------------
    def _update_unc(self, unc):
        d_par_osss = {name.replace('_SS', '').replace('_OS', '') : val for name, val in self._d_par_full.items() if self._pick_osss(name, unc)}

        d_par={}
        d_par={ name : val for name, val in d_par_osss.items() if self._is_fixed_par(name) }
        d_par=self._add_corrected_par(d_par, d_par_osss, unc)

        return d_par
    #------------------------------
    def _rename_pars(self, d_par):
        d_rename = {'dl' : 'delta', 'gm' : 'gamma', 'ap' : 'alpha', 'bt' : 'beta'}

        d_renamed = {}
        for name, par in d_par.items():
            if name not in d_rename:
                d_renamed[name] = par
                continue

            new_name = d_rename[name]
            d_renamed[new_name] = par

        return d_renamed
    #------------------------------
    def _build_pars(self, d_par_val, preffix):
        d_par = {}
        for name, (low, hig, val, err) in d_par_val.items():
            if err == 0:
                d_par[name] = zfit.param.ConstantParameter(f'{name}_{preffix}', val)
            else:
                d_par[name] = self._get_flt_par(name, preffix, val, low, hig)

        return d_par
    #------------------------------
    def _get_flt_par(self, name, preffix, val, low, hig):
        if name not in builder.d_shared:
            return zfit.param.Parameter(f'{name}_{preffix}', val, low, hig)

        par_name = builder.d_shared[name]
        if par_name not in zfit.Parameter._existing_params:
            return zfit.param.Parameter(par_name, val, low, hig)
        else:
            return zfit.Parameter._existing_params[par_name]
    #------------------------------
    def _build_cons(self, d_par_val, d_par_obj):
        d_con = {}
        for name, (low, hig, val, err) in d_par_val.items():
            if err == 0:
                continue

            par = d_par_obj[name]
            d_con[par.name] = val, err 

        return d_con
    #------------------------------
    def _fix_shape(self, pdf):
        for par in pdf.get_params():
            par.floating=False
    #------------------------------
    def get_pdf(self, obs=None, unc=None, preffix=None, name=None, fix_shape=False): 
        '''
        Parameters
        -------------------
        obs (zfit.Parameter): Observable used for the PDF

        unc (int|None|dict): 
          -1   : Use OS
           0   : Use SS
           None: Nominal corrections on top of SS,
           dict: {par : val} where par in ['mu', 'lm'] and val in [-1, 0, +1]

        preffix(str): Used to name parameters
        name (str): PDF name
        fix_shape (bool): Will fix the shape if true

        Returns 
        -------------------
        pdf, l_con (tuple): Zfit PDF and list of constraints on parameters
        '''
        self._initialize()

        d_par_val = self._update_unc(unc)
        d_par = self._build_pars(d_par_val, preffix)
        l_con = self._build_cons(d_par_val, d_par)

        d_par['obs'] = obs
        d_par['name']= name
        d_par = self._rename_pars(d_par)

        pdf = zpdf_jh(**d_par)
        if fix_shape:
            self._fix_shape(pdf)

        return pdf, l_con
#----------------------------------------------
