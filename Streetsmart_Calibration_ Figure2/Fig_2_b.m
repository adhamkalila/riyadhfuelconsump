% script will create the first figure part b of the paper
% Written by: Adham Kalila (kalila@mit.edu) in December 2016
% LOAD variables

load ('data/FEandprofile.mat');
load ('data/Fuelec2.mat')

%% Clean Variables to omit values greater than 

city = allalpha17.CityMPG;
simple_clean = str2double(city);
data=simple_clean(find(simple_clean<51)); % [MPG]
data_metric = data.*0.425144     ;           % [km/l]
%% create distribution 
clear yy
a = histogram(data_metric,25, 'Normalization', 'pdf');
xx=[min(data_metric):0.01:max(data_metric)];


% yy = spline(a.Values,a.BinEdges(1:end-1),xx)
pd = fitdist(data_metric, 'lognormal');
mu = pd.mu;
sig = pd.sigma;
for i = 1:size(xx, 2)
yyb(i) = (xx(i)*sig*sqrt(2*pi))^(-1)*exp(-(log(xx(i)) - mu)^(2)/(2*(sig^2)));
end
%% 
figb = figure
plot(xx,yyb,'b', 'LineWidth', 2)
xlim([0,30]);
xlabel('Fuel Economy [km/l]')
ylabel('Frequency')
alpha(.5);

%% produce array of simulated FE to plot on same fig
% input the number of observations in each bin:
FACTOR = 1;

obs = [
    39
    82
    239
    307
    338
    381
    270
    207
    131
    94
    142] * FACTOR;
FE_prop = [];
for i = 1:size(obs)
    sample = round(rand(obs(i),1)*456976);
    % Fuel economy array with proportions similar to EPA
    %Fuelec has the old ranges with narrow std. dev
    %Fuelec2 has the new values with approx 1 std dev.
     for j=1:obs(i)
         try
           FE_prop = [FE_prop, Fuelec2(sample(j), i)];
         catch 
             continue
         end
         
     end
end

FE_prop = FE_prop.*0.425144;           % [km/l]
%% Plot
figure(figb)
hold on
histogram(FE_prop,[0:30], 'Normalization', 'pdf')
ylim([-0.002,0.2])
set(get(gca,'child'),'FaceColor','[0,0.5,0]','EdgeColor','w');
alpha(.5);
legend('EPA', 'StreetSmart')

%% Save as EPS
set(figb, 'Position', [0 0 400 200])
print(figb,'-dpsc2','-painters','-r600','fig_1_b_new.eps')