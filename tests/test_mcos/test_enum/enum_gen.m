enum_arr = [EnumClass.enum1, EnumClass.enum3, EnumClass.enum5; EnumClass.enum2, EnumClass.enum4, EnumClass.enum6];
enum_base = EnumClass.enum1;
enum_uint32 = EnumClass2.enum1;

e1 = EnumClass.enum1;
e2 = EnumClass.enum2;
e3 = EnumClass.enum3;
obj1 = NestedClass(e1, e2, e3);

save('test_enum_v7.mat', 'enum_base', 'enum_arr', 'obj1', 'enum_uint32', '-v7');
save('test_enum_v73.mat', 'enum_base', 'enum_arr', 'obj1', 'enum_uint32', '-v7.3');
