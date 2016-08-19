# megan
Even Interview. See notebook file for the brain dump...

## Setup

1. `virtualenv venv`
1. `source venv/bin/activate`
1. `pip install -r requirements.txt`
1. `jupyter notebook`

## Organization

- `even_account` has all the modules for an account
    - `RealDateAccount` is an account with an interface using real dates (ex 21016-1-1)
    - `Account` is an account that begins at day 0
    - `PayCycle` combines all of the periodic incomes and expenses
    - `ExpenseGoalAggregator` combines all of the one-off goals
    - `...Transaction` are a number of classes supporting different transaction time period types
    - Tests can be run in each file by running the file
- `Megas's Even Account.ipynb` was my first attempt at the problem. It is a brain dump
- `meagan_acount_test.ipynb` is an example usage of `RealDateAccount` with pretty plots

## Design

### Requested Features
- Periodic income
- Periodic expenses
- One-off goals
- Fixed daily allowance for all time
- Look at balance over time
- Look at tranactions over time

### Design Decisions
- I did not allow a transaction to be added to an acount that would put the account in the red at any time
- I assume all income/expenses start right away
- I assume that goals, because they are transient, are funded from the daily allowance. Therfore the daily allowance is decreased for all time (to keep it constant) by the largest amount necessary to meet the goals.
- Daily allowance is similar to discretionary rate with the key differnce that it takes into account goals
- I created transaction ids to make it easier to remove transactions that were already added

### Future Features
- Allow for entering expenses/income that will begin in the future
- Break out income, expenses and goals balance/transactions
- Allow for variable daily allowance (particularly once goals expire)
- Better name for `ExpenseGoal` and `ExpenseGoalAggregator`
- Add other types of one-off transactions
- Clean-up `PayCycle` code

## Problem Statement
A person (let’s call her Megan), has trouble managing her money. Megan is just one example of someone that is struggling with finances; as you’ll see, this problem is quite generic.
Megan has n number of sources of income (multiple jobs), each on an understood schedule, e.g. every other Friday, or on the 1st and 15th of every month, etc. For this exercise, let’s assume we’ve already Even-ed out her pay, so every paycheck for each job is a predictable amount.

Megan has m number of obligations (rent, utilities, credit card payment, car insurance, etc.) also on set schedules, e.g. rent money needs to be available on the 1st, credit card on the 12th, car insurance on the 24th, and so on.

She also has a number of goals. She wants to save up $500 to visit her family on September 3. She wants $100 for horse riding lessons each week, needs $200 for groceries every month, and sends money home to her father every other month on the 5th for her health insurance.

So… in summary:

Multiple sources of income on different schedules.

Multiple types of expenses on different schedules.

If we wanted to guarantee that Megan had enough money for each of her expenses when they arrived, how might we go about setting aside money from her paychecks to cover them? Any money not set aside will be considered discretionary income, which Megan will spend. Additionally, how would we go about ensuring that Megan always receives a consistent amount of discretionary income, regardless of the expenses in that particular cycle?

## Problem 1

How might we go about setting aside money from her paychecks to cover all of the expenses?

## Problem 2

How would we go about ensuring that Megan always receives a consistent amount of discretionary income, regardless of the expenses in that particular cycle?
