s1 = "Hello";
s2 = ["Apple", "Banana", "Cherry"; "Date", "Fig", "Grapes"];
s3 = "";

save('string_base.mat', 's1','-v7');
save('string_array.mat', 's2','-v7');
save('string_empty.mat', 's3','-v7');
