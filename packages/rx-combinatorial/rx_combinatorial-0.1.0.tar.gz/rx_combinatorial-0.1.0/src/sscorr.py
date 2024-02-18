import os
import glob
import ROOT
import tqdm
import numpy
import pprint
import pandas as pnd

from logzero            import logger as log
from stats.correlations import corr

#----------------------------------
class sscorr:
    '''
    Class used to analyze correlations between variables in SS sample
    '''
    #----------------------------------
    def __init__(self, version=None, q2bin=None, trigger=None, dset=None):
        self._ver = version
        self._q2b = q2bin
        self._trg = trigger
        self._dst = dset

        self._d_cut   = None
        self._plt_dir = None
        self._l_var   = None

        self._initialized = False
    #----------------------------------
    @property
    def cuts(self):
        return self._d_cut

    @cuts.setter
    def cuts(self, value):
        self._d_cut = value
    #----------------------------------
    @property
    def plt_dir(self):
        return self._plt_dir

    @plt_dir.setter
    def plt_dir(self, value):
        try:
            os.makedirs(value, exist_ok=True)
        except:
            log.error(f'Cannot make: {value}')
            raise

        self._plt_dir = value
    #----------------------------------
    def _initialize(self):
        if self._initialized:
            return

        if not isinstance(self._d_cut, dict):
            log.error('Dictionary of cuts is not a dictionary')
            raise

        if len(self._d_cut) != 2:
            log.error('Wrong size for dictionary of cuts, expect 2:')
            pprint.pprint(self._d_cut)
            raise

        self._l_var = [ key for key in self._d_cut ]

        self._initialized = True
    #----------------------------------
    def _load_data(self, kind=None):
        chan    = 'mm'  if self._trg == 'MTOS' else 'ee'
        trig    = 'TIS' if self._trg == 'GTIS' else 'TOS'
        samp    = 'cmb' if kind      == 'SS'   else 'data'

        json_path = f'./{samp}_{chan}_{trig}.json'
        if os.path.isfile(json_path):
            log.info(f'Reading cached data from: {json_path}')
            df = pnd.read_json(json_path)
            return df

        cas_dir = os.environ['CASDIR']
        jsn_wc  = f'{cas_dir}/cb_calculator/{self._ver}/cmb_{chan}_{self._dst}_{trig}/data*.json'

        l_jsn   = glob.glob(jsn_wc)
        if len(l_jsn) == 0:
            log.error(f'Found no JSON faile in {jsn_wc}')
            raise
        else:
            log.info(f'Taking data from: {jsn_wc}')

        l_df = [ pnd.read_json(json_file_path) for json_file_path in tqdm.tqdm(l_jsn, ascii=' -') ]
        df   = pnd.concat(l_df)
        df   = df.reset_index(drop=True)
        df   = df[self._l_var]
        df   = df.dropna()

        df.to_json(json_path, indent=4)
        log.info(f'Caching to: {json_path}')

        return df
    #----------------------------------
    def plot_ss(self):
        self._initialize()

        if self._plt_dir is None:
            log.error(f'No plotting directory specified')
            raise

        df     = self._load_data()
        d_data = df.to_dict(orient='list')
        d_dat  = {key : numpy.array(val) for key, val in d_data.items()}
        rdf    = ROOT.RDF.FromNumpy(d_dat)

        obj = corr(['BDT_prc'], ['BDT_cmb'], rdf)
        obj.save(self._plt_dir)
    #----------------------------------
    def plot_os(self):
        return
#----------------------------------

