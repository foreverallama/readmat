enum_arr = [EnumClass.enum1, EnumClass.enum3, EnumClass.enum5; EnumClass.enum2, EnumClass.enum4, EnumClass.enum6];
enum_base = EnumClass.enum1;
enum_uint32 = EnumClass2.enum1;

e1 = EnumClass.enum1;
e2 = EnumClass.enum2;
e3 = EnumClass.enum3;
obj1 = NestedClass(e1, e2, e3);

save('enum_base.mat','enum_base','-v7');
save('enum_array.mat','enum_arr','-v7');
save('enum_inside_obj.mat','obj1','-v7');
save('enum_uint32.mat','enum_uint32','-v7');
