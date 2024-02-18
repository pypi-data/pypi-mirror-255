from evt_mixer import evt_mixer as emix

import ROOT
import utils_noroot as utnr
import pandas       as pnd
import os
import math

#-----------------------------------------
class data:
    ran      = ROOT.TRandom3(1)
    out_dir  = utnr.make_dir_path('tests/evt_mixer')
    data_path= f'{out_dir}/data.json'
#-----------------------------------------
def rbmass():
    return data.ran.Gaus(5280, 30)
#-----------------------------------------
def rjmass():
    return data.ran.Gaus(3000, 10)
#-----------------------------------------
def rphi():
    return data.ran.Uniform(-math.pi, +math.pi)
#-----------------------------------------
def reta():
    return data.ran.Uniform(1.2, 5)
#-----------------------------------------
def rpt():
    return data.ran.Uniform(5e3, 2e4)
#-----------------------------------------
def get_entry():
    B_lor = ROOT.TLorentzVector()
    B_lor.SetPtEtaPhiM(rpt(), reta(), rphi(), rbmass() )

    J_lor = ROOT.TLorentzVector()
    J_lor.SetPtEtaPhiM(rpt(), reta(), rphi(), rjmass() )

    e_lor = ROOT.TLorentzVector()
    e_lor.SetPtEtaPhiM(rpt(), reta(), rphi(), 0 )

    p_lor = J_lor - e_lor

    k_lor = B_lor - e_lor - p_lor

    l_em = [e_lor.E(),  e_lor.Px(),  e_lor.Py(),  e_lor.Pz()]
    l_ep = [p_lor.E(),  p_lor.Px(),  p_lor.Py(),  p_lor.Pz()]
    l_kp = [k_lor.E(),  k_lor.Px(),  k_lor.Py(),  k_lor.Pz()]

    return [B_lor.M()] + l_em + l_ep + l_kp
#-----------------------------------------
def make_data(nentries):
    df = pnd.DataFrame(columns=['B_M', 'L1_PE', 'L1_PX', 'L1_PY', 'L1_PZ', 'L2_PE', 'L2_PX', 'L2_PY', 'L2_PZ', 'H_PE', 'H_PX', 'H_PY', 'H_PZ'])
    for i_entry in range(nentries):
        row = get_entry()
        df = utnr.add_row_to_df(df, row, index=i_entry)

    return df
#-----------------------------------------
def get_data():
    if os.path.isfile(data.data_path):
        df = pnd.read_json(data.data_path)
    else:
        df = make_data(10000)
        df.to_json(data.data_path, indent=4)

    return df
#-----------------------------------------
def test_simple():
    df  = get_data()
    emx = emix(shift_vars=['H_PE', 'H_PX', 'H_PY', 'H_PZ'], period=2)
    emx.out_dir = f'{data.out_dir}/simple'
    df  = emx.get_df(df=df, d_name={'jpsi' : 'Jpsi_Mx', 'bplus' : 'B_Mx'})
#-----------------------------------------
def test_diagnostics():
    df  = get_data()
    emx = emix(shift_vars=['H_PE', 'H_PX', 'H_PY', 'H_PZ'], period=2)
    emx.d_check = {'bplus' : 'diag'}
    emx.out_dir = f'{data.out_dir}/diagnostics'
    df  = emx.get_df(df=df, d_name={'jpsi' : 'Jpsi_Mx', 'bplus' : 'B_Mx'})
#-----------------------------------------
def main():
    test_simple()
    test_diagnostics()
#-----------------------------------------
if __name__ == '__main__':
    main()

