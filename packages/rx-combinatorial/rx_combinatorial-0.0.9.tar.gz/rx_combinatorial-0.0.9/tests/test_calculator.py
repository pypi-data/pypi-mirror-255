from cb_calculator import calculator as calc

from zutils.pdf    import SUJohnson  as zpdf_jh
from zutils.pdf    import modexp     as zpdf_me

from logzero import logger as log

import pandas as pnd 
import numpy
import zfit
import math
import os
#-----------------------------------------------
class data:
    d_ne   = 10000

    d_mu_h = 100
    d_lm_h =  10

    mu_h   = 4200
    lm_h   =   50

    d_mu_j = 100
    d_ap_j = 0.01
    d_bt_j = 0.01

    mu_j   =  3800
    ap_j   = 0.003
    bt_j   = 0.002

    numpy.random.seed(seed=1)
#-----------------------------------------------
def delete_all_pars():
    d_par = zfit.Parameter._existing_params
    l_key = list(d_par.keys())

    for key in l_key:
        del(d_par[key])
#-----------------------------------------------
def get_model(q2bin, kind):
    if q2bin == 'high':
        obs = zfit.Space(f'mass_{q2bin}_{kind}', limits=(4480, 6500))
    else:
        obs = zfit.Space(f'mass_{q2bin}_{kind}', limits=(4000, 6000))

    if kind == 'OS':
        mu_h = data.mu_h + data.d_mu_h
        lm_h = data.lm_h + data.d_lm_h

        mu_j = data.mu_j + data.d_mu_j
        ap_j = data.ap_j + data.d_ap_j
        bt_j = data.bt_j + data.d_bt_j
    else:
        mu_h = data.mu_h
        lm_h = data.lm_h

        mu_j = data.mu_j
        ap_j = data.ap_j
        bt_j = data.bt_j

    if   q2bin in ['psi2', 'high']:
        mu  = zfit.Parameter(f'mu_tst_{kind}', mu_h, 4000, 5000)
        lm  = zfit.Parameter(f'lm_tst_{kind}', lm_h,   20,  100)
        gm  = zfit.Parameter(f'gm_tst_{kind}',        -10,  -15,   -1)
        dl  = zfit.Parameter(f'dl_tst_{kind}',        2.5, 0.01,   20)
        
        pdf = zpdf_jh(obs=obs, mu=mu, lm=lm, gamma=gm, delta=dl)
    elif q2bin == 'jpsi':
        mu  = zfit.Parameter(f'mu_tst_{kind}', mu_j,    2500,  4000)
        ap  = zfit.Parameter(f'ap_tst_{kind}', ap_j,  0.0001,  0.05)
        bt  = zfit.Parameter(f'bt_tst_{kind}', bt_j,       0,  0.01)
        
        pdf = zpdf_me(obs=obs, mu=mu, alpha=ap, beta=bt)
    else:
        log.error(f'Invalid q2bin: {q2bin}')
        raise

    return pdf
#-----------------------------------------------
def get_data(q2bin, nentries=100000, kind=None):
    df      = pnd.DataFrame(columns=['B_M', 'B_jpsi_M', 'B_psi2_M', 'Jpsi_M', 'BDT_cmb', 'BDT_prc'])
    pdf     = get_model(q2bin, kind) 

    b_m     = pdf.create_sampler(n=nentries)
    b_m     = b_m.numpy().flatten()

    if q2bin == 'high':
        low_bound = 3800
        hig_bound = 5000 
    else:
        log.error(f'Invalid q2 bin: {q2bin}')
        raise

    j_m     = numpy.random.uniform(low_bound, hig_bound, size=nentries)
    bdt_prc = numpy.random.uniform(0, 1, size=nentries)
    bdt_cmb = numpy.random.uniform(0, 1, size=nentries)

    df.B_M      =  b_m
    df.B_jpsi_M =  b_m
    df.B_psi2_M =  b_m
    df.Jpsi_M   =  j_m 
    df.BDT_prc  =  bdt_prc 
    df.BDT_cmb  =  bdt_cmb

    delete_all_pars()

    return df
#-----------------------------------------------
def save_df(df, dir_path):
    df_1 = df.iloc[     :25000]
    df_2 = df.iloc[25000:50000]
    df_3 = df.iloc[50000:75000]
    df_4 = df.iloc[75000:    ]

    df_1 = df_1.reset_index(drop=True)
    df_2 = df_2.reset_index(drop=True)
    df_3 = df_3.reset_index(drop=True)
    df_4 = df_4.reset_index(drop=True)

    os.makedirs(dir_path, exist_ok=True)

    log.info(f'Saving to: {dir_path}')

    df_1.to_json(f'{dir_path}/data_0_4.json', indent=4)
    df_2.to_json(f'{dir_path}/data_1_4.json', indent=4)
    df_3.to_json(f'{dir_path}/data_2_4.json', indent=4)
    df_4.to_json(f'{dir_path}/data_3_4.json', indent=4)
#-----------------------------------------------
def make_data(q2bin, year, nentries=10000):
    dat_dir     = f'tests/cache/{q2bin}'
    os_dir_path = f'{dat_dir}/data_ee_{year}_TOS'
    ss_dir_path = f'{dat_dir}/cmb_ee_{year}_TOS'

    if os.path.isdir(os_dir_path) and os.path.isdir(ss_dir_path):
        log.info(f'Data already cached, not remaking it')
        return

    df_ss = get_data(q2bin, nentries            , kind='SS')
    df_os = get_data(q2bin, nentries + data.d_ne, kind='OS')

    save_df(df_os, os_dir_path)
    save_df(df_ss, ss_dir_path)
#-----------------------------------------------
def test_high():
    q2bin= 'high'
    cwd  = os.getcwd()

    make_data(q2bin, '2016')
    make_data(q2bin, '2018')

    obj  =calc(dset='all', trig='ETOS', vers=f'v0_{q2bin}', q2bin=q2bin, mass_const=False)
    obj.cache_dir= f'{cwd}/tests/cache/{q2bin}'
    obj.fit_tries= 1
    d_par=obj.save_pars()
#-----------------------------------------------
def check(d_par, q2bin):
    if q2bin == 'high':
        check_delta(d_par, 'lm')
        check_delta(d_par, 'mu')
#-----------------------------------------------
def check_delta(d_par, name):
    measured, error, _ = d_par[f'd_{name}']

    if   name == 'mu':
        cnd_1 = math.isclose(measured,  -85.94389907346911, abs_tol=1e-7)
        cnd_2 = math.isclose(   error,   9.649602485999054, abs_tol=1e-7)
    elif name == 'lm':
        cnd_1 = math.isclose(measured, -10.825624042322298, abs_tol=1e-7)
        cnd_2 = math.isclose(   error,   0.577324335009675, abs_tol=1e-7)
    else:
        log.error(f'Invalid parameter: {name}')
        raise

    assert(cnd_1 and cnd_2)
#-----------------------------------------------
def main():
    test_high()
#-----------------------------------------------
if __name__ == '__main__':
    main()

