
# Big Data Fusion to Estimate Urban Fuel Consumption:
###  A case study of Riyadh

## **Purpose:**

This repo contains the code that will enable the recreation of the research conducted at MIT in 2017 pertaining to fuel consumption estimation by combining different sources of big data. The original code scripts used were split between MATLAB (or Oracle) and Python.The purpose of the published framework is to showcase and share the methods and scripts used to calibrate the model, verify its outputs, and utilize it to test policy implementations that affect fuel consumption. The current application is on the city of Riyadh, Saudi Arabia. 

Use: The Streetsmart Calibration Folder contains MATLAB/Octave code showing the calibration of the Streestmart model as well as the creation of Figure 2 of the paper. Other scripts included demonstrate the use of the code to recreate the analysis described in the paper. A summary of the data and scripts follows.

For a picture of how the code fits together, not including the calibration folder, please see the attached flowchart PDF titled ‘Flowchart.pdf’ in the main directory of the repository. 

## **Data**
It is currently zipped (at 1 Gb) but once uncmpressed it wiill reach 4.5 Gb. To recreate the figures using the data, the data folder must be downloaded and unzipped and placed in the same folder as the scripts.
It the data used in the analysis, altered to remove any sensitive data we cannot share publicly. It still contains enough of the outputs to recreate the figures of the paper.

- **flow_byEdge_time#**.csv : a CSV with flows in cars/period for the different time windows. the conversion to cars/hour occurs in the scripts. It depends on the ‘calles method’ applied to create the flows. (cite calles paper here) 
    - TimeWindows: 
        - time 1: Weekdays 8-9 AM 
        - time 2: Weekdays 5 - 6 PM 
        - time 3: Weekdays 12 - 1 PM

- **Riyadh_trips_timestamps.csv** : a list of the times that trips are initiated for the analysis of the hour by hour trips distributions in Figure 3
    - The 2 columns are
        - day: the day the trip was initiated
        - The Timestamp of the trip

