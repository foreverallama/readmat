% Case 1: Key Combined, Value Combined
dict1 = dictionary([1, 2, 3], ["apple", "banana", "cherry"]);
dict2 = dictionary(["x", "y", "z"], [10, 20, 30]);
dict3 = dictionary(["name", "age"], {"Alice", 25});
dict4 = dictionary({1, 2, 3}, ["one", "two", "three"]);

% Save all
save('test_dict_v7.mat', '-v7');
save('test_dict_v73.mat', '-v7.3');
