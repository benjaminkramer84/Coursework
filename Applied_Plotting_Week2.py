# # Assignment 2 - Data 
# 
# Before working on this assignment please read these instructions fully. In the submission area, you will notice that you can click the link to **Preview the Grading** for each step of the assignment. This is the criteria that will be used for peer grading. Please familiarize yourself with the criteria before beginning the assignment.
# 
# An NOAA dataset has been stored in the file `data/C2A2_data/BinnedCsvs_d400/fb441e62df2d58994928907a91895ec62c2c42e6cd075c2700843b89.csv`. This is the dataset to use for this assignment. Note: The data for this assignment comes from a subset of The National Centers for Environmental Information (NCEI) [Daily Global Historical Climatology Network](https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/readme.txt) (GHCN-Daily). The GHCN-Daily is comprised of daily climate records from thousands of land surface stations across the globe.
# 
# Each row in the assignment datafile corresponds to a single observation.
# 
# The following variables are provided to you:
# 
# * **id** : station identification code
# * **date** : date in YYYY-MM-DD format (e.g. 2012-01-24 = January 24, 2012)
# * **element** : indicator of element type
#     * TMAX : Maximum temperature (tenths of degrees C)
#     * TMIN : Minimum temperature (tenths of degrees C)
# * **value** : data value for element (tenths of degrees C)
# 
# For this assignment, you must:
# 
# 1. Read the documentation and familiarize yourself with the dataset, then write some python code which returns a line graph of the record high and record low temperatures by day of the year over the period 2005-2014. The area between the record high and record low temperatures for each day should be shaded.
# 2. Overlay a scatter of the 2015 data for any points (highs and lows) for which the ten year record (2005-2014) record high or record low was broken in 2015.
# 3. Watch out for leap days (i.e. February 29th), it is reasonable to remove these points from the dataset for the purpose of this visualization.
# 4. Make the visual nice! Leverage principles from the first module in this course when developing your solution. Consider issues such as legends, labels, and chart junk.
# 
# The data you have been given is near **Ann Arbor, Michigan, United States**, and the stations the data comes from are shown on the map below.

# In[92]:

import matplotlib.pyplot as plt
import mplleaflet
import pandas as pd

def leaflet_plot_stations(binsize, hashid):

    df = pd.read_csv('data/C2A2_data/BinSize_d{}.csv'.format(binsize))

    station_locations_by_hash = df[df['hash'] == hashid]

    lons = station_locations_by_hash['LONGITUDE'].tolist()
    lats = station_locations_by_hash['LATITUDE'].tolist()

    plt.figure(figsize=(8,8))

    plt.scatter(lons, lats, c='r', alpha=0.7, s=200)

    return mplleaflet.display()

leaflet_plot_stations(400,'fb441e62df2d58994928907a91895ec62c2c42e6cd075c2700843b89')


# In[101]:

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
get_ipython().magic('matplotlib notebook')


data_raw = pd.read_csv('data/C2A2_data/BinnedCsvs_d400/fb441e62df2d58994928907a91895ec62c2c42e6cd075c2700843b89.csv')
data_raw['Date'] = pd.to_datetime(data_raw['Date'])


data_clean = data_raw[~((data_raw.Date.dt.month == 2) & (data_raw.Date.dt.day == 29))].copy() #Remove Leap Days
data_clean['Month_Day'] = data_clean['Date'].dt.strftime('%m-%d') #Create a month-day column to group by

data_clean['Data_Value'] = data_clean['Data_Value']/10 #Temps are in tenths of a percent

data_clean_pre2014=data_clean[data_clean['Date']<='2014-12-31'] #Remove 2015

data_max = data_clean_pre2014[data_clean_pre2014.Element == 'TMAX' ] #df for Maxes
data_min = data_clean_pre2014[data_clean_pre2014.Element == 'TMIN' ] #df for Mins

#Group by Day of Year, take max/min
record_highs = data_max.groupby(by = ['Month_Day'])['Data_Value'].max().rename('Temp_High') 
record_lows = data_min.groupby(by = ['Month_Day'])['Data_Value'].min().rename('Temp_Low')

## 2015 Comparison
data_max_w2015 = data_clean[data_clean.Element == 'TMAX' ]
data_min_w2015 = data_clean[data_clean.Element == 'TMIN' ]


record_highs_w2015 = data_max_w2015.groupby(by = ['Month_Day'])['Data_Value'].max().rename('Temp_High_2015')
record_lows_w2015 = data_min_w2015.groupby(by = ['Month_Day'])['Data_Value'].min().rename('Temp_Low_2015')


comparison_2015_max = pd.concat([record_highs_w2015, record_highs] , axis = 1)
comparison_2015_min = pd.concat([record_lows_w2015, record_lows] , axis = 1)

highs_2015 = (pd.DataFrame(comparison_2015_max[comparison_2015_max.Temp_High_2015 
                    > comparison_2015_max.Temp_High]['Temp_High_2015']).reset_index())
lows_2015 = (pd.DataFrame(comparison_2015_min[comparison_2015_min.Temp_Low_2015 
                    < comparison_2015_min.Temp_Low]['Temp_Low_2015']).reset_index())


x_values = np.arange(1,366)
x_ticks = []
x_ticks_values = []
dates = np.arange('2017-01-01', '2018-01-01', dtype='datetime64[M]')
for date in dates:
    t= pd.to_datetime(str(date))
    x_ticks.append(t.strftime('%b'))
    x_ticks_values.append(int(t.strftime('%j')))
  
    
##Setting Up and Cleaining Plot
fig, ax = plt.subplots()
right_side = ax.spines["right"]
right_side.set_visible(False)
top_side = ax.spines["top"]
top_side.set_visible(False)

axes = plt.gca()
axes.set_ylim([-50,50])
axes.set_xlim([1,366])

axes.set_xlabel('Month')
axes.set_ylabel('Temperature (C)')
axes.set_title('Ann Arbor Temperature Record Highs and Lows (2005-2014)')


#Plot 2005-2014 maxes and mins
plt.plot(x_values, record_highs, zorder = 1)
plt.plot(x_values, record_lows, zorder = 1)
plt.gca().fill_between(range(len(record_highs)), 
                       record_lows, record_highs, 
                       facecolor='gray', 
                       alpha=0.25, label='_nolegend_')
plt.xticks(x_ticks_values, x_ticks)

x_axis = plt.gca().xaxis

for item in x_axis.get_ticklabels():
    item.set_rotation(45)
    
##Plot Record Breaking Temps for 2015
highs_2015['Day']= pd.to_datetime('2015-' + highs_2015['Month_Day']).dt.strftime('%j').astype('int')
highs_2015.head()
plt.scatter(highs_2015['Day'], highs_2015['Temp_High_2015'], s = 5, c = '#000080', zorder = 2)

lows_2015['Day']= pd.to_datetime('2015-' + lows_2015['Month_Day']).dt.strftime('%j').astype('int')
highs_2015.head()
plt.scatter(lows_2015['Day'], lows_2015['Temp_Low_2015'], s = 5, c = '#813F0B', zorder = 2)

legend_labels = ['Record Highs', 'Record Lows', '2015 Record Breaking Highs', '2015 Record Breaking Lows']
plt.legend(legend_labels, frameon = False, loc = 4)






# In[ ]:



