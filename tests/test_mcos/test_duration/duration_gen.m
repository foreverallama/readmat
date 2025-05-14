dur1 = seconds(5);
dur2 = minutes(5);
dur3 = hours(5);
dur4 = days(5);
dur5 = duration(1,2,3); % 1h, 2m, 3s
dur6 = seconds([10, 20, 30; 40, 50, 60]);
dur7 = duration.empty;
dur8 = years([1 2 3]);

save('test_duration_v7.mat', '-v7');
save('test_duration_v73.mat','-v7.3');
