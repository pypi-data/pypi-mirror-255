from setuptools import setup, find_packages

import os
import glob

#--------------------------------
def get_scripts():
    l_obj = glob.glob('scripts/*')
    l_file= [ obj for obj in l_obj if os.path.isfile(obj) ]

    return l_file
#--------------------------------
setup(
    name            = 'rx_combinatorial',
    version         = '0.0.9',
    description     = 'Project used to calculate combinatorial background shapes',
    long_description= '',
    scripts         = get_scripts(),
    packages        = [''], 
    package_dir     = {'' : 'src'},
    package_data    = {'cb_data' : ['*/*.json'], 'cb_pars' : ['*/*.json']},
    install_requires= open('requirements.txt').read()
)

