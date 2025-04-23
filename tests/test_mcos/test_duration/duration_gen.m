dur1 = seconds(5);
dur2 = minutes(5);
dur3 = hours(5);
dur4 = days(5);
dur5 = duration(1,2,3); % 1h, 2m, 3s
dur6 = seconds([10, 20, 30; 40, 50, 60]);
dur7 = duration.empty;
dur8 = years([1 2 3]);

save('dur_s.mat','dur1','-v7');
save('dur_m.mat','dur2','-v7');
save('dur_h.mat','dur3','-v7');
save('dur_d.mat','dur4','-v7');
save('dur_base.mat','dur5','-v7');
save('dur_array.mat','dur6','-v7');
save('dur_empty.mat','dur7','-v7');
save('dur_y.mat','dur8','-v7');
