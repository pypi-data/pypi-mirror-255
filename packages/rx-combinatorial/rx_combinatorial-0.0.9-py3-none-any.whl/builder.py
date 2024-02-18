import zfit
import pprint
import utils_noroot as utnr

from log_store           import log_store
from importlib.resources import files
from zutils.pdf          import SUJohnson as zpdf_jh
from zutils.pdf          import modexp    as zpdf_me
from zutils.pdf          import hypexp    as zpdf_he

log=log_store.add_logger(name='cb_calculator:builder')
#----------------------------------------------
class builder:
    def __init__(self, dset=None, trigger=None, version=None):
        self._dset       = dset
        self._trigger    = trigger 
        self._version    = version
        self._kind       = 'nominal' 

        self._intialized = False 
    #------------------------------
    @property
    def kind(self):
        return self._kind

    @kind.setter
    def kind(self, value):
        '''
        Expected: cmb_etos:alt_001 for mtos or 002, 003 etc too
        '''
        if value is None:
            log.error(f'Passed a None as combinatorial kind')
            raise

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

        if self._kind is None:
            log.debug('Using nominal model')

        self._check_none(self._dset   , 'dataset')
        self._check_none(self._trigger, 'trigger')
        self._check_none(self._version, 'version')

        self._intialized = True
    #------------------------------
    def _check_none(self, var, name):
        if var is None:
            log.error(f'Variable {name} not specified')
            raise ValueError
    #------------------------------
    def _build_par(self, name, l_val):
        min_x, max_x, val_x, err_x = l_val
        if min_x == max_x:
            log.debug(f'Making {name} parameter constant')
            par = zfit.param.ConstantParameter(name, val_x)
        else:
            par = zfit.param.Parameter(name, val_x, min_x, max_x)

        return par
    #------------------------------
    def _get_pdf(self, d_cls_par, preffix):
        if   self._kind == 'nominal':
            log.debug(f'Using SUJohnson PDF for {self._kind} kind')
            pars_path = files('cb_pars').joinpath(f'{self._version}/sujohnson.json')
            cls       = zpdf_jh
        elif self._kind == 'alt_001':
            log.debug(f'Using HyperExponential PDF for {self._kind} kind')
            pars_path = files('cb_pars').joinpath(f'{self._version}/hypexp.json')
            cls       = zpdf_he
        else:
            log.error(f'Invalid PDF kind: {self._kind}')
            raise ValueError

        d_par     = utnr.load_json(pars_path)
        d_pdf_par = {name : self._build_par(f'{name}_{preffix}', l_val) for name, l_val in d_par.items()}
        d_cls_par.update(d_pdf_par)

        pdf   = cls(**d_cls_par)

        return pdf 
    #------------------------------
    def get_pdf(self, obs=None, preffix=None, name=None, fix_shape=None):
        '''
        Parameters
        -------------------
        obs (zfit.Parameter): Observable used for the PDF
        preffix(str): Used to name parameters
        name (str): PDF name
        fix_shape (bool): Will fix the shape if true

        Returns 
        -------------------
        pdf: Zfit PDF
        '''
        self._initialize()

        d_par         = {}
        d_par['obs' ] = obs
        d_par['name'] = name

        pdf = self._get_pdf(d_par, preffix)

        return pdf
#----------------------------------------------

