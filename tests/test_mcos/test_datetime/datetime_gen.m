dt1 = datetime(2025, 4, 1, 12, 00, 00);
dt2 = datetime(2025,4,1,12,00,00, 'TimeZone', "America/New_York");
dt3 = datetime(2025, 4, 1) + days(0:5);
dt3 = reshape(dt3, 2, 3);
dt4 = datetime.empty;
dt5 = datetime(2025,4,1,12,00,00, 'Format', 'yyyy-MM-dd HH:mm:ss');

save('dt_base.mat','dt1','-v7');
save('dt_tz.mat','dt2','-v7');
save('dt_array.mat','dt3','-v7');
save('dt_empty.mat','dt4','-v7');
save('dt_fmt.mat','dt5','-v7');
