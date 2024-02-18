import logzero
from log_store import log_store
log_store.set_level('cb_calculator:builder', logzero.DEBUG)

from osss_builder import builder
from logzero      import logger  as log

import os
import zfit
import numpy

import zutils.utils      as zut
import utils_noroot      as utnr
import matplotlib.pyplot as plt

#----------------------------
def delete_all_pars():
    d_par = zfit.Parameter._existing_params
    l_key = list(d_par.keys())

    for key in l_key:
        del(d_par[key])
#----------------------------
def plot_pdf(pdf, min_x=4480, max_x=6500, label=None):
    arr_x = numpy.linspace(min_x, max_x, 2000)
    arr_y = pdf.pdf(arr_x)

    plt.plot(arr_x, arr_y, label=label) 
#----------------------------
def test_os():
    obs      = zfit.Space('mass', limits=(4000, 6500))

    obj      = builder(dset='2018', trigger='ETOS', q2bin='psi2', vers='v7', const=False)
    pdf_0, _ = obj.get_pdf(obs=obs, unc=  0, preffix='comp_ss')
    pdf_1, _ = obj.get_pdf(obs=obs, unc= -1, preffix='comp_os')

    plot_pdf(pdf_0, min_x=4000, max_x=6500, label='SS')
    plot_pdf(pdf_1, min_x=4000, max_x=6500, label='OS')

    out_dir = utnr.make_dir_path('tests/os')

    plt.legend()
    plt.xlabel('MeV')
    plt.ylabel('Normalized')
    plt.grid()
    log.info(f'Saving to: {out_dir}/plot.png')
    plt.savefig(f'{out_dir}/plot.png')
    plt.close('all')

    delete_all_pars()
#----------------------------
def test_comp():
    obs      = zfit.Space('mass', limits=(4480, 6500))

    obj      = builder(dset='all', trigger='ETOS', q2bin='high', vers='v9', const=False)
    pdf_0, _ = obj.get_pdf(obs=obs, unc=    0, preffix='comp_z')
    pdf_1, _ = obj.get_pdf(obs=obs, unc= None, preffix='comp_n')

    plot_pdf(pdf_0)
    plot_pdf(pdf_1)

    out_dir = utnr.make_dir_path('tests/comp')

    plt.legend(['SS', r'$\bar{OS}$'])
    plt.xlabel('MeV')
    plt.ylabel('Normalized')
    plt.grid()
    plt.savefig(f'{out_dir}/plot.png')
    plt.close('all')

    delete_all_pars()
#----------------------------
def test_unc():
    d_sys_1  = {'mu' :  0, 'lm' : +1}
    d_sys_2  = {'mu' :  0, 'lm' : -1}
    d_sys_3  = {'mu' : +1, 'lm' :  0}
    d_sys_4  = {'mu' : -1, 'lm' :  0}

    out_dir = utnr.make_dir_path('tests/unc')

    obs      = zfit.Space('mass', limits=(4480, 6500))

    obj      = builder(dset='2018', trigger='ETOS', q2bin='high', vers='v5', const=False)
    pdf_0, _ = obj.get_pdf(obs=obs, unc=       0, preffix='comp_z')
    pdf_1, _ = obj.get_pdf(obs=obs, unc=    None, preffix='comp_n')
    pdf_2, _ = obj.get_pdf(obs=obs, unc= d_sys_1, preffix='comp_1')
    pdf_3, _ = obj.get_pdf(obs=obs, unc= d_sys_2, preffix='comp_2')
    pdf_4, _ = obj.get_pdf(obs=obs, unc= d_sys_3, preffix='comp_3')
    pdf_5, _ = obj.get_pdf(obs=obs, unc= d_sys_4, preffix='comp_4')

    plot_pdf(pdf_0)
    plot_pdf(pdf_1)
    plot_pdf(pdf_2)
    plot_pdf(pdf_3)
    plot_pdf(pdf_4)
    plot_pdf(pdf_5)

    plt.legend(['SS', 
        r'$\bar{OS}$',  
        r'$\bar{OS} + \sigma_{\lambda}$', 
        r'$\bar{OS} - \sigma_{\lambda}$',
        r'$\bar{OS} + \sigma_{\mu}$', 
        r'$\bar{OS} - \sigma_{\mu}$'
        ])
    plt.xlabel('MeV')
    plt.ylabel('Normalized')
    plt.grid()
    plt.savefig(f'{out_dir}/plot.png')
    plt.close('all')

    delete_all_pars()
#----------------------------
def test_simple():
    os.makedirs('tests/builder/simple', exist_ok=True)
    for trig in ['MTOS', 'ETOS', 'GTIS']:
        obs      = zfit.Space('mass', limits=(4000, 6500))
        obj      = builder(dset='all', trigger=trig, q2bin='high', vers='v9', const=False)
        pdf_ss, _= obj.get_pdf(obs=obs, unc=  0, preffix='comp_ss', name='Comb')

        zut.print_pdf(pdf_ss)
        plot_pdf(pdf_ss)
        delete_all_pars()

    plt.legend(['mTOS', 'eTOS', 'gTIS!'])
    plt.savefig('tests/builder/simple/pdf.png')
#----------------------------
def test_fix_shape():
    obs      = zfit.Space('mass', limits=(4000, 6500))
    obj      = builder(dset='2018', trigger='ETOS', q2bin='high', vers='v5', const=False)
    pdf_ss, _= obj.get_pdf(obs=obs, unc=  0, preffix='comp_ss', name='Comb', fix_shape=True)

    zut.print_pdf(pdf_ss)

    delete_all_pars()
#----------------------------
def test_shared():
    os.makedirs('tests/builder/simple', exist_ok=True)
    obs      = zfit.Space('mass', limits=(4000, 6500))

    builder.d_shared = {'mu' : 'mu_cmb'}

    obj_1    = builder(dset='all', trigger='ETOS', q2bin='high', vers='v9', const=False)
    pdf_1, _ = obj_1.get_pdf(obs=obs, unc=  0, preffix='comp_ss_1', name='Comb')

    obj_2    = builder(dset='all', trigger='ETOS', q2bin='high', vers='v9', const=False)
    pdf_2, _ = obj_2.get_pdf(obs=obs, unc=  0, preffix='comp_ss_2', name='Comb')

    zut.print_pdf(pdf_1)
    zut.print_pdf(pdf_2)
#----------------------------
def main():
    test_shared()
    test_simple()
    test_fix_shape()
    test_os()
    test_comp()
    test_unc()
#----------------------------
if __name__ == '__main__':
    main()

