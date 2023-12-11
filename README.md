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

## References
Loan formulas in Russian
- https://mortgage-calculator.ru/%D1%84%D0%BE%D1%80%D0%BC%D1%83%D0%BB%D0%B0-%D1%80%D0%B0%D1%81%D1%87%D0%B5%D1%82%D0%B0-%D0%B8%D0%BF%D0%BE%D1%82%D0%B5%D0%BA%D0%B8/
- https://www.raiffeisen.ru/wiki/formuly-dlya-samostoyatelnogo-rascheta-ipoteki/
- https://www.vtb.ru/articles/kak-rasschityvaetsya-ipoteka/
- https://alfabank.ru/get-money/mortgage/articles/kak-rasschitat-ipoteku-samostoyatelno/

## TODO:
- Daily rate
