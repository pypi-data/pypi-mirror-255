import logzero
from log_store import log_store
log_store.set_level('cb_calculator:builder', logzero.DEBUG)

import zfit
import numpy
import matplotlib.pyplot as plt
import zutils.utils      as zut
import utils_noroot      as utnr

from builder import builder

#------------------------------------
class data:
    obs = zfit.Space('obs', limits=(4500, 6100))
#------------------------------------
def test_simple():
    obj      = builder(dset='all', trigger='ETOS', version='v1')
    obj.kind = 'nominal' 
    pdf      = obj.get_pdf(obs=data.obs, preffix='simple', name='Combinatorial', fix_shape=False)

    zut.print_pdf(pdf)
#------------------------------------
def plot_pdf(pdf, label=None):
    arr_x = numpy.linspace(4500, 6100, 100)
    arr_y = pdf.pdf(arr_x)

    plt.plot(arr_x, arr_y, label=label) 
#------------------------------------
def test_syst():
    for kind in ['cmb_etos:alt_001', 'nominal']:
        obj      = builder(dset='all', trigger='ETOS', version='v1')
        obj.kind = kind
        pdf      = obj.get_pdf(obs=data.obs, preffix=kind, name='Combinatorial', fix_shape=False)

        plot_pdf(pdf, label=kind)

    dir_path = utnr.make_dir_path('tests/builder/syst/v1')
    plt.savefig(f'{dir_path}/overlaid.png')
    plt.close('all')
#------------------------------------
def main():
    test_syst()
    test_simple()
#------------------------------------
if __name__ == '__main__':
    main()
