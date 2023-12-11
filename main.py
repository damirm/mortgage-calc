from argparse import ArgumentParser
import datetime
import tomllib
from dataclasses import dataclass
import calendar
from typing import Dict, Generator, Iterator
from enum import Enum


class RepaymentGoal(Enum):
    DEBT = 1
    PERIOD = 2
    NONE = 100


@dataclass
class Repayment:
    date: datetime.date
    amount: float
    goal: RepaymentGoal

    def is_debt(self) -> bool:
        return self.__is_goal_of(RepaymentGoal.DEBT)

    def is_period(self) -> bool:
        return self.__is_goal_of(RepaymentGoal.PERIOD)

    def __is_goal_of(self, goal: RepaymentGoal) -> bool:
        if isinstance(self.goal, RepaymentGoal):
            return self.goal.name == goal.name
        elif isinstance(self.goal, str):
            return self.goal == goal.name
        raise ValueError(f"Invalid repayment goal: {self.goal}")


@dataclass
class Loan:
    start_date: datetime.date
    amount: float
    months: int
    rate: float
    payment_day: int
    monthly_budget: float
    default_repayment_goal: RepaymentGoal


@dataclass
class Payment:
    start_date: datetime.date
    end_date: datetime.date
    amount: float
    interest_amount: float
    principal_amount: float
    loan_amount: float
    repayment_amount: float


def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return datetime.date(year, month, day)


def format_money(val: float) -> str:
    return "{:0,.2f}".format(val)


def print_line(cols, *vals):
    parts = [pad_col(col, val) for (col, val) in zip(cols, vals)]
    print(" ".join(parts))


def pad_col(col: str, value: str) -> str:
    padding = max(len(col), len(value))
    return "{value:^{padding}}".format(value=value, padding=padding)


def first_day(date: datetime.date) -> datetime.date:
    return date.replace(day=1)


def iter_repayments(period_start: datetime.date, period_end: datetime.date,
                    repayments: Dict[datetime.date, Iterator[Repayment]],
                    default_value: Iterator[Repayment]) -> Generator[Repayment, None, None]:
    period = period_end - period_start
    found = False
    for days in range(period.days):
        date = period_start + datetime.timedelta(days=days)
        if date in repayments:
            found = True
            for repayment in repayments[date]:
                yield repayment
    if not found:
        for repayment in default_value:
            yield repayment
    return


def payments(loan: Loan, repayments: Dict[datetime.date, Iterator[Repayment]]) -> Generator[Payment, None, None]:
    end_date = add_months(loan.start_date, loan.months)

    loan_amount = loan.amount
    zero_repayment = Repayment(loan.start_date, 0, RepaymentGoal.NONE)
    current_period_start = loan.start_date
    # TODO: Handle case when loan.start_date.day is greather than loan.payment_day
    current_period_end = current_period_start.replace(day=loan.payment_day)

    # TODO: Use daily rates.
    monthly_rate = loan.rate/100/12
    common_rate = (1 + monthly_rate)**loan.months
    monthly_payment = loan_amount * monthly_rate * common_rate / (common_rate - 1)

    default_repayment = Repayment(
        loan.start_date,
        loan.monthly_budget - monthly_payment,
        loan.default_repayment_goal,
    ) if loan.monthly_budget > 0 else zero_repayment

    default_repayments = list(filter(lambda r: r.amount > 0, (default_repayment,)))

    while current_period_end < end_date:
        period_repayments = list(iter_repayments(current_period_start, current_period_end,
                                 repayments, iter(default_repayments)))

        current_debt_repayment = Repayment(
            current_period_start,
            sum(r.amount for r in filter(lambda r: r.is_debt(), period_repayments)),
            RepaymentGoal.DEBT,
        )

        current_period_repayment = Repayment(
            current_period_start,
            sum(r.amount for r in filter(lambda r: r.is_period(), period_repayments)),
            RepaymentGoal.PERIOD,
        )
        if current_period_repayment.amount > 0:
            # TODO: Implement me.
            raise NotImplementedError("Repayment with period type is not implemented yet :-(")

        interest_amount = loan_amount * monthly_rate
        principal_amount = monthly_payment - interest_amount

        if current_debt_repayment.amount > 0:
            loan_amount -= current_debt_repayment.amount

        loan_amount -= principal_amount

        if loan_amount <= 0.0:
            principal_amount += loan_amount
            monthly_payment = interest_amount + principal_amount
            loan_amount = 0

        sum_repayment_amount = sum(r.amount for r in period_repayments)
        yield Payment(
            current_period_start,
            current_period_end,
            monthly_payment,
            interest_amount,
            principal_amount,
            loan_amount,
            sum_repayment_amount,
        )

        current_period_start = current_period_end
        current_period_end = add_months(current_period_end, 1)

        if loan_amount <= 0:
            break


def group_repayments(repayments: Iterator[Repayment]) -> Dict[datetime.date, Iterator[Repayment]]:
    res = dict()

    for repayment in repayments:
        res.setdefault(repayment.date, []).append(repayment)

    return res


def main(args):
    with open(args.config, "rb") as f:
        config = tomllib.load(f)

    loan = Loan(**config["loan"])

    repayments = group_repayments((Repayment(**repayment) for repayment in config.get("repayment", [])))

    cols_padding = " "
    cols = ("start_date", "end_date", "amount", "interest_amount",
            "principal_amount", "loan_amount", "repayment_amount")
    padded_cols = ["{}{}{}".format(cols_padding, col, cols_padding) for col in cols]

    total_interest_amount = 0

    for payment in payments(loan, repayments):
        total_interest_amount += payment.interest_amount

        values_to_print = (
            payment.start_date.isoformat(), payment.end_date.isoformat(), format_money(payment.amount),
            format_money(payment.interest_amount), format_money(payment.principal_amount),
            format_money(payment.loan_amount), format_money(payment.repayment_amount),
        )

        if payment.start_date == loan.start_date:
            headers = (pad_col(val, col) for (col, val) in zip(padded_cols, values_to_print))
            print(" ".join(headers))

        print_line(padded_cols, *values_to_print)

    print("-" * 10)
    print("Total interest amount: {:.2f}".format(total_interest_amount))


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--config", help="Path to config file", default="config.toml")
    return parser.parse_args()


if __name__ == "__main__":
    main(parse_args())
