 # Purpose: this script will calculate Fuel consumption Estimates for one time window
 # Input:
#     - cleaned Alltrips file with TP_trip instances
#     - Road_network_local
#     - Example segments_byEdge (code to recreate it is commented out below)
# Output:
#     - Riyadh_streets_FCcalculated ( pickle of streets network json with attribute FC for each edge)



import datetime
from TPtrip import *
from fuel_calc import *
import cPickle as pickle
import json
import numpy as np

 # Time window for the analysis: 8 - 9 AM
timeWindow = [8,9] # in GMT timezone
time1 = True; time2 = False; time3= False
starttime = datetime.time(timeWindow[0]-3,0,0) # 3 hours subtracted since Ryadh time is GMT + 3
endtime = datetime.time(timeWindow[1]-3,0,0)
weekdays = [1,2,3,4,7] # weekdays in isoweekday datetime format. Weekdays in Saudi are Sunday to Thursday inclusive


##############################################################################


# Load the All trips filtered pickle to extract the appropriate TripTable entries

Alltrips_staysremoved = pickle.load( open( "data/Alltrips_Github.pkl", "rb" ) )

# Load Empty Streets network to save fuel consumption estimates to it for every edge

streets =  pickle.load( open( "data/Riyadh_network_local.pkl", "rb" ) )
print 'loaded empty streets network'

# Create a an empty list for FC_Estimate in each edge's dict
for e1, e2 in streets.edges():
    streets.edge[e1][e2]['FC_Estimate_time1'] = []
    streets.edge[e1][e2]['FC_Estimate_time2'] = []
    streets.edge[e1][e2]['FC_Estimate_time3'] = []

# Create a dict with keys the tripID and the values another dic with keys the GPS index and value the triptable list index
# This is mainly for the trips that have been split around stays (~1400 trips) which have TripTable indices different from GPS indices
GPSi_2_TripTablei = {}
for i in range(len(Alltrips_staysremoved)):
    GPSi_2_TripTablei[Alltrips_staysremoved[i].TripID] = {}
    for u in range(len(Alltrips_staysremoved[i].TripTable)):
        GPS_index = Alltrips_staysremoved[i].TripTable[u][0]
        GPSi_2_TripTablei[Alltrips_staysremoved[i].TripID][GPS_index] = u

# Build a dict between edge nodes and GID:
gid_2_edge = {}
for n1,n2 in streets.edges():

    gid_2_edge[streets[n1][n2]['gid']] = (n1, n2)

# The next block will read in the map matched points in json format and create a dict of matched gps points under the edge they were matched to
# it is commented out since it requires the use of data protected under an NDA. instead, a sterlized pickle of the result is loaded in

"""
# Loads Road network for interpreting matching results
directory = '...'
ZeyadGr = import_geojson("Road Network.geojson", directory)

# build a dictionary of tripID to index for the list Alltrips_staysremoved

tripids = {}
for i in range(len(Alltrips_staysremoved)):

    tripids[Alltrips_staysremoved[i].TripID]=i

# produce dict of mathced trips by Trip ID
months = ['2015_august.json', '2015_december.json', '2015_july.json', '2015_june.json', '2015_may.json', '2015_november.json', '2015_october.json', '2015_september.json', '2016_april.json', '2016_august.json', '2016_december.json', '2016_february.json', '2016_january.json', '2016_july.json', '2016_june.json', '2016_march.json', '2016_may.json', '2016_november.json', '2016_october.json', '2016_september.json']
directory = "Matched segments/"
t = time.time()
matchedtrips = {}
for month in months:
    with open( directory + month, 'r') as f:
            edges = json.loads( f.read() )
    for edge in edges:
        e1,e2 = eval(edge)
        for p in edges[edge]:
            if (p['speed']) > 160: continue    # upper ceiling of allowed speeds in km/h
            gidedge = ZeyadGr.edge[e1][e2]['gid']
            pickup = pd.to_datetime(p['time']['pickup'])
            if not (pickup.isoweekday() in weekdays): continue  # checks if segment is in weekdays as defined above (iso)
            if not (starttime <= pickup.time() <= endtime): continue # checks if segment is in desired time window
            p['gid']= gidedge
            if p['TripID'] in matchedtrips:
                matchedtrips[p['TripID']].append(p)
            else:
                matchedtrips[p['TripID']] = [p]
elapsed = time.time() - t
print 'matchedtrips Performed in', elapsed/60, 'min'

# loop over matchedtrips and for every GID, and new trip, add the appropraite TripTable entries to a new dict, Segmentsbyegde
segments_byEdge = {}
Trip_repeat = []
t = time.time()
for key in matchedtrips:
    tripdf = pd.DataFrame(matchedtrips[key])
    tripdf_sum = pd.DataFrame(tripdf.groupby(['TripID', 'gid']).describe()) # produces a df with min and max values for each attripbute, including GPS index

    for row in range(len(tripdf_sum)):
        gid = tripdf_sum.index.get_level_values('gid')[row]
        tripid = tripdf_sum.index.get_level_values('TripID')[row]
        class_index = tripids[tripid]
        start_gpsi = int(tripdf_sum.iloc[row][3]) # the triptable index for the first segment
        end_gpsi = int(tripdf_sum.iloc[row][7] +1) # triptable index for the last segment
        if not gid in segments_byEdge:

            segments_byEdge[gid] = {tripid: [Alltrips_staysremoved[class_index].TripTable[start_gpsi:end_gpsi]]}
        else:
            if tripid in segments_byEdge[gid]:
                Trip_repeat.append([tripid,gid])
                continue
            segments_byEdge[gid][tripid] = [Alltrips_staysremoved[class_index].TripTable[start_gpsi:end_gpsi]]

elapsed = time.time() - t
print 'Segments_byEdge Dict Performed in', elapsed/60, 'min'

"""

with open('data/matchedSegmentsbyEdge_time1_8_9AM_weekdays_github.pkl', 'rb') as f:
    segments_byEdge = pickle.load(f)

t = time.time()
for gid, trips in segments_byEdge.iteritems():
    e1 = gid_2_edge[gid][0]
    e2 = gid_2_edge[gid][1]
    for tripid, segments in trips.iteritems():
        ti = 0; tm = 0; iadx = 0;ivdt = 0
        ti, tm, iadx, ivdt = computemetrics(segments, tripid)
        # Append the FC Estimate to the edge in streets network
        if time1: streets[e1][e2]['FC_Estimate_time1'].append(Fuelconsump_Riyadh(ti, tm, iadx, ivdt))
        elif time2: streets[e1][e2]['FC_Estimate_time2'].append(Fuelconsump_Riyadh(ti, tm, iadx, ivdt))
        elif time3: streets[e1][e2]['FC_Estimate_time3'].append(Fuelconsump_Riyadh(ti, tm, iadx, ivdt))
    if time1: streets[e1][e2]['FC_avg_time1'] = np.mean(streets[e1][e2]['FC_Estimate_time1'])
    elif time2: streets[e1][e2]['FC_avg_time2'] = np.mean(streets[e1][e2]['FC_Estimate_time2'])
    elif time3: streets[e1][e2]['FC_avg_time3'] = np.mean(streets[e1][e2]['FC_Estimate_time3'])
elapsed = time.time() - t
print 'FC Estimates Performed in', elapsed/60, 'min'

with open('Riyadh_streets_FCcalculated.pkl', 'wb') as output:
    pickle.dump(streets, output, -1)
