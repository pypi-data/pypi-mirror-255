from setuptools import setup, find_packages
#from version import find_version
from codecs import open
from os import path
import re

#here = path.abspath(path.dirname(__file__))



with open('imputetspy/__init__.py', encoding='utf-8') as f:
    __version__ = re.search(r'__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read()).group(1)



setup(
        name = 'imputetspy',
        author = 'Ahmad Zaenal',
        description = 'Re-written R package "imputeTS" in python code with some other imputation in time series method ',
        long_description = 'Imputation method for time series data inspired by *imputeTS* package in R',
        license = 'MIT',
        project_urls = {'Github': 'https://github.com/zaenalium/imputeTSpy', 'Documentation': 'https://imputetspy.readthedocs.io/en/latest/'},
        include_package_data=True,
        version=__version__,
        packages =  ['imputetspy'], #find_packages(),
        author_email='ahmadzaenal125@gmail.com',
        keywords='time series, imputation',  # Optional
        install_requires=['numpy','pandas>=0.25.0','matplotlib','scikit-learn>=0.19.1', 'statsmodels', 'patsy'],  # Optional
     )
