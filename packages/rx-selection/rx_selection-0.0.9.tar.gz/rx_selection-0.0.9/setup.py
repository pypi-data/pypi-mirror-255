from setuptools import setup, find_packages

import glob

setup(
        name            ='rx_selection',
        version         ='0.0.9',
        description     ='Scripts for applying selection',
        long_description='',
        scripts         = glob.glob('scripts/*'),
        packages        = ['', 'selection_data', 'selection_tables', 'selection'],
        package_data    = {'selection_data' : ['*.json']},
        package_dir     = {'' : 'src'},
        install_requires= open('requirements.txt').read().splitlines()
        )

