


import numpy as np

# input the ranges of each k for each bin of Fuel Economy From Streetsmart Calibration
k1 = [37,34.6,31.9,29.5,26.9,24.3,21.7,19,16.3,14,5, 33.5,29.5,5]

k2_ranges = [(30, 34),(23, 32),(21, 26),(17.5, 24),(15, 22),(13, 18),(12, 16),(12, 15),(11, 14),(10.5 ,12.5),(5, 14.5), (30,75), (12,27),(6,10)]

k4_ranges = [(2000, 2300),(1300, 2300),(1100, 1900),(1000, 1600),(1000, 1250),(980, 1250),(850, 1200),(750, 1050),(780, 900),(710, 900),(500, 1000), (2000,8000), (500,2200), (500,600)]

# input the percentage of each bin in the Riyadh Fleet From Streetsmart Calibration
RiyadhFleet_bybin = [0.0016624, 0.0003830, 0.0227833, 0.0440881, 0.0487076, 0.0481790, 0.0419814, 0.1098564, 0.0383885, 0.3886037, 0.1585104, 0.0416826, 0.0549435, 0.0002298]

def Fuelconsump_Riyadh(ti, tm, iadx, ivdt):
    """
    a function that takes the speed profile metrics and returns an average fuel conumption
    for every FE bin from 1 to 14
    Outputs:    ti = time idle [sec]
                tm = time moving [sec]
                iadx = integral of acceleration by distance [m^2/sec^2]
                ivdt = integral of velocity by time = distance [km]
    """

    FC_byrange = []
    for f in range(len(k1)):

    #   ranges for k values
        vary_k1 = k1[f]*10**(-5)
        vary_k2 = np.linspace(k2_ranges[f][0]*10**(-5), k2_ranges[f][1]*10**(-5), 25)
        vary_k3 = np.linspace(1*10**(-5), 4.8*10**(-5), 25)
        vary_k4 = np.linspace(k4_ranges[f][0]*10**(-5), k4_ranges[f][1]*10**(-5), 25)
        fuelvalues = []

        for y in range(25):
            for l in range(25):
                for x in range(25):
                    Fuel = ti*vary_k1 + tm*vary_k2[x] + iadx*vary_k3[l] + ivdt*vary_k4[y]
                    fuelvalues.append(Fuel)

        FC_byrange.append(np.mean(fuelvalues))
    Average_FC = 0
    for i in range(14): # calculates a weighted average fuel cosumtpon using the proportions in RiyadhFleet_bybin
        Average_FC = Average_FC + FC_byrange[i]*RiyadhFleet_bybin[i]


    return Average_FC

def Fuelconsump_Riyadhbin(ti, tm, iadx, ivdt, bin_num=range(14)):
    """
    Uses Streetsmart model to estiamte Fuel consumption
    inputs: ti[sec] (idle time), tm [sec](time moving), iadx [m2/s2](integral of acc dx), ivdt [km](integral of velocity dt or sum of distance moving)
        bin_num: list of all bins to be considered. pass a single bin to be considered or range(14) for all bins.

    returns: mean fuel consumption [US Gallon], assuming gaussian dbn (if bin_num is range(14))
            OR simple mean of one bin if one bin_num is one bin
    """
    if len(bin_num) == 14: Riyadh_weighted = True
    else: Riyadh_weighted = False

    FC_byrange = {}
    for b in bin_num:
    #   ranges for k values
        vary_k1 = k1[b]*10**(-5)
        vary_k2 = np.linspace(k2_ranges[b][0]*10**(-5), k2_ranges[b][1]*10**(-5), 25)
        vary_k3 = np.linspace(1*10**(-5), 4.8*10**(-5), 25)
        vary_k4 = np.linspace(k4_ranges[b][0]*10**(-5), k4_ranges[b][1]*10**(-5), 25)
        fuelvalues = []

        for y in range(25):
            for l in range(25):
                for x in range(25):
                    Fuel = ti*vary_k1 + tm*vary_k2[x] + iadx*vary_k3[l] + ivdt*vary_k4[y]
                    fuelvalues.append(Fuel)

        FC_byrange[b] = np.mean(fuelvalues)
    Average_FC = 0
    if Riyadh_weighted:
        for b in FC_byrange: # calculates a weighted average fuel cosumtpon using the proportions in RiyadhFleet_bybin
            Average_FC = Average_FC + FC_byrange[b]*RiyadhFleet_bybin[b]
    else:
        Average_FC = FC_byrange[b]


    return Average_FC


def computemetrics(segments, tripid):
    """
    Computing metrics of a given set of Triptable entries:
    function that takes list of triptable segments and returns metrics
    """

    ti = 0
    tm = 0
    ivdt = 0
    iadx=0
    index = tripids[tripid]
    for seg in segments:
        table_i = GPSi_2_TripTablei[tripid][seg[0]]
        time = seg[3]
        simple_dist = seg[4]
        speed = seg[5]
        acc = seg[6]
        if speed == 0: ti = ti + time
        else: tm = tm + time
        ivdt = ivdt + simple_dist
        #calculates avg_dist covered around a single GPS point as the average of the distances of the segements including that point.
        avg_dist = 0.5*(simple_dist+Alltrips_staysremoved[index].TripTable[table_i-1][4])*1000 # converts from km to m
        iadx = iadx + abs(acc*avg_dist)
    return [ti,tm,iadx,ivdt]
