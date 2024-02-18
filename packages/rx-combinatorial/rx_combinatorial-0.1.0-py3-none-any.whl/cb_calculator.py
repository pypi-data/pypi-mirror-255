from rk.efficiency import efficiency
from rk.cutflow    import cutflow
from importlib.resources import files

from logzero       import logger     as log
from zutils.plot   import plot       as zfp
from atr_mgr       import mgr        as amgr
from fitter        import zfitter
from evt_mixer     import evt_mixer

from stats.average import average    as sta_avg
from zutils.utils  import pad_data   as zut_pad
from zutils.utils  import fix_pars   as zut_fix
from zutils.utils  import float_pars as zut_flt

from zutils.pdf    import SUJohnson  as zpdf_jh
from zutils.pdf    import modexp     as zpdf_me
from zutils.pdf    import hypexp     as zpdf_he

import os
import re 
import glob
import zfit
import numpy
import pprint
import mplhep

import pandas            as pnd
import matplotlib.pyplot as plt
import read_selection    as rs
import utils_noroot      as utnr

#----------------------------------------
class calculator:
    def __init__(self, dset=None, trig=None, vers=None, q2bin=None, mass_const=False):
        self._dset        = dset
        self._trig        = trig
        self._vers        = vers
        self._q2bin       = q2bin
        self._mass_const  = mass_const

        self._fit_tries   = 5 
        self._const_pref  = None
        self._cache_dir   = None
        self._scale_dir   = None
        self._bdt_cut_sgn = None
        self._bdt_cut_inv = None
        self._bdt_cmb_wp  = None
        self._qsq_cut     = None
        self._pdf         = None
        self._low_m       = None 
        self._high_m      = None 
        self._obs         = None

        self._evt_mix     = False
        self._d_data      = {}
        self._nbins       = 50
        self._q2bin       = q2bin 
        self._l_bdt_quant = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        self._nquantile   = len(self._l_bdt_quant) - 1
        self._d_par_name  = None 

        self._highest_q2  = '(Jpsi_M * Jpsi_M < 22000000.0)'

        self._dl_hi       = 2.5 
        self._gm_hi       = -10

        self._lm_jp       = 40
        self._gm_jp       = -6

        self._lm_ps       = 40
        self._gm_ps       = -6

        self._jpsi_dn     = 0
        self._jpsi_up     = 5000 

        self._df_ss       = None
        self._df_os       = None

        self._d_qnt       = None
        self._arr_qnt     = None

        self._pars_dir    = None 
        self._plot_dir    = None 
        self._channel     = None

        self._low_blind   = 5100
        self._high_blind  = 5400
        self._d_range     = None 
        self._d_sample    = {'SS' : 'cmb', 'OS' : 'data'}
        self._new_bdt_cut = '0.977'

        self._initialized = False
    #----------------------------------------
    @property
    def cache_dir(self):
        return self._cache_dir

    @cache_dir.setter
    def cache_dir(self, value):
        try:
            os.makedirs(value, exist_ok=True)
        except:
            log.error(f'Cannot make cache directory: {value}')
            raise

        self._cache_dir = value
    #----------------------------------------
    @property
    def fit_tries(self):
        return self._fit_tries

    @fit_tries.setter
    def fit_tries(self, value):
        self._fit_tries = value
    #----------------------------------------
    @property
    def evt_mix(self):
        return self._evt_mix

    @evt_mix.setter
    def evt_mix(self, value):
        if value not in [True, False]:
            log.error(f'Invalid evt_mix flag: {value}')
            raise

        self._evt_mix = value
    #----------------------------------------
    def _initialize(self):
        plt.style.use(mplhep.style.LHCb2)
        if self._initialized:
            return

        self._set_names()
        self._cache_dir = self._get_cache_dir() 
        self._scale_dir = self._get_scale_dir()
        self._const_pref= 'yconst' if self._mass_const else 'nconst'

        self._set_mass_range()
        self._set_cuts()
        self._set_bdt_wp()
        self._channel = self._get_channel()
        self._make_dirs()

        zfit.settings.changed_warnings.hesse_name = False

        self._d_range = self._get_ranges()

        df_os                      = self._get_data(sample='OS')
        df_ss                      = self._get_data(sample='SS')
        self._d_qnt, self._arr_qnt = self._get_quantiles(df_ss)

        self._initialized = True
    #----------------------------------------
    def _set_names(self):
        self._d_par_name = {}
        #-----------------
        self._d_par_name['ne' ]  = 'Yield'
        self._d_par_name['dne']  = 'Yield/Width'
        self._d_par_name['d_ne'] = 'Yield (SS - OS)'
        self._d_par_name['d_dne']= 'Yield/Width (SS - OS)'
        #-----------------
        self._d_par_name['ap']   = r'\alpha'
        self._d_par_name['bt']   = r'$\beta$'
        self._d_par_name['d_ap'] = r'$\alpha_{SS} - \alpha_{OS}$'
        self._d_par_name['d_bt'] = r'$\beta_{SS} - \beta_{OS}$'
        #-----------------
        self._d_par_name['mu' ]  = '$\mu$'
        self._d_par_name['lm' ]  = '$\lambda$'
        self._d_par_name['dl' ]  = '$\delta$'
        self._d_par_name['gm' ]  = '$\gamma$'

        self._d_par_name['d_mu'] = '$\mu_{SS} - \mu_{OS}$'
        self._d_par_name['d_lm'] = '$\lambda_{SS} - \lambda_{OS}$'
        self._d_par_name['d_dl'] = '$\delta_{SS} - \delta_{OS}$'
        self._d_par_name['d_gm'] = '$\gamma_{SS} - \gamma_{OS}$'
    #----------------------------------------
    def _get_cache_dir(self):
        if self._cache_dir is not None:
            return self._cache_dir

        cache_dir = f'{os.environ["CASDIR"]}/cb_calculator/{self._vers}'

        if not os.path.isdir(cache_dir):
            log.error(f'Cannot find {cache_dir}')
            raise

        return cache_dir
    #----------------------------------------
    def _get_scale_dir(self):
        scale_dir = files('cb_data').joinpath(self._vers)

        return scale_dir
    #----------------------------------------
    def _update_signal_bdt_cut(self, cut):
        regex= r'BDT_cmb > ([0-9\.]+) and BDT_prc > [0-9\.]+'
        mtch = re.match(regex, cut)
        if not mtch:
            log.error(f'Cannot match {cut} with {regex}')
            raise

        old_cut = mtch.group(1)

        cut     = cut.replace(old_cut, self._new_bdt_cut)
        log.warning(f'Replacing {old_cut} -> {self._new_bdt_cut}: {cut}')

        return cut
    #----------------------------------------
    def _set_cuts(self):
        qsq_cut           = rs.get('q2' , self._trig, q2bin=self._q2bin, year = 'none')
        qsq_cut           = qsq_cut.replace('&&', 'and')
        self._qsq_cut     = qsq_cut

        bdt_cut           = rs.get('bdt', self._trig, q2bin=self._q2bin, year = 'none')
        bdt_cut_sgn       = bdt_cut.replace('&&', 'and')
        self._bdt_cut_sgn = self._update_signal_bdt_cut(bdt_cut_sgn)
        self._bdt_cut_inv = self._bdt_cut_sgn.replace('BDT_cmb >', 'BDT_cmb <')
    #----------------------------------------
    def _set_bdt_wp(self):
        rgx='BDT_cmb > ([\d,\.]+).*'
        mtch = re.match(rgx, self._bdt_cut_sgn)
        if not mtch:
            log.error('Cannot extract combinatorial WP from: {self._bdt_cut_sgn}')
            raise

        wp_str = mtch.group(1)
        self._bdt_cmb_wp = float(wp_str)
    #----------------------------------------
    def _set_mass_range(self):
        if   self._q2bin == 'jpsi':
            self._low_m  = 3500
            self._high_m = 6500 
        elif self._q2bin == 'psi2':
            self._low_m  = 3500
            self._high_m = 6500 
        elif self._q2bin == 'high':
            self._low_m  = 4480
            self._high_m = 6500 
        else:
            log.error(f'Invalid q2 bin: {self._q2bin}')
            raise

        self._obs = zfit.Space('mass', limits=(self._low_m, self._high_m))
    #----------------------------------------
    def _get_channel(self):
        if  self._trig in ['ETOS', 'GTIS']:
            channel = 'ee'
        elif self._trig == 'MTOS':
            channel = 'mm'
        else:
            log.error(f'Invalid trigger: {self._trig}')
            raise ValueError

        return channel
    #----------------------------------------
    def _make_dirs(self):
        self._pars_dir  = f'{self._cache_dir}/pars_{self._dset}_{self._trig}/{self._q2bin}_{self._const_pref}'
        self._plot_dir  = f'{self._cache_dir}/plot_{self._dset}_{self._trig}/{self._q2bin}_{self._const_pref}'

        os.makedirs(self._cache_dir, exist_ok=True)
        os.makedirs(self._scale_dir, exist_ok=True)
        os.makedirs(self._pars_dir , exist_ok=True)
        os.makedirs(self._plot_dir , exist_ok=True)
    #----------------------------------------
    def _get_ranges(self):
        d_range = {}

        d_range['B_M']      = (self._low_m, self._high_m)
        d_range['BDT_cmb']  = (0.0, self._bdt_cmb_wp)
        d_range['Jpsi_M']   = (self._jpsi_dn, self._jpsi_up)
        d_range['B_jpsi_M'] = (self._low_m, self._high_m)
        d_range['L1_PT']    = (2000.0, 15000.0)
        d_range['L2_PT']    = (2000.0, 15000.0)
        d_range['L1_P']     = (2000.0, 100000.0)
        d_range['L2_P']     = (2000.0, 100000.0)

        return d_range
    #----------------------------------------
    def _compare_var(self, df_ss, df_os, var):
        fig, _ = plt.subplots(figsize=(8,5))
        ax = None
        ax = df_ss.plot.hist(column=[var], density=True, bins=self._nbins, histtype='step', range=self._d_range[var], ax=ax)
        ax = df_os.plot.hist(column=[var], density=True, bins=self._nbins, histtype='step', range=self._d_range[var], ax=ax)
        ax.legend(['SS', 'OS'])

        path = f'{self._plot_dir}/{var}.png'

        log.info(f'Saving to: {path}')

        plt.xlabel(var)
        plt.savefig(path)
        plt.close('all')
    #----------------------------------------
    def _get_stats(self, df, stage):
        nevs = len(df.index)
        log.info(f'{stage:<20}{nevs:<20}')

        return nevs
    #----------------------------------------
    def _remove_spikes(self, df, sample):
        proc    = self._d_sample[sample]
        trig    = self._trig[1:]
        spk_path= f'{self._cache_dir}/{proc}_{self._channel}_{self._dset}_{trig}/spikes.json'
        if not os.path.isfile(spk_path):
            log.warning(f'Spikes path not found: {spk_path}')
            return df
        else:
            log.info(f'Removing spikes with: {spk_path}')

        l_mass  = utnr.load_json(spk_path)
        mat_rem = numpy.array([l_mass] * len(df.B_M)).T
        arr_flg = numpy.isclose(df.B_M, mat_rem, atol=1e-5).any(axis=0)
        df      = df[~arr_flg]

        return df
    #----------------------------------------
    def _filter(self, df, sample, invert_bdt=True, highest_q2=False):
        bdt_cut = self._bdt_cut_inv if invert_bdt else self._bdt_cut_sgn
        mas_cut = f'B_M > {self._low_m} and B_M < {self._high_m}'

        ntot=self._get_stats(df, 'Total')

        df=df.query(      bdt_cut)
        nbdt=self._get_stats(df, 'bdt cut')

        qsq_cut = self._highest_q2 if highest_q2 else self._qsq_cut
        df=df.query(qsq_cut)
        nqsq=self._get_stats(df, 'qsq cut')

        df=df.query(      mas_cut)
        nmas=self._get_stats(df, 'mass cut')

        df.bdt_cut = bdt_cut

        eff_bdt = efficiency(nbdt, arg_tot=ntot, cut=bdt_cut)
        eff_qsq = efficiency(nqsq, arg_tot=nbdt, cut=qsq_cut)
        eff_mas = efficiency(nmas, arg_tot=nqsq, cut=mas_cut)
        
        cfl        = cutflow()
        cfl['bdt'] = eff_bdt
        cfl['qsq'] = eff_qsq
        cfl['mas'] = eff_mas

        bdt_label= 'invbdt' if invert_bdt else 'sigbdt'
        qsq_label= 'higqsq' if highest_q2 else 'stdqsq'
        label    = f'{bdt_label}_{qsq_label}'
        cfl_path = f'{self._plot_dir}/cfl_{sample}_{label}.json'
        log.info(f'Saving to: {cfl_path}')
        cfl.to_json(cfl_path)

        log.info(f'#Events for {sample}: {len(df.index)}')

        self._plot_data(df, sample, label)

        return df
    #----------------------------------------
    def _plot_data(self, df, sample, label):
        df.B_M.hist(bins=50)
        plt.title(f'{sample}; {label}')
        plot_path = f'{self._plot_dir}/data_{sample}_{label}.png'
        plt.savefig(plot_path)
        plt.close('all')
    #----------------------------------------
    def _replace_mass(self, df):
        if   self._q2bin == 'jpsi':
            df['B_M'] = df['B_jpsi_M'] 
        elif self._q2bin == 'psi2':
            df['B_M'] = df['B_psi2_M'] 
        else:
            log.error(f'Invalid q2bin: {self._q2bin}')
            raise

        return df
    #----------------------------------------
    def _get_paths(self, sample):
        proc    = self._d_sample[sample]
        trig    = self._trig[1:]

        dset       = '*' if self._dset == 'all' else self._dset
        dat_dir_wc = f'{self._cache_dir}/{proc}_{self._channel}_{dset}_{trig}'

        l_path  = glob.glob(f'{dat_dir_wc}/data*.json')

        if len(l_path) == 0:
            log.error(f'No JSON path found in {dat_dir}')
            raise
        else:
            log.info(f'Using {len(l_path)} paths')

        return l_path
    #----------------------------------------
    def _get_data(self, sample=None, invert_bdt=True, highest_q2=False):
        bdt_nam = 'invbdt' if invert_bdt else 'sigbdt'
        qsq_nam = 'higqsq' if highest_q2 else 'stdqsq'

        key = f'{sample}_{bdt_nam}_{qsq_nam}'
        if key in self._d_data:
            return self._d_data[key]

        l_path = self._get_paths(sample)

        l_df = [ pnd.read_json(path) for path in l_path]
        df   = pnd.concat(l_df, axis=0)
        self._get_stats(df, 'loading')
        if self._mass_const: 
            df = self._replace_mass(df)

        df   = self._remove_spikes(df, sample)
        df   = self._mix_evt(df, sample)
        df   = self._filter(df, sample, invert_bdt = invert_bdt, highest_q2=highest_q2)

        self._d_data[key] = df

        return df
    #----------------------------------------
    def _mix_evt(self, df, sample):
        if not self._evt_mix:
            log.info(f'Not using event mixing')
            return df

        log.info(f'Using event mixing')

        mgr=amgr(df)

        obj=evt_mixer(shift_vars=['H_PE', 'H_PX', 'H_PY', 'H_PZ'], period=1)
        obj.d_check = {'bplus' : sample}
        obj.out_dir = self._plot_dir
        df =obj.get_df(df=df, d_name={'jpsi' : 'Jpsi_M', 'bplus' : 'B_M'})

        obj=evt_mixer(shift_vars=['L1_PE', 'L1_PX', 'L1_PY', 'L1_PZ'], period=2)
        df =obj.get_df(df=df, d_name={'jpsi' : 'Jpsi_M', 'bplus' : 'B_M'})

        df =mgr.add_atr(df)

        return df
    #----------------------------------------
    def _get_sujh(self):
        mu  = zfit.Parameter('mu', 4500, 3000, 6000)
        lm  = zfit.Parameter('lm',   50,   20, 3000)
        gm  = zfit.Parameter('gm',  -10,  -15,   -1)
        dl  = zfit.Parameter('dl',    5, 0.00,   20)
        ne  = zfit.Parameter('ne', 1000,    0,  1e6)
        
        pdf = zpdf_jh(obs=self._obs, mu=mu, lm=lm, gamma=gm, delta=dl)
        pdf = pdf.create_extended(ne, name='SUJohnson')

        return pdf
    #----------------------------------------
    def _get_expo(self):
        lm  = zfit.Parameter('lm',  -0.001,   -0.010,  0)
        
        pdf = zfit.pdf.Exponential(obs=self._obs, lam=lm)

        return pdf
    #----------------------------------------
    def _get_mexp(self):
        mu  = zfit.Parameter('mu',  3700,   2500, 4000)
        ap  = zfit.Parameter('ap',  0.001, -0.05, 0.05)
        bt  = zfit.Parameter('bt',  0.001,     0, 0.01)

        pdf = zpdf_me(self._obs, mu=mu, alpha=ap, beta=bt)

        return pdf
    #----------------------------------------
    def _get_hexp(self):
        mu  = zfit.Parameter('mu',  3700,     2500,  6000)
        ap  = zfit.Parameter('ap',  0.001,  0.0001,  0.05)
        bt  = zfit.Parameter('bt',  0.001,       0,  0.01)
        ne  = zfit.Parameter('ne', 1000,    0,  1e6)

        pdf = zpdf_he(self._obs, mu=mu, alpha=ap, beta=bt)
        pdf = pdf.create_extended(ne, name='Hyper exponential')

        return pdf
    #----------------------------------------
    def _get_pdf(self):
        if   self._pdf is not None:
            return self._pdf
        elif self._pdf is     None and self._q2bin == 'high':
            self._pdf = self._get_sujh()
        elif self._pdf is     None and self._q2bin == 'psi2':
            self._pdf = self._get_sujh()
        elif self._pdf is     None and self._q2bin == 'jpsi':
            self._pdf = self._get_sujh()
        else:
            log.error(f'Invalid q2 bin: {self._q2bin}')
            raise

        if   self._q2bin == 'high':
            self._pdf = zut_fix(self._pdf, {'gm' : [self._gm_hi, 0], 'dl' : [self._dl_hi, 0]})
        elif self._q2bin == 'psi2':
            self._pdf = zut_fix(self._pdf, {'gm' : [self._gm_ps, 0], 'lm' : [self._lm_ps, 0]})
        elif self._q2bin == 'jpsi':
            self._pdf = zut_fix(self._pdf, {'gm' : [self._gm_jp, 0], 'lm' : [self._lm_jp, 0]})

        return self._pdf
    #----------------------------------------
    def _ends_in(self, name, l_end):
        l_flg = [ name.endswith(end) for end in l_end ]
        l_flg = [ int(flg) for flg in l_flg]

        flg   = sum(l_flg)

        if flg not in [0, 1]:
            log.error(f'Flag is: {flg}')
            raise ValueError

        return flg == 1
    #----------------------------------------
    def _fit(self, df, name, title):
        arr_mass = df.B_M.to_numpy()
        bdt_cut  = df.bdt_cut
        bdt_cut  = bdt_cut.replace('and', '\n')
        title    = f'{bdt_cut}\n{title}'
        pdf      = self._get_pdf()

        obj=zfitter(pdf, arr_mass)
        res=obj.fit(ntries=self._fit_tries, ranges=[(self._low_m, self._low_blind), (self._high_blind, self._high_m)])

        if res.status != 0 or not res.valid:
            log.error(f'Failed fit: {name}')
            self._plot_fit(arr_mass, pdf, res, title, name)
            print(res)
            raise

        res.hesse()

        self._plot_fit(arr_mass, pdf, res, title, name)

        return res
    #----------------------------------------
    def _plot_fit(self, arr_mass, pdf, res, title, name):
        obj=zfp(data=arr_mass, model=pdf, result=res)
        obj.plot(nbins=self._nbins, d_leg={}, plot_range=self._d_range['B_M'], ext_text=title)
        obj.axs[0].axvline(x=self._low_blind , color='red', linestyle=':')
        obj.axs[0].axvline(x=self._high_blind, color='red', linestyle=':')

        os.makedirs(f'{self._plot_dir}/fits', exist_ok=True)

        log.info(f'Saving to: {self._plot_dir}/fits/{name}.png')
        plt.savefig(f'{self._plot_dir}/fits/{name}.png')
        plt.close('all')

        return res
    #----------------------------------------
    def _compare(self, df_ss, df_os):
        self._compare_var(df_ss, df_os, 'BDT_cmb')
        self._compare_var(df_ss, df_os, 'B_M')
        self._compare_var(df_ss, df_os, 'Jpsi_M')
        self._compare_var(df_ss, df_os, 'B_jpsi_M')
        self._compare_var(df_ss, df_os, 'L1_PT')
        self._compare_var(df_ss, df_os, 'L2_PT')
        self._compare_var(df_ss, df_os, 'L1_P')
        self._compare_var(df_ss, df_os, 'L2_P')
    #----------------------------------------
    def _get_quantiles(self, df):
        arr_qnt = numpy.array([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.977]) 

        d_qnt = dict()
        for iqnt in range(arr_qnt.size - 1):
            low = arr_qnt[iqnt + 0]
            hig = arr_qnt[iqnt + 1]

            d_qnt[f'qnt_{iqnt}'] = (low, hig)

        return d_qnt, arr_qnt
    #----------------------------------------
    def _res_to_df(self, res, index=None):
        d_data = {}
        for par, d_val in res.params.items():
            val = d_val['value']
            err = d_val['hesse']['error']

            d_data[f'{par.name}_val'] = [val]
            d_data[f'{par.name}_err'] = [err]

        d_data['quantile'] = [index]

        return pnd.DataFrame(d_data)
    #----------------------------------------
    def _vars_from_df(self, df):
        s_par_name = {name.replace('_err', '').replace('_val', '') for name in df.columns}

        return s_par_name
    #----------------------------------------
    def _add_norm_yld(self, df, low, hig):
        db = hig - low

        df['dne_val'] = df.ne_val / db
        df['dne_err'] = df.ne_err / db

        return df
    #----------------------------------------
    def _get_fit_df(self, d_res):
        l_df_ss = []
        l_df_os = []
        for qnt, (res_ss, res_os, low_b, hig_b) in d_res.items():
            df_ss = self._res_to_df(res_ss, index=qnt)
            df_os = self._res_to_df(res_os, index=qnt)

            df_ss = self._add_norm_yld(df_ss, low_b, hig_b)
            df_os = self._add_norm_yld(df_os, low_b, hig_b)

            l_df_ss.append(df_ss)
            l_df_os.append(df_os)

        df_ss = pnd.concat(l_df_ss, axis=0)
        df_os = pnd.concat(l_df_os, axis=0)

        df_ss = df_ss.set_index('quantile', drop=True)
        df_os = df_os.set_index('quantile', drop=True)

        return df_ss, df_os
    #----------------------------------------
    def _plot_pars(self, df_ss, df_os):
        os.makedirs(f'{self._plot_dir}/fits/pars/', exist_ok=True)

        s_par_name = { name.replace('_err', '').replace('_val', '') for name in df_ss.columns }
        for par_name in s_par_name:
            ax=None
            ax=df_ss.plot(y=f'{par_name}_val', yerr=f'{par_name}_err', capsize=4, label='SS', ax=ax)
            ax=df_os.plot(y=f'{par_name}_val', yerr=f'{par_name}_err', capsize=4, label='OS', ax=ax)

            plt.ylabel(self._d_par_name[par_name])
            plt.grid()
            plt.savefig(f'{self._plot_dir}/fits/pars/{par_name}.png')
            plt.close('all')
    #----------------------------------------
    def _plot_scales(self, df_sc, d_par):
        plot_dir = f'{self._plot_dir}/scales' 
        os.makedirs(plot_dir, exist_ok=True)

        s_var = self._vars_from_df(df_sc)

        for par_name in s_var:
            avg, err, pval = d_par[par_name]

            ax = df_sc.plot(y=f'{par_name}_val', yerr=f'{par_name}_err', linestyle='none', capsize=4)

            plt.ylabel(self._d_par_name[par_name])
            plt.xlabel('quantile')

            plt.axhline(color='red', y=avg + err, linestyle=':')
            plt.axhline(color='red', y=avg)
            plt.axhline(color='red', y=avg - err, linestyle=':')

            plt.grid(True)
            plt.legend(title=f'p-value={pval:.3f}', labels=['$-\sigma$', 'mean', '$+\sigma$', 'Difference'])
            plot_path = f'{plot_dir}/{par_name}.png'
            log.info(f'Saving to: {plot_path}')
            plt.savefig(plot_path)
            plt.close('all')
    #----------------------------------------
    def _get_scales(self, df_ss, df_os):
        d_scale = {}
        if   self._q2bin == 'high':
            nlast = -1 if not self._evt_mix else self._nquantile 
            nfrst =  0
        elif self._q2bin == 'jpsi':
            nlast = -1 if not self._evt_mix else self._nquantile 
            nfrst =  0
        elif self._q2bin == 'psi2':
            nlast = -1 if not self._evt_mix else self._nquantile 
            nfrst =  0
        else:
            log.error(f'Invalid q2bin: {self._q2bin}')
            raise

        for par_name in self._vars_from_df(df_ss):
            arr_ss_val = df_ss[f'{par_name}_val'].to_numpy()
            arr_os_val = df_os[f'{par_name}_val'].to_numpy()

            arr_ss_err = df_ss[f'{par_name}_err'].to_numpy()
            arr_os_err = df_os[f'{par_name}_err'].to_numpy()

            arr_sc_val = arr_ss_val - arr_os_val
            arr_sc_err = numpy.sqrt( arr_ss_err ** 2 + arr_os_err ** 2 )

            if nlast is not None:
                arr_sc_val = arr_sc_val[:nlast]
                arr_sc_err = arr_sc_err[:nlast]

            if nfrst is not None:
                arr_sc_val = arr_sc_val[nfrst:]
                arr_sc_err = arr_sc_err[nfrst:]

            d_scale[f'd_{par_name}_val'] = arr_sc_val
            d_scale[f'd_{par_name}_err'] = arr_sc_err

        return pnd.DataFrame(d_scale)
    #----------------------------------------
    def _load_pars(self):
        pars_path_ss = f'{self._pars_dir}/{self._trig}_{self._dset}_ss.json'
        pars_path_os = f'{self._pars_dir}/{self._trig}_{self._dset}_os.json'

        if not os.path.isfile(pars_path_ss):
            return False

        self._df_ss = pnd.read_json(pars_path_ss)
        self._df_os = pnd.read_json(pars_path_os)

        log.info('Parameter dataframes found, loading them')

        return True
    #----------------------------------------
    def _save_fit_pars(self, df_ss, df_os):
        pars_path_ss = f'{self._pars_dir}/{self._trig}_{self._dset}_ss.json'
        pars_path_os = f'{self._pars_dir}/{self._trig}_{self._dset}_os.json'

        df_ss.to_json(pars_path_ss, indent=4)
        df_os.to_json(pars_path_os, indent=4)

        log.info('Cached fit dataframe parameters')
    #----------------------------------------
    def _bin_df(self, df, only_sr=None):
        if only_sr:
            return {'qnt_h' : df}

        d_df = {}
        for key, (low, hig) in self._d_qnt.items():
            df_binned         = df[(df.BDT_cmb > low) & (df.BDT_cmb < hig)]
            df_binned.bdt_cut = df.bdt_cut
            d_df[key]         = df_binned

        return d_df
    #----------------------------------------
    def _get_ddf(self, highest_q2=None, only_sr=None, invert_bdt=None):
        df_os = self._get_data(sample='OS', highest_q2=highest_q2, invert_bdt=invert_bdt)
        df_ss = self._get_data(sample='SS', highest_q2=highest_q2, invert_bdt=invert_bdt)

        d_df_os = self._bin_df(df_os, only_sr=only_sr)
        d_df_ss = self._bin_df(df_ss, only_sr=only_sr)

        return d_df_os, d_df_ss
    #----------------------------------------
    def _get_pars(self):
        if self._load_pars():
            return self._df_ss, self._df_os

        d_df_os  , d_df_ss   = self._get_ddf(highest_q2=False, only_sr=False, invert_bdt=True )
        d_df_os_2, d_df_ss_2 = self._get_ddf(highest_q2=True , only_sr=True , invert_bdt=False)

        d_df_os.update(d_df_os_2)
        d_df_ss.update(d_df_ss_2)

        d_res        = self._fit_bins(d_df_ss, d_df_os)
        df_ss, df_os = self._get_fit_df(d_res)

        self._save_fit_pars(df_ss, df_os)

        return df_ss, df_os
    #----------------------------------------
    def _get_bdt_from_quantile(self, qnt):
        if qnt == 'qnt_h':
            return self._bdt_cmb_wp, 2

        [i_qnt] = re.match(r'qnt_(\d)', qnt).groups()
        i_qnt   = int(i_qnt)

        low_b = self._arr_qnt[i_qnt + 0]
        hig_b = self._arr_qnt[i_qnt + 1]

        return low_b, hig_b
    #----------------------------------------
    def _fit_bins(self, d_df_ss, d_df_os):
        d_res = {}
        for qnt in d_df_ss:
            low_b, hig_b = self._get_bdt_from_quantile(qnt)
            title = f'{low_b:.3f} < $BDT_{{cmb}}$ < {hig_b:.3f}'
            log.info(f'Fitting in {title}/{qnt}')

            df_ss = d_df_ss[qnt]
            df_os = d_df_os[qnt]

            res_os = self._fit(df_os, f'OS_{qnt}', title)
            res_ss = self._fit(df_ss, f'SS_{qnt}', title)

            d_res[qnt] = (res_ss, res_os, low_b, hig_b)

        return d_res
    #----------------------------------------
    def _avg_scales(self, df_sc):
        d_scale = {}

        for par_name in self._vars_from_df(df_sc):
            arr_val = df_sc[f'{par_name}_val'].to_numpy()
            arr_err = df_sc[f'{par_name}_err'].to_numpy()

            avg, err, pvl = sta_avg(arr_val, arr_err)
            d_scale[par_name] = [avg, err, pvl]

        return d_scale
    #----------------------------------------
    def _plot_quantiles(self):
        df_os = self._get_data(sample='OS')
        df_ss = self._get_data(sample='SS')

        ax=None
        ax=df_ss.plot.hist(column=['BDT_cmb'], range=self._d_range['BDT_cmb'], histtype='step', bins=self._nquantile, ax=ax)
        ax=df_os.plot.hist(column=['BDT_cmb'], range=self._d_range['BDT_cmb'], histtype='step', bins=self._nquantile, ax=ax)

        for bdt_qnt in self._arr_qnt:
            ax.axvline(x=bdt_qnt, linewidth=0.5, color='gray', linestyle='-')

        plot_path = f'{self._plot_dir}/quantiles.png'
        log.info(f'Saving to: {plot_path}')
        plt.legend(['SS', 'OS'])
        plt.yscale('log')
        plt.gca().set_ylim(bottom=0.1)
        plt.xlabel('$BDT_{cmb}$')
        plt.savefig(plot_path)
        plt.close('all')
    #----------------------------------------
    def _fit_sr(self, sample):
        df    = self._get_data(sample=sample, invert_bdt=False)
        title = f'{sample}, {self._bdt_cut_sgn}'
        res   = self._fit(df, f'{sample}_qnt_s', title)

        d_par = {}
        for par, d_val in res.params.items():
            name= par.name
            val = d_val['value']
            err = d_val['hesse']['error']
            pvl = 1

            d_par[f'{name}_{sample}'] = (par.lower.numpy(), par.upper.numpy(), val, err)

        print(res)

        return d_par
    #----------------------------------------
    def _plot_sr(self, sample):
        df       = self._get_data(sample=sample, invert_bdt=False)
        title    = f'{sample}, {self._bdt_cut_sgn}'
        name     = f'{sample}_qnt_s'
        arr_mass = df.B_M.to_numpy()

        os.makedirs(f'{self._plot_dir}/fits', exist_ok=True)

        plt.hist(arr_mass, bins=100, histtype='step')
        plt.savefig(f'{self._plot_dir}/fits/{name}.png')
        plt.close('all')
    #----------------------------------------
    def _save_pars(self, d_par):
        scale_path = f'{self._scale_dir}/{self._q2bin}_{self._const_pref}_{self._trig}_{self._dset}.json'

        if   self._q2bin == 'high':
            d_par['dl'] = (0, 0, self._dl_hi, 0)
            d_par['gm'] = (0, 0, self._gm_hi, 0)
        elif self._q2bin == 'psi2':
            d_par['lm'] = (0, 0, self._lm_ps, 0)
            d_par['gm'] = (0, 0, self._gm_ps, 0)
        elif self._q2bin == 'jpsi':
            d_par['lm'] = (0, 0, self._lm_jp, 0)
            d_par['gm'] = (0, 0, self._gm_jp, 0)
        else:
            log.error(f'Invalid q2bin: {self._q2bin}')
            raise ValueError

        log.info(f'Saving scales to: {scale_path}')
        utnr.dump_json(d_par, scale_path)
    #----------------------------------------
    def save_pars(self):
        self._initialize()

        df_ss, df_os = self._get_pars()

        self._plot_pars(df_ss, df_os)
        df_sc        = self._get_scales(df_ss, df_os)
        d_par        = self._avg_scales(df_sc)
        self._plot_scales(df_sc, d_par)
        self._plot_quantiles()

        d_ss_sr = self._fit_sr('SS')
        d_par.update(d_ss_sr)

        if self._evt_mix:
            d_os_sr = self._fit_sr('OS')
            d_par.update(d_os_sr)

        self._save_pars(d_par)

        if self._q2bin != 'high' and not self._evt_mix:
            d_os_sr = self._plot_sr('OS')

        return d_par
#----------------------------------------

