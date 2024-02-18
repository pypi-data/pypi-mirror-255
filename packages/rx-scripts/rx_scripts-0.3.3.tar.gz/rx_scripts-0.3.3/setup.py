from setuptools import setup, find_packages

import glob

setup(
        name            ="rx_scripts",
        version         ='0.3.3',
        description     ='Generic utilities for data analysis',
        long_description='Package used to store utilities for RX calculation',
        scripts         = glob.glob('scripts/*') + glob.glob('jobs/*'),
        packages        = ['', 'stats', 'zutils', 'plotting'], 
        package_dir     = {'' : 'src'},
        install_requires= open('requirements.txt').read()
        )

