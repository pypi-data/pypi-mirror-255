from setuptools import setup, find_packages

import glob

setup(
        name                ='rx_tools',
        version             ='0.2.4',
        description         ='Project containing tools for RX measurement',
        long_description    ='',
        scripts             = glob.glob('scripts/*'),
        packages            = ['tools_data/trigger', 'rk'],
        package_dir         = {'' : 'src'},
        install_requires    = open('requirements.txt').read().splitlines(),
        )

