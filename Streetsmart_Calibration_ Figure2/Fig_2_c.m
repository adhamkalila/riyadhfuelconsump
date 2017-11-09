% script will create the first figure part c of the paper
% Written by: Adham Kalila (kalila@mit.edu) in December 2016
% LOAD variables

% input the number of observations in each bin
% It also contains code to plot two other countries for comparison 
% (UK and Poland) using TRACCS data
load('data/krange_counts.mat')

% load Vehiclematchedranges from excel and fill in the bins 12 to 14 with
% the means from the k ranges table (found in evernote )
load('data/vehiclesmatchedRanges.mat')
%% Produces Riyadh histogram 
%%% This code will plot the Accident data FE mean that results from the matching.m code
% it will make a random gaussian distribution around the FE_means with a
% std dev of 1.5
% and compare Riyadh with the UK and POland FE means from TRACCS 


FE_ricar = Vehiclesmatchedranges.meancMPG;
ranges_ricar = Vehiclesmatchedranges.rangenumber;
counts_ricar = Vehiclesmatchedranges.Count;

for i= 1:size(FE_ricar)
    if ranges_ricar(i) == 12
        FE_ricar(i) = 6.3;
    elseif ranges_ricar(i) == 13
        FE_ricar(i) = 17.27;
    elseif ranges_ricar(i) == 14
        FE_ricar(i) = 43.5;
    end
end
FE_ricar = FE_ricar.*0.425144; % [km/l]
%% Histogram for Riyadh
Ri = [];
for i = 2:size(FE_ricar)
Ri = [Ri; normrnd(FE_ricar(i), 1, [round(counts_ricar(i)),1])]; 
end

Ri = Ri(find(Ri>0)); % cuts unrealistically small FE's
%%
figc = figure
histogram(Ri,100 , 'Normalization', 'pdf')
set(get(gca,'child'),'FaceColor','[0,0.5,0]','EdgeColor','w');
%% Load the TRACCS data for UK and Poland
load('data/UKandPoTRACCS2010.mat')
%% Plot two other city's FE distribuions for comparison (From TRACCS data) 
% First UK

uk_FE_MPG = UKTRACCS_Summary2010.MPG;
uk_FE = uk_FE_MPG.*0.425144;           % [km/l]
uk_count = UKTRACCS_Summary2010.counts;

UK = [];
for i = 1:size(uk_FE)
UK = [UK; normrnd(uk_FE(i), 1, [round(uk_count(i)),1])]; 
end
figure (5)
hold on
uk = histogram(UK,100, 'Normalization', 'pdf')
clear yy
xx=[min(UK):0.01:max(UK)];

uk_x = uk.BinEdges;
uk_y = uk.Values;
uk_x = uk_x(1:end-1);
yy = spline(uk_x,uk_y, xx);
%% Plot UK
figure(figc)
hold on 
plot(xx,yy, 'b', 'LineWidth', 2 )

%%  Second Poland

Po_FE = POTRACCS_Summary2010.MPG;
Po_count = POTRACCS_Summary2010.counts;
Po_FE = Po_FE.*0.425144;           % [km/l]

%% plotting histogram of simualted normal dbns around each FE
%  std dev is chosen to be 1.5
Po_FE_list = [];
for i = 1:size(Po_FE)
Po_FE_list = [Po_FE_list; normrnd(Po_FE(i), 1, [round(Po_count(i)),1])]; 
end
figure (5)
hold on
po = histogram(Po_FE_list,100, 'Normalization', 'pdf')
clear yy
xxp=[min(Po_FE_list):0.01:max(Po_FE_list)];

po_x = po.BinEdges;
po_y = po.Values;
po_x = po_x(1:end-1);
yyp = spline(po_x,po_y, xxp);
%% Plot Poland
figure (figc) 
hold on 
plot(xxp,yyp, 'r', 'LineWidth', 2 )
xlabel('Fuel Economy [km/l]')
ylabel('Frequency')
xlim([0,30]);
ylim([-0.002,0.2]);
legend('Riyadh', 'UK', 'Poland')

%%
set(figc, 'Position', [0 0 400 200])
print(figc,'-dpsc2','-painters','-r600','fig_1_c_new.eps')