import numpy as np
import pandas as pd
from imputetspy.utils import check_data, consecutive, power_exp, stineman_interp, slopes
from imputetspy.datasets import ts_airgap, ts_heating, ts_nh4
from scipy import stats
from scipy.stats import gmean, hmean, mode
from scipy.interpolate import interp1d


def na_ma(data, k = 4, func='mean', 
                weighting = None, maxgap = None) :
    """ Missing value replacement by weighted moving average. Uses semi-adaptive window size to ensure all NAs are replaced    
    
    Parameters:
        data: numpy.array, list or pandas.Series
                Data to impute.
                
        k: integer width of the moving average window. Expands to both sides of the center element e.g. k=2 means 4 observations (2 left, 2 right) are taken into account. If all observations in the current window are NA, the window size is automatically increased until there are at least 2 non-NA values present.

        func : metric function, such as mean, median, mode, or any function that return single number e.g numpy.std(), numpy.max(), or custom function.

        weighting:	Weighting to be used. Accepts the following input:
                                
                                * "linear" - Linear Weighted Moving Average (LWMA)
                                
                                * "exponential" - Exponential Weighted Moving Average (EWMA)
                                
        maxgap: Maximum number of successive NAs to still perform imputation on. Default setting is to replace all NAs without restrictions. With this option set, consecutive NAs runs, that are longer than 'maxgap' will be left NA. This option mostly makes sense if you want to treat long runs of NA afterwards separately.
    Returns:
        numpy.array imputed data.
    
    Examples:
    
        >>> import imputetspy    
        >>> data = imputetspy.datasets.ts_nh4()
        >>> data_fill_ma = imputetspy.na_ma(data, 4)

    
    """
    
    if (func != 'mean') & (weighting != None) :
        raise("weighting only can be used only if func = np.mean!!!!")
    
    if func == 'mean':
        func = np.mean
    elif func == 'median':
        func = np.median
    elif func == 'mode':
        func =  stats.mode
    else:
        func = func

    x = check_data(data)
    idx = np.arange(x.shape[0])
    nan_idx = idx[np.isnan(x)]
    non_nan_idx = idx[np.isnan(x) == False]
    if maxgap != None :
        z = consecutive(nan_idx)
        exc = []
        for i in range(len(z)) :
            if len(z[i]) > maxgap :
                exc.extend(z[i])
        nan_idx = nan_idx[np.isin(nan_idx, exc) == False]
    else :
        pass
    prev_k = k//2
    inp = []
    if weighting == None :
        for i in nan_idx :
            try :
                prv = non_nan_idx[(i - non_nan_idx) > 0][-prev_k:]
            except :
                prv = []
            try :
                nxt = non_nan_idx[(non_nan_idx - i) > 0][:prev_k]
            except :
                nxt = []
            to_mv = np.append(prv, nxt)
            inp.append(func(x[to_mv]))
    elif weighting == "linear" :
        for i in nan_idx :
            try :
                prv = non_nan_idx[(i - non_nan_idx) > 0][-prev_k:]
                prv = (1/(np.arange(len(prv)) + 2)) * x[prv]
            except :
                prv = []
            try :
                nxt = non_nan_idx[(non_nan_idx - i) > 0][:prev_k]
                nxt = (1/(np.arange(len(nxt)) + 2)) * x[nxt]
            except :
                nxt = []
            to_mv = np.append(prv, nxt)
            inp.append(np.mean(to_mv))    
    elif weighting == "exponential" :
        for i in nan_idx :
            try :
                prv = non_nan_idx[(i - non_nan_idx) > 0][-prev_k:]
                prv = power_exp(len(prv)) * x[prv]
            except :
                prv = []
            try :
                nxt = non_nan_idx[(non_nan_idx - i) > 0][:prev_k]
                nxt = power_exp(len(nxt)) * x[nxt]
            except :
                nxt = []
            to_mv = np.append(prv, nxt)
            inp.append(np.mean(to_mv))
    else :
        raise('please specify correct weighting!!!!')
    x[nan_idx] = inp
    return x



