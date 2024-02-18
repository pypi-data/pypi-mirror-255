from sscorr import sscorr

#-----------------------------------
def test_simple():
    obj=sscorr(version='v7', q2bin='high', trigger='ETOS', dset='2018')
    obj.cuts    = {'BDT_cmb' : 0.977, 'BDT_prc' : 0.480751}
    obj.plt_dir = 'tests/sscorr'
    obj.plot_ss()
    obj.plot_os()

#-----------------------------------
if __name__ == '__main__':
    test_simple()

