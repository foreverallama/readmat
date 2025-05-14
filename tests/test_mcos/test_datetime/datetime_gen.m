dt1 = datetime(2025, 4, 1, 12, 00, 00);
dt2 = datetime(2025,4,1,12,00,00, 'TimeZone', "America/New_York");
dt3 = datetime(2025, 4, 1) + days(0:5);
dt3 = reshape(dt3, 2, 3);
dt4 = datetime.empty;
dt5 = datetime(2025,4,1,12,00,00, 'Format', 'yyyy-MM-dd HH:mm:ss');

save('test_datetime_v7.mat', 'dt1', 'dt2', 'dt3', 'dt4', 'dt5', '-v7');
save('test_datetime_v73.mat', 'dt1', 'dt2', 'dt3', 'dt4', 'dt5', '-v7.3');
