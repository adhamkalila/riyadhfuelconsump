
import matplotlib.pyplot as plt
import csv
import pylab
pylab.rcParams['figure.figsize'] = (35.0, 8.0) #makes figure size wider

from math import radians, cos, sin, asin, sqrt
import math
import time
import scipy.io as sio
import json
from matplotlib import collections as mc
from numpy import sin, cos, arctan2, pi, sqrt
from os import listdir, path, makedirs, rmdir
import networkx as nx
from sys import stdout
import numpy as np
import cPickle as pickle
import pandas as pd
import staycode as sc
import string
import copy


def import_geojson(fileName, directory, directed=True):
    """
    function takes a geojson representaion of a network and return a NetworkX graph
    Inputs: filename and directory where geojson file is saved and boolean for directed or undrirected graph
    Outputs: Network X graph directoed or undirected.
    """

    def reverse_typify(value):
        if type(value) == list: return tuple(value)
        return value

    with open(directory+fileName, "r") as f:
        data = json.loads( f.read() )
    if directed: graph = nx.DiGraph()
    else: graph = nx.Graph()
    for feature in data['features']:
        if feature['geometry']['type'] == 'Point':
            n = feature['properties']['node_id']
            attrs = { str(key): value for key, value in feature['properties'].items() if key != 'node_id' }
            if 'pos' not in attrs: attrs['pos'] = feature['geometry']['coordinates']
            graph.add_node(reverse_typify(n), attrs)
        else:
            e1, e2 = feature['properties']['from_node'], feature['properties']['to_node']
            attrs = { key: value for key, value in feature['properties'].items() if key != 'from_node' and key != 'to_node' }
            graph.add_edge(e1, e2, attrs)
            if 'pos' not in graph.node[e1]: graph.node[e1]['pos'] = feature['geometry']['coordinates'][0]
            if 'pos' not in graph.node[e2]: graph.node[e2]['pos'] = feature['geometry']['coordinates'][-1]
    return graph

