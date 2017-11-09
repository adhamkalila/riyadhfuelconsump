
## Purpose:

The Data and Scripts in this folder are for recreating the Calibration Figures in the paper

## Data Folder contains:

- **FEandprofile.mat** (MATLAB data structure)
    - FTP-75 Speed profile (Driving Schedule) data points
    - EPA Green Vehicle Guide 2017 &lt;https://www.fueleconomy.gov/feg/EPAGreenGuide/xls/all_alpha_17.xlsx Accessed February 2017&gt;

- **Fuelec2.mat**(MATLAB data structure)
    - Randomly simulated observations of Fuel Economies using the Streetsmart model for each car Mileage Bin (Buses, Tucks, and Motorcycles excluded)

- **krange_counts.mat**
    - Proportions of cars in each of the Bins as derived from crash data analysis

- **VehiclesMatchedRanges.mat**
    - Crash data Car models matched to city mean MPG from EPA Guide

- **UKandPoTRACCS2010.mat**
    - mileage data and car proportions from TRACCS &lt;[http://traccs.emisia.com/index.php](http://traccs.emisia.com/index.php)&gt; Accessed: June 2017

## Scripts Folder contains:

MATLAB (or Octave) scripts to produce:

- **Fig_2_a.m**: FTP-75 Speed profile graph Speed vs. Time
- **Fig_2_b.m**: Histogram and best fit line of Car mileages from EPA report and simulated using the Streetsmart model. 
- **Fig_2_c.m**: Histogram and best fit lines for the distributions of the fuel economies of car fleets from Riyadh, the UK , and Poland.  


