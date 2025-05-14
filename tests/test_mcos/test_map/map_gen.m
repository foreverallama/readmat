%% Empty
map1 = containers.Map();

%% Basic with numeric keys
keys = [1 2];
vals = {'a' 'b'};
map2 = containers.Map(keys, vals);

%% Basic with char keys

keys = {'a','b'};
vals = [1,2];
map3 = containers.Map(keys, vals);

%% Basic with string keys

keys = ["a", "b"];
vals = [1,2];
map4 = containers.Map(keys, vals);

%% Save

save('test_map_v7.mat', 'map1', 'map2', 'map3', 'map4', '-v7');
save('test_map_v73.mat', 'map1', 'map2', 'map3', 'map4', '-v7.3');
