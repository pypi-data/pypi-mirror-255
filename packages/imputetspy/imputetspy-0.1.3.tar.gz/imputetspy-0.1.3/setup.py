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
        long_description = "This package is a package for all imputation method in time series method. Most of this kind of package are available in R, however, when we use the package for interfacing python to R is somehow complicated, and need to install a lot of things as well as the performance is doesn't meet our expectation. Thefore, I decide to create this dedicated python package for time series imputation. Please visit this (link)[https://imputetspy.readthedocs.io/] for the detail of the package documentations.",
        license = 'MIT',
        project_urls = {'Github': 'https://github.com/zaenalium/imputeTSpy', 'Documentation': 'https://imputetspy.readthedocs.io/en/latest/'},
        include_package_data=True,
        version=__version__,
        packages =  ['imputetspy'], #find_packages(),
        author_email='ahmadzaenal125@gmail.com',
        keywords='time series, imputation',  # Optional
        install_requires=['numpy','pandas>=0.25.0','matplotlib','scikit-learn>=0.19.1', 'statsmodels', 'patsy'],  # Optional
     )