def na_mean(data, option = "mean", maxgap = None) :
    """ Missing Value Imputation by overall Average values (can use median & mode as well)
        

    Parameters:

        data (float): numpy.array, list or pandas.Series data to impute.
        option (string): Algorithm to be used. Accepts these following input:  

                - "mean" - take the mean for imputation (default choice)\n
                - "median" - take the median for imputation\n
                - "mode" - take the mode for imputation\n
                - "harmonic" - take the harmonic mean\n
                - "geometric" - take the geometric mean\n    

        maxgap (int): Maximum number of successive NAs to still perform imputation on. 
                Default setting is to replace all NAs without limitation. 
                With this option set, consecutive NAs runs, that are longer than 'maxgap' will be left NA. 
                This option mostly makes sense if you want to treat long runs of NA afterwards separately.
        
    
    Returns:
        numpy array imputed data.
    
    Examples:
    
        >>> import imputetspy
        >>> data = imputetspy.datasets.ts_nh4()
        >>> data_fill_mean = imputetspy.na_mean(data, option = 'mean')
        >>> data_fill_med = imputetspy.na_mean(data, option = 'median')
    
    """
    

    x = check_data(data)
    idx = np.arange(x.shape[0])
    nan_idx = idx[np.isnan(x)]
    non_nan_idx = idx[np.isnan(x) == False]
    if maxgap != None :
        z = consecutive(nan_idx)
        exc = []
        for i in range(len(z)) :
            if len(z[i]) > maxgap :
                exc.extend(z[i])
        nan_idx = nan_idx[np.isin(nan_idx, exc) == False]
    else :
        pass
    
    if option == "mean" :
        val = np.nanmean(x)
    elif option == "median" :
        val = np.nanmedian(x)
    elif option == "harmonic" :
        val = hmean(x[np.isnan(x)])
    elif option == "geometric" :
        val = gmean(x[np.isnan(x)])
    elif option == "mode" :
        val = mode(x[np.isnan(x)])
    
    x[nan_idx] = val
    
    return x


def na_random(data, lower_bound = None, upper_bound = None, maxgap = None) :
    """ Missing Value Imputation by Random Sample
    
    Replaces each missing value by drawing a random sample between two given bounds based on uniform distribution.
    
    Parameters:
        data (float): numpy.array, list or pandas.Series data to impute.
        lower_bound (float): minimum number of the random data (lower bound of uniform distribution), if empty the parameter will be the minimum of the data.
        upper_bound (float): maximum number of the random data (upper bound of uniform distribution), if empty the parameter will be the maximum of the data.
        maxgap (int): Maximum number of successive NAs to still perform imputation on. 
                Default setting is to replace all NAs without limitation. 
                With this option set, consecutive NAs runs, that are longer than 'maxgap' will be left NA. 
                This option mostly makes sense if you want to treat long runs of NA afterwards separately.
    Returns:
        numpy.array Imputed data.
    
    Examples:

        >>> import imputetspy
        
        >>> data = imputetspy.datasets.ts_nh4()
        
        >>> data_fill_random = imputetspy.na_random(data, lower_bound = min(data_fill_random) , upper_bound = max(data_fill_random))

    
    """
    x = check_data(data)
    idx = np.arange(x.shape[0])
    nan_idx = idx[np.isnan(x)]
    
    if maxgap != None :
        z = consecutive(nan_idx)
        exc = []
        for i in range(len(z)) :
            if len(z[i]) > maxgap :
                exc.extend(z[i])
        nan_idx = nan_idx[np.isin(nan_idx, exc) == False]
    else :
        pass
    
    if lower_bound == None :
        lower_bound = np.nanmin(x)
    
    
    if upper_bound == None :
        upper_bound = np.nanmax(x)
        
    inp = []
    for i in range(len(nan_idx)) : 
        inp.append(np.random.uniform(lower_bound, upper_bound))
        
    
    x[nan_idx] = inp
    
    return x


def locf(data, na_remaining = "rev", maxgap = None):
    """ Last Observation Carried Forward
    
    For each set of missing indices, use the value of one row before(same
    column). In the case that the missing value is the first row, look one
    row ahead instead. If this next row is also NaN, look to the next row.
    Repeat until you find a row in this column that's not NaN. All the rows
    before will be filled with this value.
    
    Parameters:
        data: numpy.array, list or pandas.Series
            Data to impute.
        na_remaining : Method to be used for remaining nan (if missing number apear in the first observation) :
            "keep" - to return the series with NAs
            "mean" - to replace remaining NAs by overall mean
            "rev" - to perform nocb / locf from the reverse direction
        maxgap : Maximum number of successive NAs to still perform imputation on. Default setting is to replace all NAs without restrictions. With this option set, consecutive nan runs, that are longer than 'maxgap' will be left nan. This option mostly makes sense if you want to treat long runs of nan afterwards separately
    
    Returns:
        numpy.array imputed data.
        
    Examples:
        >>> import imputetspy
        
        >>> data = imputetspy.datasets.ts_nh4()
        
        >>> data_fill_locf = imputetspy.locf(data)
        >>> data_fill_nocb = imputetspy.nocb(data)
    
    """
    data = check_data(data)
    nan_xy = np.argwhere(np.isnan(data))
    nan_xy_idx = np.array([x[0] for x in nan_xy])
    
    if maxgap != None :
        z = consecutive(nan_xy_idx)
        exc = []
        for i in range(len(z)) :
            if len(z[i]) > maxgap :
                exc.extend(z[i])
        nan_xy_idx = nan_xy_idx[np.isin(nan_xy_idx, exc) == False]
    else :
        pass
    
    n = data.shape[0]
    n_int = np.arange(n)#[x for x in range(n)]
    
    data_cp = data.copy()
    
    for i in nan_xy_idx :
        try :
            cdd = n_int [n_int > i]
            idx_rep = np.min(cdd[np.isin(cdd, nan_xy_idx) == False])
            data_cp[i] = data_cp[idx_rep]
        except :
            if na_remaining == "rev" :
                cdd = n_int [n_int < i]
                idx_rep = np.max(cdd[np.isin(cdd, nan_xy_idx) == False])
                data_cp[i] = data_cp[idx_rep]
            elif na_remaining == "mean":
                idx_rep = np.mean(data[np.isnan(data) == False])
                data_cp[i] = idx_rep
            elif na_remaining == "keep":
                pass
            else :
                raise("the option is invalid, please fill valid option!!!!")
    return data_cp
        

