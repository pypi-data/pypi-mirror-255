from setuptools import setup, find_packages

import glob

setup(
        name            ='rx_differential_crosscheck_fits',
        version         ='0.0.4',
        description     ='Code used to fit jpsi and psi2S mode in bins of different variables',
        #scripts         = glob.glob('scripts/*'),
        package_dir     = {'' : 'python'},
        install_requires= open('requirements.txt').read()
        )


