%% Empty calendarDuration
cdur1 = calendarDuration.empty(0, 0);
save('cdur1.mat', 'cdur1');

%% Pure calendarDays
cdur2 = caldays([1 2 3]);
save('cdur2.mat', 'cdur2');

%% Pure calendarWeeks
cdur3 = calweeks([1 2]);
save('cdur3.mat', 'cdur3');

%% Mixed caldays + calmonths
cdur4 = caldays([1 2]) + calmonths([1 0]);
save('cdur4.mat', 'cdur4');

%% Mixed calmonths + calyears
cdur5 = calyears(1) + calmonths([0 6]);
save('cdur5.mat', 'cdur5');

%% Mixed calquarters + caldays
cdur6 = calquarters(1) + caldays(15);
save('cdur6.mat', 'cdur6');

%% 2D array with varied values
cdur7 = [calmonths(1), caldays(5); calmonths(2), caldays(10)];
save('cdur7.mat', 'cdur7');

%% Include time via duration (adds millis)
cdur8 = caldays(1) + duration(1, 2, 3);  % 1 day + 1h 2m 3s
save('cdur8.mat', 'cdur8');