def nocb(data, axis=0, na_remaining = "rev", maxgap = None):
    """ Next Observation Carried Backward

    For each set of missing indices, use the value of one row before(same
    column). In the case that the missing value is the first row, look one
    row ahead instead. If this next row is also NaN, look to the next row.
    Repeat until you find a row in this column that's not NaN. All the rows
    before will be filled with this value.

    Parameters:
        data: numpy.array, list or pandas.Series
            Data to impute.
        na_remaining : Method to be used for remaining nan (if missing number apear in the last observation) :
            "keep" - to return the series with NAs
            "mean" - to replace remaining NAs by overall mean
            "rev" - to perform nocb / locf from the reverse direction
        maxgap : Maximum number of successive NAs to still perform imputation on. Default setting is to replace all NAs without restrictions. With this option set, consecutive nan runs, that are longer than 'maxgap' will be left nan. This option mostly makes sense if you want to treat long runs of nan afterwards separately

    Returns:
        numpy.ndarray Imputed data.
    
    Examples:
        >>> import imputetspy
        
        >>> data = imputetspy.datasets.ts_nh4()
        
        >>> data_fill_locf = imputetspy.locf(data)
        >>> data_fill_nocb = imputetspy.nocb(data)
    """
    data = check_data(data)
    nan_xy = np.argwhere(np.isnan(data))
    nan_xy_idx = np.array([x[0] for x in nan_xy])
    
    if maxgap != None :
        z = consecutive(nan_xy_idx)
        exc = []
        for i in range(len(z)) :
            if len(z[i]) > maxgap :
                exc.extend(z[i])
        nan_xy_idx = nan_xy_idx[np.isin(nan_xy_idx, exc) == False]
    else :
        pass
    
    n = data.shape[0]
    n_int = np.arange(n)#[x for x in range(n)]
    
    data_cp = data.copy()
    
    for i in nan_xy_idx :
        try :
            cdd = n_int [n_int < i]
            idx_rep = np.min(cdd[np.isin(cdd, nan_xy_idx) == False])
            data_cp[i] = data_cp[idx_rep]
        except :
            if na_remaining == "rev" :
                cdd = n_int [n_int > i]
                idx_rep = np.max(cdd[np.isin(cdd, nan_xy_idx) == False])
                data_cp[i] = data_cp[idx_rep]
            elif na_remaining == "mean":
                idx_rep = np.mean(data[np.isnan(data) == False])
                data_cp[i] = idx_rep
            elif na_remaining == "keep":
                pass
            else :
                raise("the option is invalid, please fill valid option!!!!")
    return data_cp
    



def na_interpolate(data, option = "linear", maxgap = None) :
  """ Missing Value Imputation by Interpolation
  
  Uses linear, spline or stineman interpolation to replace missing values.

  
  Parameters:
    data: numpy.array, list or pandas.Series data to impute.
    option: The interpolate algorithm to be used. Accepts these following input:  
                - "linear" - use linear interpolation\n
                - "spline" - interpolation based on spline function\n
                - "stineman" - interpolation based on stineman function\n

  Returns:
    numpy.array imputed data.
  
  Examples:
    >>> import imputetspy
    
    >>> data = imputetspy.datasets.ts_nh4()
    
    >>> data_fill_lin = imputetspy.na_interpolate(data, option = 'linear')
    >>> data_fill_sp = imputetspy.na_interpolate(data, option = 'spline')

  
  """

  x = check_data(data)
  idx = np.arange(x.shape[0])
  nan_idx = idx[np.isnan(x)]
  
  if maxgap != None :
    z = consecutive(nan_idx)
    exc = []
    for i in range(len(z)) :
        if len(z[i]) > maxgap :
            exc.extend(z[i])
    nan_idx = nan_idx[np.isin(nan_idx, exc) == False]
  else :
      pass

  
  if option == "linear" :
    f = interp1d(idx[np.isin(idx, nan_idx) == False],
                x[np.isin(idx, nan_idx) == False]   )
    intrep_val = f(idx)
  elif option == "spline" :
    f = interp1d(idx[np.isin(idx, nan_idx) == False],
                x[np.isin(idx, nan_idx) == False], kind= "cubic"   )
    intrep_val = f(idx)
  elif option == "stineman" :
    intrep_val = stineman_interp(idx , idx[np.isin(idx, nan_idx) == False], 
                            x[np.isin(idx, nan_idx) == False], yp = None)
  else :
    raise print("Please fill the valid option!!!")
    
  x[nan_idx] = intrep_val[nan_idx]
  
  return x
    
    
    

