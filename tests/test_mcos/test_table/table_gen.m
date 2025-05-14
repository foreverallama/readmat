T1 = table([1.1; 2.2; 3.3], [4.4; 5.5; 6.6]);

T2 = table(["apple"; "banana"; "cherry"]);

Time = datetime(2020,1,1) + days(0:2)';
Duration = seconds([30; 60; 90]);
T3 = table(Time, Duration);

S = struct('field1', 123, 'field2', 'abc');
C = {S; S; S}; % cell array of structs
O = MyObj(42);  % assuming MyObj is defined somewhere
T4 = table(C, {O; O; O});

T5 = table({1; 'text'; datetime(2023,1,1)});

T6 = table([1.1; NaN; 3.3], ["A"; ""; "C"]);

T7 = table([10; 20; 30], [100; 200; 300], 'VariableNames', {'X', 'Y'});

T8 = table([1; 2; 3], [4; 5; 6], ...
    'VariableNames', {'Col1', 'Col2'}, ...
    'RowNames', {'R1', 'R2', 'R3'});

T9 = table([1; 2], ["one"; "two"], 'VariableNames', {'ID', 'Label'});
T9.Properties.Description = 'Test table with full metadata';
T9.Properties.DimensionNames = {'RowId', 'Features'};
T9.Properties.UserData = struct('CreatedBy', 'UnitTest', 'Version', 1.0);
T9.Properties.VariableUnits = {'', 'category'};
T9.Properties.VariableDescriptions = {'ID number', 'Category label'};
T9.Properties.VariableContinuity = {'continuous', 'step'};

time = datetime(2023,1,1) + days(0:2);
data = [1,4;2,5;3,6];
T10 = table(time', data);

save('test_table_v7.mat', 'T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9' ,'T10', '-v7');
save('test_table_v73.mat', 'T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9' ,'T10', '-v7.3');
