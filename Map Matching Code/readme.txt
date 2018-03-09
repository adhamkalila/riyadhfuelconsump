The script in this folder is designed to read two types of files:
    1. A json file in a custom format used to describe a road network (in the root folder)
    2. A set of files containing GPS trajectories (in the Trips folder)
And then process the GPS trajectories to match them to routes in the road network.

The script requires updating the 'directory' variable to the path of this folder.
The 'filenames' variable contains the names of GPS trajectory files that the software will attempt to map.

To run the software, please follow the example code given at the end of the script. 
The steps essentially consist of: 
    1. Reading the road network into a graph, cleaning it and segmenting it
    2. Looping through the files specified by the 'filenames' variable'
    3. For each file, attempting to map the trajectories to the graph.
       The total processing time and number of mapped trajectories are printed after each file.
    4. Saving the results to a file in the Results folder with the same name as the input from the Trips folder

The GPS trajectory files are expected to be structured according to these requirements:
    1. Each row of the file is a JSON object defining a single GPS trajectory
       This allows the software to read the file line-by-line and avoid loading the entire file at once.
    2. The JSON object defining each GPS trajectory is structured as follows:
            { tripID: [ segment1, segment2, .... ] }
        Where each segment is a dictionary representing one interval of the GPS trajectory. For example:
            {
                "distance": 0.15381657426513887,                        #The Euclidean distance (in km) traversed in this GPS segment
                "speed": 0.015381657426513887,                          #The average speed in this GPS segment (distance/period)
                "start": [46.69877253279598, 24.747029574310872],       #The GPS coordinates at the start of the interval
                "end": [46.69749177912585, 24.746280813815133],         #The GPS coordinates at the end of the interval
                "Pickup Time": "2016-1-7T11:0:48+00:00",                #The time at the start of the GPS trajectory
                "period": 10.0,                                         #The average interval between subsequent GPS points 
                "time": 10.0                                            #The overall time (in s) traversed so far
            }
