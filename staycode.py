
# coding: utf-8

# In[1]:

from scipy.interpolate import interp1d
import gzip
import collections
from collections import Counter
import numpy as np
import glob
import datetime
import timeit
import sys
import cPickle as pickle
import scipy as sc
import sys
import pandas as pd
import gc
import csv
from scipy import stats
from collections import defaultdict
from operator import itemgetter
import itertools
import networkx as nx
import matplotlib
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt
from math import radians, cos, sin, asin, sqrt
import seaborn as sns
import math
import community
import operator
from matplotlib import cm
from scipy.sparse import lil_matrix
# get_ipython().magic(u'matplotlib inline')
import igraph
from igraph import *
import folium
from folium import plugins
SAVEDATA='/home/adham/osmnx/Taxipixi'
DATAROOT='/home/adham/osmnx/Taxipixi'
orginal_Stdout=sys.stdout

# iniday=datetime.datetime(2015,1,1)
AVG_EARTH_RADIUS = 6371  # in kmA


# In[2]:

def openpickle(filename):
    start = timeit.default_timer()
    if filename[-1:]=='z':
        f=gzip.open(filename,'rb')
    else:
        f=open(filename,'r')

    cosa=pickle.load(f)
    f.close
    stop = timeit.default_timer()
    print 'APERTO file '+filename+' in time '+str(stop-start)
    sys.stdout.flush()

    return cosa


def scrivipickle(filename,cosa):
    start = timeit.default_timer()
    if filename[-1:]=='z':
        f=gzip.open(filename,'wb')
    else:
        f=open(filename,'w')
    pickle.dump(cosa,f)
    f.close
    stop = timeit.default_timer()
    print 'scritto file '+filename+' in time '+str(stop-start)
    sys.stdout.flush()

    return

def haversine(point1, point2, miles=False):
    """ Calculate the great-circle distance bewteen two points on the Earth surface.

    :input: two 2-tuples, containing the latitude and longitude of each point
    in decimal degrees.

    Example: haversine((45.7597, 4.8422), (48.8567, 2.3508))

    :output: Returns the distance bewteen the two points.
    The default unit is kilometers. Miles can be returned
    if the ``miles`` parameter is set to True.

    """
    # unpack latitude/longitude
    lat1, lng1 = point1
    lat2, lng2 = point2

    # convert all latitudes/longitudes from decimal degrees to radians
    lat1, lng1, lat2, lng2 = map(radians, (lat1, lng1, lat2, lng2))

    # calculate haversine
    lat = lat2 - lat1
    lng = lng2 - lng1
    d = sin(lat * 0.5) ** 2 + cos(lat1) * cos(lat2) * sin(lng * 0.5) ** 2
    h = 2 * AVG_EARTH_RADIUS * asin(sqrt(d))
    if miles:
        return h * 0.621371  # in miles
    else:
        return h  # in kilometers


# In[312]:

def medoid_2d(XY):
    n=len(XY)
    Dist=np.zeros([n,n])
    for i in range(len(XY)-1):
        lat1=XY[i,1]
        log1=XY[i,0]
        for j in range(i+1,n):
            lat2=XY[j,1]
            log2=XY[j,0]
            #print lat1,log1,lat2,log2
            Dist[i,j]=haversine((lat1,log1),(lat2,log2))
            Dist[j,i]=Dist[i,j]
    mean_dist=mean(Dist)
    index_min = np.argmin(mean_dist)
    return index_min




def stay(user1,par):
    flight=np.array(user1)
    maxt=len(flight)
    time=[x[0] for x in user1]
    dT=np.zeros([maxt-1,1])
    dist=np.zeros([maxt-1,1])
    record={}

    for m in range(len(par)):
        diam=par[m][0]
        diam=0.3
        dur=par[m][1]
        stay_ind=np.zeros([maxt,1])
        stays=[]
        stay_ind_list = []
        i=0
        while i<maxt-1:
            dT[i][0]=time[i+1]-time[i]
            lat1=flight[i][2]
            lat2=flight[i+1][2]
            log1=flight[i][1]
            log2=flight[i+1][1]
            dist[i][0]=haversine((lat1,log1), (lat2,log2), miles=False)
            i+=1

    i=0
    k=1

    while i<maxt-1:
        if dist[i]>diam:
            i=i+1
        else:
            start_obs=i
            end_obs=i+1
            for j in range(i+2,maxt):
                lat1=flight[i][2]
                lat2=flight[j][2]
                log1=flight[i][1]
                log2=flight[j][1]
                dist_ij=haversine((lat1,log1), (lat2,log2), miles=False)
                if dist_ij>diam:
                    end_obs=j-1
                    break
                if j==maxt:
                    end_osb=j
            d_t=flight[end_obs,0]-flight[start_obs,0]

            if d_t>=dur:
                stay_set=np.array([xs[1:3] for xs in flight[start_obs:end_obs+1]])
                stay_ind[start_obs:end_obs+1]=k

                stays.append([flight[start_obs,0],flight[end_obs,0],stay_set[medoid_2d(stay_set)]])
                stay_ind_list.append([start_obs,end_obs,stay_set[medoid_2d(stay_set)]])
                k=k+1
                i=end_obs+1
            else:
                i=i+1

    record['stays']=stays
    record['stay_ind']=stay_ind
    record['stay_ind_list']=stay_ind_list
    return record


# In[73]:

# par=np.zeros([1,2])
# par[0,0]=0.3
# par[0,1]=900


# In[320]:

# with open("KenToy_2d.txt", 'r') as my_file:
#     reader = csv.reader(my_file, delimiter=' ')
#     my_list = list(reader)
# n_list=[map(float,x) for x in my_list]
# user1=np.array(n_list)


# In[ ]:




# In[146]:

# stay_set[medoid_2d(stay_set)]


# In[ ]:




# In[321]:

# r=stay(np.array(user1),par)
# r['stays']


# In[340]:

# plt.plot(user1[:,1],user1[:,2])
# stays_p=np.array([x[2] for x in r['stays']])

# plt.scatter(stays_p[:,0],stays_p[:,1],color='r')


# In[336]:

# stays_p[:,2]


# In[ ]:

# stays(user1,par)


# user1[0]

# medoid_2d(stay_set)

# XY=stay_set

#

# record['stays']

# end_obs=j-1
# d_t=flight[end_obs,0]-flight[start_obs,0]
# stay_set=[xs[1:3] for xs in flight[start_obs:end_obs+1]]
# stay_ind[start_obs:end_obs]=k
#
# flight[end_obs,0]

# np.array(stay_set)

# record['stays']
#

# In[ ]:
