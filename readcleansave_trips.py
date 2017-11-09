# Purpose: This script takes trip GPS data as csv, cleans it, and saves it as an instance
# of the TP_trip class

# ## This script will run the cleaning code on all GPS data.
# it will filter for:
# - GPS frequency that is consistent with the month's average (5 or 10s)
fr = 15 # max frequency
# - GPS points that are missing or in the wrong location
# - Riyadh trips only (not Jeddah)
# - speeds above a threshold ss
ss = 160 # cutoff speed above which a point is considered an error[km/h]


from TPtrip import *

import pandas as pd
import numpy as np
import csv
import pylab
import datetime
from math import radians, cos, sin, asin, sqrt
import math
import time
import scipy.io as sio
import cPickle as pickle


# loop through all the taxixpixi months and save each line as an instance of the class TP_Trip

taxi = ['january2016.csv']
t = time.time()
AllTrips = []

for month in taxi:
    tt = open(month, 'rU')
    df = csv.reader(tt)
    next(df)

    for trip in df: # loop through every line/trip and record it as a TP_Trip instance
        # change the line below to check if trip[15] is empty or does not exist. example can be found in july2016, 9, 10, 11 rows
        if not trip[15] or trip[12] == '0': continue # skips trips with 0 duration or Route GPS points


        onetrip = [TP_Trip(trip[0], trip[1], trip[2], trip[3], trip[4],
                           trip[5], trip[6], trip[7],trip[9], trip[10],
                           trip[11], trip[12], trip[15])]

        AllTrips.append(onetrip)

    tt.close()


elapsed = time.time() - t
print 'saved', len(AllTrips), 'trips in', int(elapsed), 'seconds'

# filter out trips with a low frequency and those in Jeddah (longitude is 39)

AllTrips_filtered = []
for i in range(len(AllTrips)):
    if (0 < augusttrips[i][0].GPSfreq < fr) and augusttrips[i][0].Route_List[0][1]>40:
        AllTrips_filtered.append(AllTrips[i][0]) # this also removes the list of lists to make it a list of TP_trip instances directly

# parameters for identification of stay. Minimum radius and duration of a stay
par=np.zeros([1,2])
par[0,0]=0.01 # [km]
par[0,1]=2200 # [sec]

Alltrips_staysremoved = removestays(par, AllTrips_filtered)

with open('Alltrips_staysremoved.pkl', 'wb') as output:
    pickle.dump(Alltrips_staysremoved, output, -1)
