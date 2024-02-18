import pandas            as pnd
import matplotlib.pyplot as plt
import utils_noroot      as utnr

import numpy

from logzero import logger as log

#---------------------------
class evt_mixer:
    def __init__(self, shift_vars=None, period=1):
        self._l_svar = shift_vars
        self._period = period

        self._d_check= None
        self._out_dir= None 

        self._initialized=False
    #---------------------------
    def _initialize(self):
        if self._initialized:
            return

        self._initialized=True
    #---------------------------
    @property
    def out_dir(self):
        return self._out_dir

    @out_dir.setter
    def out_dir(self, value):
        self._out_dir = utnr.make_dir_path(value)
    #---------------------------
    @property
    def d_check(self):
        return self._d_check

    @d_check.setter
    def d_check(self, value):
        self._d_check = value 
    #---------------------------
    def _run_diagnostics(self, df):
        if (self._d_check is None) or (self._out_dir is None):
            return

        dia_dir = utnr.make_dir_path(f'{self._out_dir}/diagnostics')
        if 'bplus' in self._d_check:
            preffix= self._d_check['bplus']
            sr_org = df.B_M
            sr_cal = self._get_bmass(df)

            ax=None
            for sr, ls in zip([sr_org, sr_cal], ['-', '--']): 
                sr.plot.hist(ax=ax, bins=50, range=(4000, 6000), histtype='step', linestyle=ls)

            plot_path = f'{dia_dir}/B_mass_comp_{preffix}.png'
            log.info(f'Saving to: {plot_path}')
            plt.legend(['Original', 'Calculated'])
            plt.savefig(plot_path)
            plt.close('all')
    #---------------------------
    def _mix_df(self, df):
        for var in self._l_svar:
            df[var] = df[var].shift(periods=self._period)

        df=df.dropna()
        
        return df
    #---------------------------
    def _add_jpsi(self, df, name='Jpsi_M'):
        sr_pe = df.L1_PE + df.L2_PE
        sr_px = df.L1_PX + df.L2_PX
        sr_py = df.L1_PY + df.L2_PY
        sr_pz = df.L1_PZ + df.L2_PZ
    
        df[name] = numpy.sqrt(sr_pe ** 2 - sr_px ** 2 - sr_py ** 2 - sr_pz ** 2)
    
        df = df.dropna()
    
        return df
    #---------------------------
    def _add_bplus(self, df, name='B_M'):
        df[name]= self._get_bmass(df)
        df      = df.dropna()
        df      = df.loc[df[name] > 0]
    
        return df
    #---------------------------
    def _get_bmass(self, df):
        sr_pe = df.L1_PE + df.L2_PE + df.H_PE
        sr_px = df.L1_PX + df.L2_PX + df.H_PX
        sr_py = df.L1_PY + df.L2_PY + df.H_PY
        sr_pz = df.L1_PZ + df.L2_PZ + df.H_PZ
    
        sr_bm = numpy.sqrt(sr_pe ** 2 - sr_px ** 2 - sr_py ** 2 - sr_pz ** 2)

        return sr_bm
    #---------------------------
    def _compare_var(self, df, var_org, var_mix, rng=None):
        if self._out_dir is None:
            return

        plt_dir = utnr.make_dir_path(f'{self._out_dir}/plots')

        ax = None
        ax = df.plot.hist(column=var_org, bins=30, range=rng, histtype='step', linestyle='--', ax=ax)
        ax = df.plot.hist(column=var_mix, bins=30, range=rng, histtype='step', linestyle=':' , ax=ax)

        log.info(f'Saving to: {plt_dir}/{var_org}_{var_mix}.png')
        plt.savefig(f'{plt_dir}/{var_org}_{var_mix}.png')
        plt.close('all')
    #---------------------------
    def get_df(self, df=None, d_name=None):
        self._initialize()

        self._run_diagnostics(df)

        df = self._add_jpsi(df)
        df = self._add_bplus(df)
        df = self._mix_df(df)
        df = self._add_jpsi(df, name = d_name['jpsi'])
        df = self._add_bplus(df, name= d_name['bplus'])

        self._compare_var(df, 'Jpsi_M',  d_name['jpsi' ], rng=(2800, 3100))
        self._compare_var(df,    'B_M',  d_name['bplus'], rng=(5000, 6000))

        return df
#---------------------------

