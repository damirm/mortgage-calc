from argparse import ArgumentParser, FileType
import datetime
import tomllib
import dataclasses
import calendar
from typing import Dict, Generator, Iterator, Tuple, IO, List
from enum import Enum
import json
import csv
import sys
import os


class RepaymentGoal(Enum):
    PERIOD = 1
    MANDATORY_PAYMENT = 2


@dataclasses.dataclass
class Repayment:
    date: datetime.date
    amount: float
    goal: RepaymentGoal
    regular_payment_included: bool
    override_monthly_budget: bool

    def is_mandatory_payment(self) -> bool:
        return self.__is_goal_of(RepaymentGoal.MANDATORY_PAYMENT)

    def is_period(self) -> bool:
        return self.__is_goal_of(RepaymentGoal.PERIOD)

    def __is_goal_of(self, goal: RepaymentGoal) -> bool:
        if isinstance(self.goal, RepaymentGoal):
            return self.goal.name == goal.name
        elif isinstance(self.goal, str):
            return self.goal == goal.name
        raise ValueError(f"Invalid repayment goal: {self.goal}")


@dataclasses.dataclass
class Loan:
    start_date: datetime.date
    amount: float
    months: int
    rate: float
    payment_day: int
    monthly_budget: float
    default_repayment_goal: RepaymentGoal


@dataclasses.dataclass
class Payment:
    start_date: datetime.date
    end_date: datetime.date
    amount: float
    interest_amount: float
    principal_amount: float
    loan_amount: float
    repayment_amount: float
    total_paid_amount: float


@dataclasses.dataclass
class PaymentTotal:
    interest_amount: float


def add_months(sourcedate: datetime.date, months: int) -> datetime.date:
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return datetime.date(year, month, day)


def days_in_year(year: int) -> int:
    base = 365
    return base + 1 if calendar.isleap(year) else base


def format_money(val: float) -> str:
    return "{:0,.2f}".format(val)


def print_row(row: str, output: IO):
    output.write(row + os.linesep)


def print_line(cols, output: IO, *vals):
    parts = [pad_col(col, val) for (col, val) in zip(cols, vals)]
    print_row(" ".join(parts), output)


def pad_col(col: str, value: str) -> str:
    padding = max(len(col), len(value))
    return "{value:^{padding}}".format(value=value, padding=padding)


def iter_repayments(
    period_start: datetime.date,
    period_end: datetime.date,
    repayments: Dict[datetime.date, Iterator[Repayment]],
    default_value: Iterator[Repayment],
    period_payment: float,
    loan: Loan,
) -> Generator[Repayment, None, None]:
    period = period_end - period_start
    found = False
    for days in range(period.days):
        date = period_start + datetime.timedelta(days=days)
        if date in repayments:
            found = True
            for repayment in repayments[date]:
                if repayment.override_monthly_budget:
                    loan.monthly_budget = repayment.amount
                if repayment.regular_payment_included:
                    repayment.amount -= period_payment
                yield repayment
    if not found:
        for repayment in default_value:
            yield repayment
    return


def get_default_repayments(loan: Loan, period_payment: float) -> List[Repayment]:
    zero_repayment = Repayment(loan.start_date, 0, loan.default_repayment_goal, False, False)
    default_repayment = (
        Repayment(loan.start_date, loan.monthly_budget - period_payment, loan.default_repayment_goal, False, False)
        if loan.monthly_budget > 0
        else zero_repayment
    )
    return list(filter(lambda r: r.amount > 0, (default_repayment,)))


def annuity_payment(amount: float, monthly_rate: float, months: int):
    ratio = (monthly_rate * (1 + monthly_rate) ** months) / (((1 + monthly_rate) ** months) - 1)
    return amount * ratio


def calc_interest_amount(
    loan: Loan, loan_amount: float, period_start: datetime.date, period_end: datetime.date
) -> float:
    return (loan_amount * (loan.rate / 100) * (period_end - period_start).days) / days_in_year(period_start.year)


def get_first_period_end(loan: Loan) -> datetime.date:
    return (
        loan.start_date.replace(day=loan.payment_day)
        if loan.start_date.day < loan.payment_day
        else add_months(loan.start_date, 1).replace(day=loan.payment_day)
    )


def year_rate_to_monthly(rate: float) -> float:
    return rate / 100 / 12


