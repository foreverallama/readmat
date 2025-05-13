% Empty calendarDuration
cdur1 = calendarDuration.empty(0, 0);

% Pure calendarDays
cdur2 = caldays([1 2 3]);

% Pure calendarWeeks
cdur3 = calweeks([1 2]);

% Mixed caldays + calmonths
cdur4 = caldays([1 2]) + calmonths([1 0]);

% Mixed calmonths + calyears
cdur5 = calyears(1) + calmonths([0 6]);

% Mixed calquarters + caldays
cdur6 = calquarters(1) + caldays(15);

% 2D array with varied values
cdur7 = [calmonths(1), caldays(5); calmonths(2), caldays(10)];

% Include time via duration (adds millis)
cdur8 = caldays(1) + duration(1, 2, 3);  % 1 day + 1h 2m 3s

% Save
save('test_caldur_v7.mat', '-v7');
save('test_caldur_v73.mat', '-v7.3');
