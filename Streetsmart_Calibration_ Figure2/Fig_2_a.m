% script will create the first figure part a of the paper
% Written by: Adham Kalila (kalila@mit.edu) in December 2016
% Load ftp-75 and allalpha17
load ('data/FEandprofile.mat');
%%
% convert the speed profile to km/h from mps
speedkmh = zeros(size(ftp75.Speed));
for i= 1:size(ftp75.Speed)
speedkmh(i) = ftp75.Speed(i)*1.60934;
end 


fig = figure 
plot (ftp75.Total, speedkmh, 'LineWidth', 2)
xlabel('Time [s]')
ylabel('Speed [km/h]')

%% Save in EPS
set(fig, 'Position', [0 0 400 200])
print(fig,'-dpsc2','-painters','-r600','fig_1_a_commandline2_trial1.eps')
