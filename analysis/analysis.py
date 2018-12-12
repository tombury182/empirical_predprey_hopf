#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 27 12:19:21 2018

@author: Thomas Bury

Analysis of chemostat data from Fussmann et al.

"""

# import python libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# import EWS function
import sys
sys.path.append('../../early_warnings')
from ews_compute import ews_compute




#-----------------------
# Parameters
#–-----------------------

# EWS computation parmaeters
band_width = 0.1 # band width of Gaussian smoothing
ham_length = 40 # length of Hamming window
ham_offset = 0.5 # offset of Hamming windows
w_cutoff = 1 # cutoff of higher frequencies
ews = ['var','ac','smax','aic','aic_params','cf','cv'] # EWS to compute
lag_times = [1,2] # lag times for autocorrelation computation



#------------------
## Data curation
#-------------------

# import data
raw = pd.read_excel('../data/raw_fussmann_2000.xls',header=[1])

# round delta column to 2d.p
raw['meandelta'] = raw['meandelta'].apply(lambda x: round(x,2))

# rename delta column
raw.rename(columns={'meandelta':'Delta'}, inplace=True)

## shift day# to start at 0
# function to take list and subtract minimum element
def zero_shift(array):
    return array-min(array)

# unique delta values
deltaVals = raw['Delta'].unique()

# loop through delta values
for d in deltaVals: 
    # shift time values to start at 0
    raw.loc[ raw['Delta']==d,'day#'] = zero_shift(
            raw.loc[ raw['Delta']==d,'day#']) 


## index dataframe by Delta and day#
raw.set_index(['Delta','day#'], inplace=True)            

# compute number of data points for each value of delta
series_lengths=pd.Series(index=deltaVals)
series_lengths.index.name= 'Delta'
for d in deltaVals:
    series_lengths.loc[d] = len(raw.loc[d])
    
# only keep delta values with over 40 data points (so power spec can be computed)
deltaValsFilt = series_lengths[ series_lengths > 40 ].index

               
               
#–--------------------          
## Plot of all trajctories
#-----------------------

# Plot all Chlorella trajectories
raw['Chlorella'].unstack(level=0).plot(
        title = 'Chlorella trajectories')

# Plot all Brachionus trajectories
raw['Brachionus'].unstack(level=0).plot(
        title = 'Brachionus trajectories')


#--------------------------
# Compute EWS
#------------------------

## Chlorella EWS
print('\nChlorella')

# Set up a list to store output dataframes for each delta
appended_ews = []
appended_pspec = []

# Loop through delta values
for d in deltaValsFilt:
    series = raw.loc[d,'Chlorella']
    # plug series into ews_compute - no rolling window (rw=1)
    ews_dic = ews_compute(series,
                         roll_window = 1,
                         smooth = True,
                         band_width = band_width,
                         ews = ews,
                         lag_times = lag_times,
                         ham_length = ham_length,
                         ham_offset = ham_offset,
                         w_cutoff = w_cutoff
                         )
    # DataFrame of EWS metrics
    df_ews_temp = ews_dic['EWS metrics']
    # DataFrame for power spectra and their fits
    df_pspec_temp = ews_dic['Power spectrum']
    
    # Include a column for delta value in each DataFrame
    df_ews_temp['Delta'] = d*np.ones(len(df_ews_temp))
    df_pspec_temp['Delta'] = d*np.ones(len(df_pspec_temp))
    
    # add DataFrame to list
    appended_ews.append(df_ews_temp)
    appended_pspec.append(df_pspec_temp)
    
    # Print complete    
    print('Delta = '+str(d)+' complete.')
    
# concatenate DataFrames - use delta value and time as indices
df_ews_chlor = pd.concat(appended_ews).set_index('Delta',append=True).reorder_levels([1,0])
df_pspec_chlor = pd.concat(appended_pspec).set_index('Delta',append=True).reorder_levels([2,0,1])


## Brachionus EWS

print('\nBrachionus')

# Set up a list to store output dataframes for each delta
appended_ews = []
appended_pspec = []

# Loop through delta values
for d in deltaValsFilt:
    series = raw.loc[d,'Brachionus']
    # plug series into ews_compute - no rolling window (rw=1)
    ews_dic = ews_compute(series,
                         roll_window = 1,
                         smooth = True,
                         band_width = band_width,
                         ews = ews,
                         lag_times = lag_times,
                         ham_length = ham_length,
                         ham_offset = ham_offset,
                         w_cutoff = w_cutoff
                         )
    # DataFrame of EWS metrics
    df_ews_temp = ews_dic['EWS metrics']
    # DataFrame for power spectra and their fits
    df_pspec_temp = ews_dic['Power spectrum']
    
    # Include a column for delta value in each DataFrame
    df_ews_temp['Delta'] = d*np.ones(len(df_ews_temp))
    df_pspec_temp['Delta'] = d*np.ones(len(df_pspec_temp))
    
    # add DataFrame to list
    appended_ews.append(df_ews_temp)
    appended_pspec.append(df_pspec_temp)
    
    # Print complete    
    print('Delta = '+str(d)+' complete.')
    
# concatenate DataFrames - use delta value and time as indices
df_ews_brach = pd.concat(appended_ews).set_index('Delta',append=True).reorder_levels([1,0])
df_pspec_brach = pd.concat(appended_pspec).set_index('Delta',append=True).reorder_levels([2,0,1])


# Check data smoothing looks ok
df_ews_chlor.loc[1.37,['State variable','Smoothing']].plot(title='Early warning signals')


## Reduce EWS dataframes by getting rid of NaN cells and dropping the Time index
df_ews_chlor = df_ews_chlor.dropna().reset_index(level=1, drop=True)
df_ews_brach = df_ews_brach.dropna().reset_index(level=1, drop=True)
    
df_pspec_chlor = df_pspec_chlor.reset_index(level=1, drop=True)
df_pspec_brach = df_pspec_brach.reset_index(level=1,)







#----------------
## Plots of EWS against delta value
#----------------
        


# Plot of EWS metrics
fig1, axes = plt.subplots(nrows=5, ncols=1, sharex=True, figsize=(6,6))
df_ews_chlor[['Variance']].plot(ax=axes[0],title='Early warning signals')
df_ews_brach[['Variance']].plot(ax=axes[0],secondary_y=True)
df_ews_chlor[['Coefficient of variation']].plot(ax=axes[1])
df_ews_brach[['Coefficient of variation']].plot(ax=axes[1],secondary_y=True)
df_ews_chlor[['Lag-1 AC']].plot(ax=axes[2])
df_ews_brach[['Lag-1 AC']].plot(ax=axes[2],secondary_y=True)
df_ews_chlor[['Smax']].plot(ax=axes[3])
df_ews_brach[['Smax']].plot(ax=axes[3],secondary_y=True)
df_ews_chlor[['AIC hopf']].plot(ax=axes[4])
df_ews_brach[['AIC hopf']].plot(ax=axes[4],secondary_y=True)





#---------------------------------
## Power spectra visualisation
#--------------------------------


## Chlorella grid plot
#plt.rc('text', usetex=True)
g = sns.FacetGrid(df_pspec_chlor.reset_index(level=['Delta','Frequency']), 
                  col='Delta',
                  col_wrap=3,
                  sharey=False,
                  aspect=1.5,
                  size=1.8
                  )
# Plots
plt.rc('axes', titlesize=10) 
g.map(plt.plot, 'Frequency', 'Empirical', color='k', linewidth=1)
g.map(plt.plot, 'Frequency', 'Fit fold', color='b', linestyle='dashed', linewidth=1)
g.map(plt.plot, 'Frequency', 'Fit hopf', color='r', linestyle='dashed', linewidth=1)
g.map(plt.plot, 'Frequency', 'Fit null', color='g', linestyle='dashed', linewidth=1)
# Axes properties
axes = g.axes
# Y labels
for ax in axes[::3]:
    ax.set_ylabel('Power')
# Y limits
for i in range(len(axes)):
    ax=axes[i]
    d=deltaValsFilt[i]
    ax.set_ylim(bottom=0, top=1.1*max(df_pspec_chlor.loc[d]['Empirical']))
    ax.set_xlim(left=-2.5, right=2.5)
    ax.set_title('Delta = %.2f' % deltaValsFilt[i])
    
# Assign to plot label
pspec_plot_chlor=g

df_ews_chlor.loc[d]['AIC fold']



## Brachionus grid plot
g = sns.FacetGrid(df_pspec_brach.reset_index(level=['Delta','Frequency']), 
                  col='Delta',
                  col_wrap=3,
                  sharey=False,
                  aspect=1.5,
                  size=1.8
                  )
# Plots
plt.rc('axes', titlesize=10) 
g.map(plt.plot, 'Frequency', 'Empirical', color='k', linewidth=1)
g.map(plt.plot, 'Frequency', 'Fit fold', color='b', linestyle='dashed', linewidth=1)
g.map(plt.plot, 'Frequency', 'Fit hopf', color='r', linestyle='dashed', linewidth=1)
g.map(plt.plot, 'Frequency', 'Fit null', color='g', linestyle='dashed', linewidth=1)
# Axes properties
axes = g.axes
# Y labels
for ax in axes[::3]:
    ax.set_ylabel('Power')
# Y limits
for i in range(len(axes)):
    ax=axes[i]
    ax.set_ylim(bottom=0, top=1.1*max(df_pspec_brach.loc[deltaValsFilt[i]]['Empirical']))
    ax.set_xlim(left=-2.5, right=2.5)
    ax.set_title('Delta = %.2f' % deltaValsFilt[i])
# Assign to plot label
pspec_plot_brach=g




#-----------------------
# Export data and plots
#-----------------------
    

# Export pspec plots
pspec_plot_chlor.savefig("../figures/pspec_grid_chlor.png", dpi=200)
pspec_plot_brach.savefig("../figures/pspec_grid_brach.png", dpi=200)

# Export EWS data for plotting in MMA
cols=['Variance','Coefficient of variation','Lag-1 AC','Lag-2 AC','Smax','AIC fold','AIC hopf','AIC null']
df_ews_chlor[cols].to_csv("../data_export/ews_chlor.csv")
df_ews_brach[cols].to_csv("../data_export/ews_brach.csv")