- **Alltrips_Github.pkl **: a pickled output of a list of all the trips from the dataset made specifically for this repository. The original data, which came in CSV form, is a list of taxi trips made by a local Saudi Arabian ride-hail taxi service. The pickle contains the speed profiles of the trips which are used to calculate fuel consumption with the Streetsmart model. It is a list of instances of the class TP_trip filtered to remove trips not made in Riyadh and those with a GPS frequency greater than 15 s. Details on how it is produced from the original CSV data is in the python script ‘readcleansave_trips.py’ in the main directory. 
- **Riyadh_network_local.pkl **: a pickle of the street network in a graph format
- **Riyadh_streets_FC_Figure3_alltimes.pkl** : a pickle of the street network of Riyadh in a graph format with Fuel consumption for each streets/edge for all 3 time windows as an attribute. 
- **DataFrame0_1_100pc.csv** : results of the iterative traffic assignment of Origin Destination flows for time 1 (from [https://github.com/PhilChodrow/riyadh_multiplex](https://github.com/PhilChodrow/riyadh_multiplex))
- **mathcedsegemtns_byEdge_time1_8_9AM_weekdays_github.pkl** : pickled output of the map matching results reorganized into a dictionary with keys: edge of street network, values : all movement segments matched to that edge from the taxi GPS routes. 
- **mx_Riyadh_streets_TAZ_ODs_0_1.pkl **: pickle of multiplex graph with streets and Traffic Analysis Zones (TAZ) and ODs of time 1 loaded. 
- **Riyadh_streets_FC_calcualted_time1_taregeted_reduction.pkl **: pickle of Riyadh street network with FC of time 1 for each edge clacilauted and saved as an attributed. needed for Figure 6 trip fuel consumption calculation. 
- **streets_withtimes.pkl** :  pickle of Riyadh Street network with attributes of free flow times per edge
- **Trips_time1_100_github.pkl** : pickle of the dictionary of simulated trips for each OD of time 1 with FC calculated. Sample of output needed for Figure 6

## **Scripts**

Each iPython Notebook script recreates a Figure of the paper. 

- **Figure_3_Ramadan Trip creation rate.ipynb **: Shows the method used to create the average hourly rates figure showing Ramadan, Non-Ramadan, and combined taxi trips throughout 2015 and 2016 in Riyadh.
- **Figure_4_Data Verification.ipynb** : Shows the method used to create the Data Verification figures using trips in the morning peak time period of weekdays from 8 - 9 AM. (a) Histogram of Reported and calculated Trip Distances. (b) Histogram of free flow travel time and Observed travel time in matched trips. (c) Histogram of Fuel economies using constant speed, speed profiles, and 1 bin and all bins.
- **Figure_5_FC_visualization.ipynb** : Shows the method used to create the Choropleth Maps of fuel consumption rates [Liter/meter.hour] by the StreetSmart model on streets matched with GPS data for typical time periods
- **Figure_6**
- **readcleansave_trips.py** : This script takes trip GPS data as csv, cleans it and saves it as an instance of the TP_trip class
- **Fuelconsumption.py** : This script calculates fuel consumption estimates for time 1 as an example of the method. It takes as input the cleaned trips instances, Road Network graph, and map matching results and outputs the street network with fuel consumption estimates as attributes of each edge. 

## **Utility**

- **TPtrip.py** : contains functions written for the class TP_trip for the analysis of GPS points and 
- **fuel_calc.py **: contains functions to calculate trips metrics for fuel consumption calculation using the Streetsmart model. 

TP_trip class is initialized by passing the following inputs in order — reflects the data used for the experiment: required fields have an asterix * other fields can be filled with an empty string.

1. TripID* - unique trip identification number
2. User_Gender
3. CreateTime
4. PickUp_Location* - coordinates in a tuple 
5. PickUp_Time* - timestamps in date time format of start of trip
6. Dropoff_Location* - coordinates in a tuple 
7. Dropoff_Time* - timestamps in date time format of end of trip
8. Cost_Trip
9. Car_Category
10. Car_Model
11. Distance_KM* - distance traveled in [km]
12. Duration_Sec* 
13. Route_String* List of GPS points followed by car without a timestamp but evenly distributed over trip. code assumes the GPS recording frequency is stable and constant. 

To install requirements run the following command in the shell from the directory of the repository once downloaded: pip install -r requirements.txt 

tree
.
├── Creating\ Trip\ Dict.ipynb
├── Figure_3_Ramadan-Trip_rate.ipynb
├── Figure_4_Data_Verification.ipynb
├── Figure_5_FC_visualization.ipynb
├── Figure_6_Targeted_Reduction.ipynb
├── Flowchart.pdf
├── Fuelconsumption.py
├── README.md
├── Streetsmart_Calibration_\ Figure2
│   ├── Fig_2_a.m
│   ├── Fig_2_b.m
│   ├── Fig_2_c.m
│   ├── README.md
│   └── data
│       ├── FEandprofile.mat
│       ├── Fuelec2.mat
│       ├── UKandPoTRACCS2010.mat
│       ├── krange_counts.mat
│       └── vehiclesmatchedRanges.mat
├── TPtrip.py
├── TPtrip.pyc
├── data
│   ├── Alltrips_Github.pkl
│   ├── DataFrame0_1_100pc_.csv
│   ├── Riyadh_network_local.pkl
│   ├── Riyadh_streets_FC_Figure3_alltimes.pkl
│   ├── Riyadh_streets_FCcalculated_time1_targeted_reduction.pkl
│   ├── Riyadh_trips_timestamps.csv
│   ├── Trips_time1_100_github.pkl
│   ├── flow_byEdge_time1.csv
│   ├── flow_byEdge_time2.csv
│   ├── flow_byEdge_time3_midday.csv
│   ├── matchedSegmentsbyEdge_time1_8_9AM_weekdays_github.pkl
│   ├── mx_Riyadh_streets_TAZ_ODs_0_1.pkl
│   ├── riyadh_route_edges_am.txt
│   └── streets_withtimes.pkl
├── fuel_calc.py
├── fuel_calc.pyc
├── readcleansave_trips.py
├── staycode.py
├── staycode.pyc