def haversine(lat1,lon1,lat2,lon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6367 * c
    return km

def segmentattributes(triptable):
    """
    Calculates distance, speed, and acceleration for the segments
    in the triptable wihtout reassigning coordinates or frequencies
    """
    for i in range(len(triptable)-1):
        if i == 0: continue
        distance = haversine(triptable[i][1][0],triptable[i][1][1],triptable[i][2][0], triptable[i][2][1]) #[km]
        speed = distance/(triptable[i][3])*3600 #[km/h]
        acceleration = (speed - triptable[i-1][5])/triptable[i][3]*10/36 #[m/s2]
        triptable[i][4:7] = [distance, speed, acceleration]

    return triptable

GPSerrors_in =[]
GPSmissing = []
SPover = []
indexerr = []
Nskip_inf = []
Route_error15 =[]

class TP_Trip(object):

    def __init__(self,TripID,User_Gender,CreateTime,PickUp_Location,PickUp_Time,Dropoff_Location,Dropoff_Time,Cost_Trip,Car_Cat,Car_Model,Distance_KM,Duration_Sec,Route_String):
        import json
        import math
        import datetime
        self.TripID = TripID
        self.User_Gender = User_Gender
        self.CreateTime = CreateTime
        self.PickUp_Location = PickUp_Location
        self.PickUp_Time = pd.to_datetime(PickUp_Time)
        self.Dropoff_Location = Dropoff_Location
        self.Dropoff_Time = pd.to_datetime(Dropoff_Time)
        self.Cost_Trip = Cost_Trip
        self.Car_Cat = Car_Cat
        self.Car_Model = Car_Model
        self.Distance_KM = Distance_KM
        self.Duration_Sec = Duration_Sec

        if Route_String[0:3] == '[{"':
            import re
            long_indexes = []
            lat_indexes = []
            Route_List = []
            for m in re.finditer('longitude', Route_String):
                long_loc = (m.start(), m.end())
                long_indexes.append(long_loc)
            for m in re.finditer('latitude', Route_String):
                lat_loc = (m.start(), m.end())
                lat_indexes.append(lat_loc)
            for i in range(len(long_indexes)):
                try:
                    coord = [float(Route_String[lat_indexes[i][1]+2:lat_indexes[i][1]+10])/1000000,float(Route_String[long_indexes[i][1]+2:long_indexes[i][1]+10])/1000000]
                    Route_List.append(coord)
                except:
                    Route_error15.append([TripID, PickUp_Time,(Route_String[lat_indexes[i][1]+2:lat_indexes[i][1]+10],Route_String[long_indexes[i][1]+2:long_indexes[i][1]+10]), long_indexes, lat_indexes])
            self.Route_List = Route_List
        else:
            try:
                self.Route_List = json.loads(Route_String)
            except NameError:
                pass
            except:
                stopper = Route_String.rfind(',[')
                Route_String = Route_String[:stopper]+']'
                self.Route_List = json.loads(Route_String)
                GPSerrors_in.append([self.TripID, self.Duration_Sec, Route_String])






        self.TripTable = []
        self.GPSfreq = float(Duration_Sec)/(len(self.Route_List)) #this is the length of the interval in sec

        for i in range(len(self.Route_List)-1):
            distance = haversine(self.Route_List[i][0],self.Route_List[i][1],self.Route_List[i+1][0], self.Route_List[i+1][1]) #[km]
            speed = distance/(self.GPSfreq)*3600 #[km/h]
            if i > 0:
                acceleration = (speed - self.TripTable[i-1][5])/self.GPSfreq*10/36 #[m/s2]
            else:
                acceleration = 0

            self.TripTable.append([i,(self.Route_List[i][0],self.Route_List[i][1]),(self.Route_List[i+1][0],self.Route_List[i+1][1]),self.GPSfreq, distance, speed, acceleration])
            # TripTable contains a list of segments with
#             0:index, 1:tuple of start coord 2: end coord, 3: GPS frequency [s],
            #  4:distance [km], 5: speed [km/h] per segment, 6: acceleration [m/s2]
        stopper = len(self.TripTable)-1

        l = 1
        while l > 0:  # Runs the speed filtering loop as many times as there are corrections
            j = 0
            stopper = len(self.TripTable)-1
            while j< stopper: # This will loop over all the segments in TripTable
                try:
                    if self.TripTable[j][5] > ss and not self.TripTable[j+1][5] > ss: # checks for scenario 1: missing point or wrong time
                        # n_skipped is an estimate of the number of missing GPS points based on the average of the speds before and after
                        n_skipped = math.floor(self.TripTable[j][5]/(np.mean([self.TripTable[j+1][5],self.TripTable[j-1][5]])))
                        n_skipped = max([2,n_skipped])
                        if n_skipped == float('inf'): # if the speeds before and after are 0, n_skipped is inf so spped is manually set to 0
                            self.TripTable[j][5] = 0.0
                            Nskip_inf.append([self.TripID,j, n_skipped])
                        else:
                            self.TripTable[j][5] = self.TripTable[j][5]/n_skipped
                            self.TripTable[j][3] = n_skipped*self.TripTable[j][3] # makes the frequency n times the unit frequency
                            GPSmissing.append([self.TripID,j, n_skipped])
                            l = l+1

                    elif self.TripTable[j][5] > ss and self.TripTable[j+1][5] > ss: #checks for scenario 2
                        SPover.append([self.TripID, j, self.TripTable[j][5]])
                        del self.TripTable[j+1]
                        stopper = stopper - 1
                        self.TripTable[j][0:3] = [j+0.5,(self.TripTable[j][1][0],self.TripTable[j][1][1]),(self.TripTable[j+1][1][0],self.TripTable[j+1][1][1])]
                        l = l+1
                except IndexError: indexerr.append([self.TripID,j]) #the error occurs because the if statement above shortens the TripTable but the counter continues up to its original length
                j = j+1
            self.TripTable = segmentattributes(self.TripTable) # Recalculates Distance, Speed and Acc after changines in the points are made by the filtering loop above
            l = l-1

    def __str__(self):
        return "Trip ID " + self.TripID + " has been saved"


def removestays(par, AllTrips_filtered):

        # call staycode and split trips
    def flatten(l):
          out = []
          for item in l:
            if isinstance(item, (list, tuple)):
              out.extend(flatten(item))
            else:
              out.append(item)
          return out


    Alltrips_staysremoved = []
    Staylog = []

    for trip in AllTrips_filtered:
        AllChildTrips = []
        user1 = []
        deltat = np.zeros([len(trip.TripTable)+1,1])
        for i in range(len(trip.TripTable)):
            deltat[i+1] = trip.TripTable[i][3] + deltat[i]
            startlat = trip.TripTable[i][1][0]
            startlon = trip.TripTable[i][1][1]
            user1.append([deltat[i],startlon,startlat])
        user1 = np.array(user1)
        STAY= sc.stay(np.array(user1),par)
        letter = string.ascii_lowercase
        a = 0
        if len(STAY['stays']) == 0 :
            Alltrips_staysremoved.append(copy.deepcopy(trip))
            continue
        # if there are stays then the trip before the first stay gets treated alone
        if len(STAY['stay_ind_list'])> 0 and STAY['stay_ind_list'][0][0] > 0:
            child_trip = copy.deepcopy(trip)
            child_trip.TripID = trip.TripID +letter[a]
            child_trip.Dropoff_Location = trip.TripTable[STAY['stay_ind_list'][0][0]]
            child_trip.Dropoff_Time = trip.PickUp_Time + datetime.timedelta(seconds=STAY['stays'][0][0][0])
            child_trip.TripTable = []
            child_trip.TripTable = trip.TripTable[:STAY['stay_ind_list'][0][0]+1]
            child_trip.Cost_Trip = trip.Cost_Trip+letter[a]
            child_trip.GPSfreq = np.mean([child_trip.TripTable[i][3] for i in range(len(child_trip.TripTable))])
            child_trip.GPSfreqnew = child_trip.GPSfreq
            child_trip.Distance_KM = np.sum([child_trip.TripTable[i][4] for i in range(len(child_trip.TripTable))])
            child_trip.Duration_Sec = np.sum([child_trip.TripTable[i][3] for i in range(len(child_trip.TripTable))])

            a = a+1
            AllChildTrips.append(copy.deepcopy(child_trip))

        # the rest of the trips are treated in the following loop
        for k in range(len(STAY['stay_ind_list'])):
            child_trip = copy.deepcopy(trip)
            child_trip.TripID = trip.TripID +letter[a]
            child_trip.PickUp_Location = trip.TripTable[STAY['stay_ind_list'][k][1]]
            child_trip.PickUp_Time = trip.PickUp_Time + datetime.timedelta(seconds=STAY['stays'][k][1][0])
            if k != len(STAY['stay_ind_list'])-1:
                child_trip.Dropoff_Location = trip.TripTable[STAY['stay_ind_list'][k+1][0]]
                child_trip.Dropoff_Time = trip.PickUp_Time + datetime.timedelta(seconds=STAY['stays'][k+1][0][0])
                child_trip.TripTable = []
                child_trip.TripTable = trip.TripTable[STAY['stay_ind_list'][k][1]:STAY['stay_ind_list'][k+1][0]+1]
            else:
                child_trip.TripTable = []
                child_trip.TripTable = trip.TripTable[STAY['stay_ind_list'][k][1]:]
            child_trip.Cost_Trip = trip.Cost_Trip+letter[a]

            child_trip.GPSfreq = np.mean([child_trip.TripTable[i][3] for i in range(len(child_trip.TripTable))])
            child_trip.GPSfreqnew = child_trip.GPSfreq
            child_trip.Distance_KM = np.sum([child_trip.TripTable[i][4] for i in range(len(child_trip.TripTable))])
            child_trip.Duration_Sec = np.sum([child_trip.TripTable[i][3] for i in range(len(child_trip.TripTable))])
            a = a+1
            Alltrips_staysremoved.append(copy.deepcopy(child_trip))
        if STAY['stay_ind_list'][0][0] == 0:
            num_children = len(STAY['stay_ind_list']) # estimate of number of child trips
        else:
            num_children = len(STAY['stay_ind_list'])+1
        Staylog.append([trip.TripID, num_children, STAY['stay_ind_list']])

        Alltrips_staysremoved2= flatten(Alltrips_staysremoved)

        return Alltrips_staysremoved2

    
    print len(Staylog),'have been cut and', len(Alltrips_staysremoved) - len(AllTrips_filtered), 'have been added'
