# Mortgage Calculator

Allows to easily plan and calculate the loan.

## Quickstart

1. Edit config file, and add special rules
2. Run the script
```
$ python main.py
```

Result:
```
 start_date   end_date   amount   interest_amount   principal_amount   repayment_amount   loan_amount
 1970-01-01  1970-01-15 8,791.59      833.33            7,958.26             0.00          92,041.74
 1970-01-15  1970-02-15 8,791.59      767.01            8,024.57           1,000.00        83,017.17
 1970-02-15  1970-03-15 8,791.59      691.81            8,099.78             0.00          74,917.39
 1970-03-15  1970-04-15 8,791.59      624.31            8,167.28             0.00          66,750.11
 1970-04-15  1970-05-15 8,791.59      556.25            8,235.34           5,000.00        53,514.78
 1970-05-15  1970-06-15 8,791.59      445.96            8,345.63             0.00          45,169.14
 1970-06-15  1970-07-15 8,791.59      376.41            8,415.18             0.00          36,753.97
 1970-07-15  1970-08-15 8,791.59      306.28            8,485.31             0.00          28,268.66
 1970-08-15  1970-09-15 8,791.59      235.57            8,556.02             0.00          19,712.64
 1970-09-15  1970-10-15 8,791.59      164.27            8,627.32             0.00          11,085.33
 1970-10-15  1970-11-15 8,791.59       92.38            8,699.21             0.00          2,386.12
 1970-11-15  1970-12-15 2,406.00       19.88            2,386.12             0.00            0.00
----------
Total interest amount: 5,113.48
```

You can print output in different formats by providing "--format" option:
```
$ python main.py --format json
{"payments": [{"start_date": "1970-01-01", "end_date": "1970-01-15", "amount": 8791.58872300099, "interest_amount": 833.3333333333334, "principal_amount": 7958.255389667657, "loan_amount": 92041.74461033235, "repayment_amount": 0}, {"start_date": "1970-01-15", "end_date": "1970-02-15", "amount": 8791.58872300099, "interest_amount": 767.0145384194362, "principal_amount": 8024.574184581554, "loan_amount": 83017.1704257508, "repayment_amount": 1000.0}, {"start_date": "1970-02-15", "end_date": "1970-03-15", "amount": 8791.58872300099, "interest_amount": 691.8097535479233, "principal_amount": 8099.7789694530675, "loan_amount": 74917.39145629773, "repayment_amount": 0}, {"start_date": "1970-03-15", "end_date": "1970-04-15", "amount": 8791.58872300099, "interest_amount": 624.3115954691477, "principal_amount": 8167.277127531843, "loan_amount": 66750.11432876589, "repayment_amount": 0}, {"start_date": "1970-04-15", "end_date": "1970-05-15", "amount": 8791.58872300099, "interest_amount": 556.2509527397158, "principal_amount": 8235.337770261274, "loan_amount": 53514.776558504615, "repayment_amount": 5000.0}, {"start_date": "1970-05-15", "end_date": "1970-06-15", "amount": 8791.58872300099, "interest_amount": 445.9564713208718, "principal_amount": 8345.63225168012, "loan_amount": 45169.1443068245, "repayment_amount": 0}, {"start_date": "1970-06-15", "end_date": "1970-07-15", "amount": 8791.58872300099, "interest_amount": 376.40953589020415, "principal_amount": 8415.179187110785, "loan_amount": 36753.965119713714, "repayment_amount": 0}, {"start_date": "1970-07-15", "end_date": "1970-08-15", "amount": 8791.58872300099, "interest_amount": 306.28304266428097, "principal_amount": 8485.305680336709, "loan_amount": 28268.659439377006, "repayment_amount": 0}, {"start_date": "1970-08-15", "end_date": "1970-09-15", "amount": 8791.58872300099, "interest_amount": 235.5721619948084, "principal_amount": 8556.016561006181, "loan_amount": 19712.642878370825, "repayment_amount": 0}, {"start_date": "1970-09-15", "end_date": "1970-10-15", "amount": 8791.58872300099, "interest_amount": 164.27202398642353, "principal_amount": 8627.316699014567, "loan_amount": 11085.326179356258, "repayment_amount": 0}, {"start_date": "1970-10-15", "end_date": "1970-11-15", "amount": 8791.58872300099, "interest_amount": 92.37771816130214, "principal_amount": 8699.211004839688, "loan_amount": 2386.11517451657, "repayment_amount": 0}, {"start_date": "1970-11-15", "end_date": "1970-12-15", "amount": 2405.9994676375413, "interest_amount": 19.884293120971414, "principal_amount": 2386.11517451657, "loan_amount": 0, "repayment_amount": 0}], "total": {"interest_amount": 5113.4754206484195}}%
```

Also you can write shedule directly to the file:
```
$ python main.py --format csv --output mortgage-schedule.csv
```

## References
Loan formulas in Russian
- https://mortgage-calculator.ru/%D1%84%D0%BE%D1%80%D0%BC%D1%83%D0%BB%D0%B0-%D1%80%D0%B0%D1%81%D1%87%D0%B5%D1%82%D0%B0-%D0%B8%D0%BF%D0%BE%D1%82%D0%B5%D0%BA%D0%B8/
- https://www.raiffeisen.ru/wiki/formuly-dlya-samostoyatelnogo-rascheta-ipoteki/
- https://www.vtb.ru/articles/kak-rasschityvaetsya-ipoteka/
- https://alfabank.ru/get-money/mortgage/articles/kak-rasschitat-ipoteku-samostoyatelno/
- https://habr.com/ru/articles/456696/
- https://www.consultant.ru/edu/student/consultation/protsenty_po_kreditu/

## TODO:
- Daily rate
- Config .ini support