def payments(
    loan: Loan,
    repayments: Dict[datetime.date, Iterator[Repayment]],
) -> Generator[Tuple[Payment, PaymentTotal], None, None]:
    loan_amount = loan.amount

    period_start = loan.start_date
    period_end = get_first_period_end(loan)
    total_payment = PaymentTotal(0)

    yield (
        Payment(
            period_start,
            period_start,
            0,
            0,
            0,
            loan_amount,
            0,
            0,
        ),
        total_payment,
    )

    end_date = add_months(loan.start_date, loan.months)
    while period_end <= end_date:
        monthly_rate = year_rate_to_monthly(loan.rate)
        period_payment = annuity_payment(loan_amount, monthly_rate, loan.months)
        interest_amount = calc_interest_amount(loan, loan_amount, period_start, period_end)

        principal_amount = period_payment - interest_amount
        total_payment.interest_amount += interest_amount

        default_repayments = get_default_repayments(loan, period_payment)
        period_repayments = list(
            iter_repayments(period_start, period_end, repayments, iter(default_repayments), period_payment, loan)
        )

        current_mandatory_repayment = sum(
            r.amount for r in filter(lambda r: r.is_mandatory_payment(), period_repayments)
        )
        if current_mandatory_repayment > 0:
            loan_amount -= current_mandatory_repayment
            # TODO: Is it correct?
            # period_payment = annuity_payment(loan_amount, monthly_rate, loan.months)

        current_period_repayment = sum(r.amount for r in filter(lambda r: r.is_period(), period_repayments))
        if current_period_repayment > 0:
            # TODO: Is it enough? Is it correct?
            loan_amount -= current_period_repayment

        loan_amount -= principal_amount

        if loan_amount <= 0.0:
            principal_amount += loan_amount
            period_payment = interest_amount + principal_amount
            loan_amount = 0

        sum_repayment_amount = sum(r.amount for r in period_repayments)
        total_payment_in_period = period_payment + sum_repayment_amount

        yield (
            Payment(
                period_start,
                period_end,
                max(0, period_payment),
                max(0, interest_amount),
                max(0, principal_amount),
                loan_amount,
                sum_repayment_amount,
                total_payment_in_period,
            ),
            total_payment,
        )

        period_start = period_end
        period_end = add_months(period_end, 1)

        if loan_amount <= 0:
            break


def group_repayments(
    repayments: Iterator[Repayment],
) -> Dict[datetime.date, Iterator[Repayment]]:
    res = dict()

    for repayment in repayments:
        res.setdefault(repayment.date, []).append(repayment)

    return res


def print_table(loan: Loan, gen: Generator[Tuple[Payment, PaymentTotal], None, None], output: IO):
    cols_padding = " "
    cols = (
        "start_date",
        "end_date",
        "amount",
        "interest_amount",
        "principal_amount",
        "principal_total_amount",
        "repayment_amount",
        "total_paid_amount",
        "loan_amount",
    )
    padded_cols = ["{}{}{}".format(cols_padding, col, cols_padding) for col in cols]

    total_payment = PaymentTotal(0)

    for payment, total in gen:
        total_payment = total

        values_to_print = (
            payment.start_date.isoformat(),
            payment.end_date.isoformat(),
            format_money(payment.amount),
            format_money(payment.interest_amount),
            format_money(payment.principal_amount),
            format_money(payment.principal_amount + payment.repayment_amount),
            format_money(payment.repayment_amount),
            format_money(payment.total_paid_amount),
            format_money(payment.loan_amount),
        )

        if payment.end_date == loan.start_date:
            headers = (pad_col(val, col) for (col, val) in zip(padded_cols, values_to_print))
            print_row(" ".join(headers), output)

        print_line(padded_cols, output, *values_to_print)

    print_row("-" * 10, output)
    print_row(
        "Total interest amount: {}".format(format_money(total_payment.interest_amount)),
        output,
    )


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        elif isinstance(o, datetime.date):
            return o.isoformat()
        return super().default(o)


def print_json(gen: Generator[Tuple[Payment, PaymentTotal], None, None], output: IO):
    total_payment = PaymentTotal(0)
    result = []
    for payment, total in gen:
        total_payment = total
        result.append(payment)
    output.write(json.dumps(dict(payments=result, total=total_payment), cls=EnhancedJSONEncoder))


def print_csv(
    gen: Generator[Tuple[Payment, PaymentTotal], None, None],
    output: IO,
    with_headers: bool = True,
):
    cols = (
        "start_date",
        "end_date",
        "amount",
        "interest_amount",
        "principal_amount",
        "repayment_amount",
        "total_paid_amount",
        "loan_amount",
    )

    writer = csv.writer(output)
    if with_headers:
        writer.writerow(cols)

    for payment, _ in gen:
        row = (
            payment.start_date.isoformat(),
            payment.end_date.isoformat(),
            payment.amount,
            payment.interest_amount,
            payment.principal_amount,
            payment.repayment_amount,
            payment.total_paid_amount,
            payment.loan_amount,
        )
        writer.writerow(row)


SUPPORTED_FORMATS = ("table", "json", "csv")


def main(args):
    with open(args.config, "rb") as f:
        config = tomllib.load(f)

    loan = Loan(**config["loan"])
    repayments = group_repayments((Repayment(**repayment) for repayment in config.get("repayment", [])))

    gen = payments(loan, repayments)

    if args.format == "table":
        print_table(loan, gen, args.output)
    elif args.format == "json":
        print_json(gen, args.output)
    elif args.format == "csv":
        print_csv(gen, args.output, with_headers=True)
    else:
        raise ValueError(f"Unknown format: {args.format}")


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--config", help="Path to config file", default="config.toml")
    parser.add_argument("--format", type=str, default="table", choices=SUPPORTED_FORMATS)
    parser.add_argument("--output", type=FileType("w"), default=sys.stdout)
    return parser.parse_args()


if __name__ == "__main__":
    main(parse_args())
