% Scalars and 2D arrays for all types
int_types = {
    'int8',    int8(42),      int8([1 2 3; 4 5 6])
    'uint8',   uint8(42),     uint8([1 2 3; 4 5 6])
    'int16',   int16(42),     int16([1 2 3; 4 5 6])
    'uint16',  uint16(42),    uint16([1 2 3; 4 5 6])
    'int32',   int32(42),     int32([1 2 3; 4 5 6])
    'uint32',  uint32(42),    uint32([1 2 3; 4 5 6])
    'int64',   int64(42),     int64([1 2 3; 4 5 6])
    'uint64',  uint64(42),    uint64([1 2 3; 4 5 6])
    'single',  single(3.14),  single([1.1 2.2 3.3; 4.4 5.5 6.6])
    'double',  3.14,          [1.1 2.2 3.3; 4.4 5.5 6.6]
};

char_scalar = 'Hello';
char_array = ['ab'; 'cd'; 'ef'];

% Create a structure to store all data
data = struct();

for i = 1:size(int_types, 1)
    type = int_types{i,1};
    scalar = int_types{i,2};
    array2d = int_types{i,3};

    data.([type '_scalar']) = scalar;
    data.([type '_array']) = array2d;
end

data.char_scalar = char_scalar;
data.char_array = char_array;

save("basic_v73.mat", '-struct', 'data', '-v7.3');
save("basic_v7.mat", '-struct', 'data', '-v7');

%% Struct and Cell
% Basic cell array
data1.cell_scalar = {'text'};
data1.cell_array = {'A', [1 2; 3 4], {true, false}};

% Deeply nested cell
nested_cell = {{'level1', {{'level2', {{'level3', 123}}}}}};
data1.cell_nested = nested_cell;

% Basic struct
s1.name = 'test';
s1.value = 123;
s1.data = [1 2; 3 4];
data1.struct_scalar = s1;

% Struct array
s2(1).id = 1;
s2(1).info = 'first';
s2(2).id = 2;
s2(2).info = 'second';
data1.struct_array = s2;

% Deeply nested struct
deep_struct.level1.level2.level3.value = 42;
deep_struct.level1.level2.cell = {{'nested', struct('a', 1, 'b', 2)}};
data1.struct_nested = deep_struct;

data1.scalar_struct_with_cell = {'a', 'b'};

data1.array_struct_with_cell(1,1).field1 = {'a', 'b'};
data1.array_struct_with_cell(2,1).field1 = {'c', 'd'};

% Save to v7.3 .mat file
save("struct_cell_v73.mat", '-struct', 'data1', '-v7.3');
save("struct_cell_v7.mat", '-struct', 'data1', '-v7');
