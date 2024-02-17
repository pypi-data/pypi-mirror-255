import numpy as np
import pandas as pd
from importlib import resources


DATA_MODULE = "imputetspy"

def ts_airgap():
    '''

    Time series of monthly airline passengers (with missing values)
    ------
    Monthly totals of international airline passengers, 1949 to 1960. This time series contains missing values.


    Returns
    ------
        numpy array
    

    Examples
    ------
        >>> import imputetspy
        
        >>> data = imputetspy.datasets.ts_airgap()

        >>> data

    '''
    
    
    #DATA_FILE = pkg_resources.resource_filename('imputetspy', 'data/tsAirgap.csv')
    data_path = resources.files(DATA_MODULE) /'data'/'tsAirgap.csv'

    df = pd.read_csv(data_path)
 
    return df
    
    
def ts_nh4():
    '''

    Time series of NH4 concentration in a wastewater system (with missing values)
    ------
    Time series of NH4 concentration in a wastewater system. Measured from 30.11.2010 - 16:10 to 01.01.2011 - 6:40 in 10 minute steps.
    

    Returns
    ------
        numpy array
    

    Examples
    ------
        >>> import imputetspy
        
        >>> data = imputetspy.datasets.ts_nh4()

        >>> data
    '''
    
    data_path = resources.files(DATA_MODULE) /'data'/'tsNH4.txt'
    
    df = np.loadtxt(data_path, delimiter=",", unpack=False)
 
    return df


def ts_heating():
    '''
    Time series of a heating systems supply temperature  (with missing values)
    ------
    Time series of a heating systems supply temperature. Measured from 18.11.2013 - 05:12:00 to 13.01.2015 - 15:08:00 in 1 minute steps.
    
   
    Returns
    ------
        numpy array
    

    Examples
    ------
        >>> import imputetspy
        
        >>> data = imputetspy.datasets.ts_heating()

        >>> data

    '''
    
    #DATA_FILE = pkg_resources.resource_filename('imputetspy', 'data/tsAirgap.csv')
    data_path = resources.files(DATA_MODULE) /'data'/'tsHeating.txt'

    df = np.loadtxt(data_path, delimiter=",", unpack=False)
 
    return df


