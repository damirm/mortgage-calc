#!/bin/bash

# result=$(python main.py --config config.damirm.toml --format json)
result=$(python main.py --format json)

loan_amount_series=$(echo "$result" | jq '.payments.[].loan_amount')
amount_series=$(echo "$result" | jq '.payments.[].amount')
interest_amount_series=$(echo "$result" | jq '.payments.[].interest_amount')

principal_amount_series=$(echo "$result" | jq -r '.payments | map(.principal_amount + .repayment_amount) | join("\n")')
series=$(paste -d, <(echo "$amount_series") <(echo "$interest_amount_series") <(echo "$principal_amount_series"))
echo "$series" | asciigraph -h 30 -c "Mortgage" -sn 3 -sl "Mandatory, Interest, Principal" -sc "red, blue, green"
