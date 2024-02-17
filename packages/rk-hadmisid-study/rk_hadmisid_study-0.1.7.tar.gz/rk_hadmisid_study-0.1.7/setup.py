from setuptools import setup, find_packages

import glob

setup(
        name            ='rk_hadmisid_study',
        version         ='0.1.7',
        author          ='xuzh',
        description     ='All tools and scripts used in the study of the hadron mis-ID.',
        packages        = find_packages(),
        package_data    = {'misID_data' : ['model/*/*/*/*.csv', 'model/*/*/*/*.json']},
        install_requires= open('requirements.txt').read()
        )
