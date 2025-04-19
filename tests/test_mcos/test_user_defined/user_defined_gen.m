obj1 = NoConstructor();
obj2 = YesConstructor();
obj3 = DefaultClass();
obj4 = NestedClass(obj1, obj2, obj3);
obj5 = YesConstructor();
obj6 = repmat(obj5,2,3);
obj7 = DefaultClass2();

save('object_without_constructor.mat', 'obj1', '-v7');
save('object_with_constructor.mat', 'obj2', '-v7');
save('object_with_default.mat', 'obj3', '-v7');
save('nested_object.mat', 'obj4', '-v7');
save('object_array.mat', 'obj6', '-v7');
save('object_in_default_prop.mat','obj7','-v7');
