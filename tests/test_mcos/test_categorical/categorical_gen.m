% Basic 1D Categorical
cat1 = categorical({'red', 'green', 'blue', 'red'});

% 2D Categorical Array
cat2 = categorical({'low', 'medium'; 'high', 'low'});

% Categorical with Explicit Categories (Unordered)
cat3 = categorical({'cold', 'hot', 'warm'}, {'cold', 'warm', 'hot'});

% Categorical with Explicit Categories (Ordered)
cat4 = categorical({'small', 'medium', 'large'}, ...
                   {'small', 'medium', 'large'}, 'Ordinal', true);

% Numeric Labels Converted to Categorical
cat5 = categorical([1, 2, 3, 2, 1], [1, 2, 3], {'low', 'medium', 'high'});

% Empty Categorical
cat6 = categorical({});

% Categorical with Missing Data (Empty string)
cat7 = categorical({'cat', '', 'dog', 'mouse'}, ...
                   {'cat', 'dog', 'mouse'});

% Categorical from String Array
cat8 = categorical(["spring", "summer", "autumn", "winter"]);

% Categorical with Mixed Case (Categories are case-sensitive)
cat9 = categorical({'On', 'off', 'OFF', 'ON', 'on'});

% 3D Categorical Array
cat10 = categorical(repmat(["yes", "no", "maybe"], [2, 1, 2]));

%% Saving

save('test_categorical_v7.mat', '-v7');
save('test_categorical_v73.mat', '-v7.3');
