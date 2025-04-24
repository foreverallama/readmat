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

save('map1.mat','map1');
save('map2.mat','map2');
save('map3.mat','map3');
save('map4.mat','map4');
