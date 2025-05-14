var_int = 10;
var_cell{1} = "String in Cell";
var_struct.MyField = "String in Struct";

save('test_simple_v7.mat', 'var_int', 'var_cell', 'var_struct', '-v7');
save('test_simple_v73.mat', 'var_int', 'var_cell', 'var_struct', '-v7.3');
