var_int = 10;
var_cell{1} = "String in Cell";
var_struct.MyField = "String in Struct";

save('var_int.mat','var_int','-v7');
save('var_cell.mat','var_cell','-v7');
save('var_struct.mat','var_struct','-v7');
