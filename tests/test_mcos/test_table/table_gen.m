T1 = table([1.1; 2.2; 3.3], [4.4; 5.5; 6.6]);
save('T1.mat', 'T1', '-v7');

T2 = table(["apple"; "banana"; "cherry"]);
save('T2.mat', 'T2', '-v7');

Time = datetime(2020,1,1) + days(0:2)';
Duration = seconds([30; 60; 90]);
T3 = table(Time, Duration);
save('T3.mat', 'T3', '-v7');

S = struct('field1', 123, 'field2', 'abc');
C = {S; S; S}; % cell array of structs
O = MyObj(42);  % assuming MyObj is defined somewhere
T4 = table(C, {O; O; O});
save('T4.mat', 'T4', '-v7');

T5 = table({1; 'text'; datetime(2023,1,1)});
save('T5.mat', 'T5', '-v7');

T6 = table([1.1; NaN; 3.3], ["A"; ""; "C"]);
save('T6.mat', 'T6', '-v7');

T7 = table([10; 20; 30], [100; 200; 300], 'VariableNames', {'X', 'Y'});
save('T7.mat', 'T7', '-v7');

T8 = table([1; 2; 3], [4; 5; 6], ...
    'VariableNames', {'Col1', 'Col2'}, ...
    'RowNames', {'R1', 'R2', 'R3'});
save('T8.mat', 'T8', '-v7');

T9 = table([1; 2], ["one"; "two"], 'VariableNames', {'ID', 'Label'});
T9.Properties.Description = 'Test table with full metadata';
T9.Properties.DimensionNames = {'RowId', 'Features'};
T9.Properties.UserData = struct('CreatedBy', 'UnitTest', 'Version', 1.0);
T9.Properties.VariableUnits = {'', 'category'};
T9.Properties.VariableDescriptions = {'ID number', 'Category label'};
T9.Properties.VariableContinuity = {'continuous', 'step'};
save('T9.mat', 'T9', '-v7');

time = datetime(2023,1,1) + days(0:2);
data = [1,4;2,5;3,6];
T10 = table(time', data);
save('T10.mat', 'T10', '-v7');
