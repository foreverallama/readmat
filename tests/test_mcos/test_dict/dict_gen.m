% Case 1: Key Combined, Value Combined
dict1 = dictionary([1, 2, 3], ["apple", "banana", "cherry"]);
dict2 = dictionary(["x", "y", "z"], [10, 20, 30]);
dict3 = dictionary(["name", "age"], {"Alice", 25});
dict4 = dictionary({1, 2, 3}, ["one", "two", "three"]);

% Save all
save('dict1.mat', 'dict1');
save('dict2.mat', 'dict2');
save('dict3.mat', 'dict3');
save("dict4.mat", "dict4");
