# imputeTSpy: Time series Imputation in Python

## What is it?

This package is a package for all imputation method in time series method. Most of this kind of package are available in R, however, when we use the package for interfacing python to R is somehow complicated, and need to install a lot of things as well as the performance is doesn't meet our expectation. Thefore, I decide to create this dedicated python package for time series imputation. Please visit this (link)[https://imputetspy.readthedocs.io/] for the detail of the package documentations. 


## Instalations

```
# manual installations from source
git clone https://github.com/zaenalium/imputeTSpy
cd imputeTSpy
python setup.py install
```

```

pip install imputetspy

```

## How to use this packages

### Moving Average imputation 

Fill the missing value in time series data by mean by *k* of both sides of the missing values. For example, if there is missing values in index 10, and we set k = 2, then we will calculate the mean from index 8, 9, 11, 12. This function also support weighted moving average function i.e. linear and exponential. Moreover, we can change the mean function to median or mode or any custom function.

```
import imputetspy

## load_sample dataset
df = imputetspy.datasets.ts_airgap()

## Moving average imputation
df['number_of_passengers'] = imputetspy.na_ma(df['number_of_passengers'], k = 2)

## Exponential moving average imputation
df['number_of_passengers'] = imputetspy.na_ma(df['number_of_passengers'], k = 2, weighting = 'exponential')


## moving median imputation
df['number_of_passengers'] = imputetspy.na_ma(df['number_of_passengers'], k = 2, func = 'median')


## moving custom functions imputation

def min_2(x):
    return min(x) * 2

df['number_of_passengers'] = imputetspy.na_ma(df['number_of_passengers'], k = 2, func = min_2)


```

### Random imputation 

Fill the missing value in time series data using random uniform distribution.

```
import imputetspy

## load_sample dataset
df = imputetspy.datasets.ts_airgap()

## Missing imputation using using random imputation
## With min of the data as the lower bound and the max to fill the upper bound parameter.
df['number_of_passengers'] = imputetspy.na_random(df['number_of_passengers'], 
                            lower_bound = min(df['number_of_passengers']) ,
                             upper_bound = max(df['number_of_passengers']))


```

### Interplotate imputation 

Fill the missing value in time series data using interpolation formula, there are three types of interpolation as follow:

- "linear" - use linear interpolation
- "spline" - interpolation based on spline function
- "stineman" - interpolation based on stineman function

```
import imputetspy

## load_sample dataset
df = imputetspy.datasets.ts_airgap()

## Missing data imputation using using linear interpolation
df['number_of_passengers'] = imputetspy.na_interpolate(df['number_of_passengers'], 
                            option = 'linear')

## Missing data imputation using using spline interpolation
df['number_of_passengers'] = imputetspy.na_interpolate(df['number_of_passengers'], 
                            option = 'spline')

## Missing data imputation using using stineman interpolation
df['number_of_passengers'] = imputetspy.na_interpolate(df['number_of_passengers'], 
                            option = 'stineman')

```


### Last Observation Carried Forward (LOCF) & Next Observation Carried Backward (NOCB)

**Last Observation Carried Forward** :Replaces each missing value with the last observation (before the missing value).


**Next Observation Carried Backward** : Replaces each missing value with the next observation (after the missing value).


```
import imputetspy

## load_sample dataset
df = imputetspy.datasets.ts_airgap()

## perform imputation using Last Observation Carried Forward (LOCF)
df['number_of_passengers'] = imputetspy.locf(df['number_of_passengers'])


## perform imputation using Next Observation Carried Backward (NOCB) 
df['number_of_passengers'] = imputetspy.locf(df['number_of_passengers'])

```

Please note, that there some case when using LOCF but the first obervation missing or NOCB with missing value in the last row. We can use the parameter called *na_remaining*. With the description as follow:

* "keep" - to return the series with NAs
* "mean" - to replace remaining NAs by overall mean
* "rev" - to perform nocb / locf from the reverse direction

The default of parameter is set to 'rev'.

### Overall Mean/median/mode imputation

In order to perform a mean imputation please take a look to this example.

```
import imputetspy

## load_sample dataset
df = imputetspy.datasets.ts_airgap()

## perform imputation by overall mean
df['number_of_passengers'] = imputetspy.na_mean(df['number_of_passengers'])

## perform imputation by overall mode
df['number_of_passengers'] = imputetspy.na_mean(df['number_of_passengers'], option = 'mode')

## perform imputation by overall median
df['number_of_passengers'] = imputetspy.na_mean(df['number_of_passengers'], option = 'median')


## perform imputation by overall harmonic mean
df['number_of_passengers'] = imputetspy.na_mean(df['number_of_passengers'], option = 'harmonic')

## perform imputation by overall geometric mean
df['number_of_passengers'] = imputetspy.na_mean(df['number_of_passengers'], option = 'geometric')


```

