p.p1 {margin: 0.0px 0.0px 0.0px 0.0px; font: 12.0px Helvetica}
p.p2 {margin: 0.0px 0.0px 0.0px 0.0px; font: 12.0px Helvetica; min-height: 14.0px}
p.p3 {margin: 0.0px 0.0px 0.0px 0.0px; font: 14.0px Helvetica}
li.li1 {margin: 0.0px 0.0px 0.0px 0.0px; font: 12.0px Helvetica}
li.li4 {margin: 0.0px 0.0px 0.0px 0.0px; font: 12.0px 'Helvetica Neue'; color: #000000}
li.li5 {margin: 0.0px 0.0px 0.0px 0.0px; font: 12.0px 'Helvetica Neue'; color: #000000; background-color: #ffffff}
span.s1 {text-decoration: underline}
span.s2 {font: 12.0px Helvetica; color: #000000}
span.s3 {font-kerning: none; background-color: #ffffff}
span.s4 {font-kerning: none}
span.s5 {background-color: #ffffff}
span.s6 {font: 12.0px 'PingFang SC'}
ol.ol1 {list-style-type: decimal}
ul.ul1 {list-style-type: disc}
ul.ul2 {list-style-type: hyphen}


## Purpose:

The Data and Scripts in this folder are for recreating the Calibration Figures in the paper

## Data Folder contains:

- FEandprofile.mat (MATLAB data structure)
    - FTP-75 Speed profile (Driving Schedule) data points
    - EPA Green Vehicle Guide 2017 &lt;https://www.fueleconomy.gov/feg/EPAGreenGuide/xls/all_alpha_17.xlsx Accessed February 2017&gt;

- **Fuelec2.mat **(MATLAB data structure)
    - Randomly simulated observations of Fuel Economies using the Streetsmart model for each car Mileage Bin (Buses, Tucks, and Motorcycles excluded)

- **krange_counts.mat **
    - Proportions of cars in each of the Bins as derived from crash data analysis

- **VehiclesMatchedRanges.mat **
    - Crash data Car models matched to city mean MPG from EPA Guide

- **UKandPoTRACCS2010.mat**
    - mileage data and car proportions from TRACCS &lt;[http://traccs.emisia.com/index.php](http://traccs.emisia.com/index.php)&gt; Accessed: June 2017

## Scripts Folder contains:

MATLAB (or Octave) scripts to produce:

- **Fig_2_a.m**: FTP-75 Speed profile graph Speed vs. Time
- **Fig_2_b.m**: Histogram and best fit line of Car mileages from EPA report and simulated using the Streetsmart model. 
- **Fig_2_c.m**: Histogram and best fit lines for the distributions of the fuel economies of car fleets from Riyadh, the UK , and Poland.  

p.p1 {margin: 0.0px 0.0px 0.0px 0.0px; font: 12.0px Helvetica}
p.p2 {margin: 0.0px 0.0px 0.0px 0.0px; font: 12.0px Helvetica; min-height: 14.0px}
li.li1 {margin: 0.0px 0.0px 0.0px 0.0px; font: 12.0px Helvetica}
li.li3 {margin: 0.0px 0.0px 0.0px 0.0px; font: 12.0px Arial}
span.s1 {text-decoration: underline}
span.s2 {font: 12.0px Helvetica}
span.s3 {font-kerning: none; color: #000000}
span.s4 {text-decoration: underline ; font-kerning: none; color: #1155cc}
ul.ul1 {list-style-type: square}
ul.ul2 {list-style-type: hyphen}