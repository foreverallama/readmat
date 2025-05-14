%% Basic Timetable with Time and Variables
time_date = datetime(2023,1,1) + days(0:2);
time_duration = seconds([10,20,30]);
data1 = [1;2;3];
tt1 = timetable(time_date', data1);

data2 = [1,4;2,5;3,6];
tt2 = timetable(time_duration', data2);

data3 = [7;8;9];
tt3 = timetable(time_date',data1,data3);

%% With Sampling Rate and TimeStep - Parse RowTimes
tt4 = timetable(data1, 'SampleRate',10000);
tt5 = timetable(data1, 'TimeStep',seconds(1));
tt6 = timetable(data1, 'TimeStep',seconds(1), 'StartTime', seconds(10));
tt7 = timetable(data1, 'TimeStep',seconds(1), 'StartTime', datetime(2020,1,1));
%% With Variable Names
tt8 = timetable(time_date', data1, 'VariableNames', {'Pressure'});

%% With Attributes
tt9 = timetable(time_date', data1);

% Set units and continuity
tt9.Properties.DimensionNames = {'Date','Pressure'};
tt9.Properties.Description = "Random Description";
tt9.Properties.VariableDescriptions = {'myVar'};
tt9.Properties.VariableUnits = {'m/s'};
tt9.Properties.VariableContinuity = {'continuous'};

%% Timetable with Calendar Step

calm = calmonths(3);
tt10 = timetable(data1, 'TimeStep', calm, 'StartTime', datetime(2020,1,1));

%% TO ADD
% Events
% Custom Props

%% Save

save('test_timetable_v7.mat', 'tt1', 'tt2', 'tt3', 'tt4', 'tt5', 'tt6', 'tt7', 'tt8', 'tt9', 'tt10', '-v7');
save('test_timetable_v73.mat', 'tt1', 'tt2', 'tt3', 'tt4', 'tt5', 'tt6', 'tt7', 'tt8', 'tt9', 'tt10', '-v7.3');
