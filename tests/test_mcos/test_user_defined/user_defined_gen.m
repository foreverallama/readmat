obj1 = NoConstructor();
obj2 = YesConstructor();
obj3 = DefaultClass();
obj4 = NestedClass(obj1, obj2, obj3);
obj5 = YesConstructor();
obj6 = repmat(obj5,2,3);
obj7 = DefaultClass2();

save('test_user_defined_v7.mat', 'obj1', 'obj2', 'obj3', 'obj4', 'obj6', 'obj7', '-v7');
save('test_user_defined_v73.mat', 'obj1', 'obj2', 'obj3', 'obj4', 'obj6', 'obj7', '-v7.3');
