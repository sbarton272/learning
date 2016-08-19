"""
Account managment
"""

from datetime import datetime
from datetime import date
import calendar
import numpy as np

from transactions import DayBasedTransaction, MonthlyTransaction, AnnualTransaction
from transactions import ExpenseGoal
from transactions import PeriodicTransaction, Transaction
from account import Account

## RealDateAccount ------------------------------------------

class RealDateAccount(object):
    """
    Account that implements an interface that
    relies on real dates. Uses today if date not provided
    """
    def __init__(self, opening_date = None, starting_balance = 0):
        if opening_date == None:
            opening_date = datetime.now()
        self.opening_date = opening_date

        # Find days since last leap year
        self.day_offset_from_leap_year = self._find_day_offset_from_leap_year(opening_date)
        
        self.account = Account(starting_balance)

    def _find_day_offset_from_leap_year(self, opening_date):
        # Find prev leap year
        leap_year = opening_date.year - 1
        while not calendar.isleap(leap_year):
            leap_year -= 1
        first_day_of_cycle = date(leap_year+1, 1, 1)
        offset = opening_date - opening_date
        return offset.days

    def get_opening_date(self):
        return self.opening_date

    def get_balance(self, start_date, stop_date = None, include_daily_allowance = False):
        start_day, stop_day = self._convert_dates_to_days(start_date, stop_date)
        return self.account.get_balance(start_day, stop_day, include_daily_allowance)

    def get_transactions(self, start_date, stop_date = None, include_daily_allowance = False):
        start_day, stop_day = self._convert_dates_to_days(start_date, stop_date)
        return self.account.get_transactions(start_day, stop_day, include_daily_allowance)

    def _convert_dates_to_days(self, start_date, stop_date):
        if stop_date == None:
            stop_date = start_date + datetime.timedelta(days=1)
        assert(self.opening_date <= start_date and start_date < stop_date)
        
        start_day = start_date - self.opening_date
        stop_day = stop_date - self.opening_date
        return start_day.days, stop_day.days
 
    def get_daily_allowance(self):
        return self.account.get_daily_allowance()

    def add_day_based_transaction(self, amount, period_in_days, day_offset=0):
        """
        Create periodic transaction that begins immediatly
        """
        return self.account.add_transaction(DayBasedTransaction(amount, period_in_days, day_offset))

    def add_monthly_transaction(self, amount, day_of_month):
        """
        Create periodic transaction that begins immediatly

        day_of_month starts at 1
        """
        day_of_month -= 1
        return self.account.add_transaction(MonthlyTransaction(amount, day_of_month, self.day_offset_from_leap_year))

    def add_annual_transaction(self, amount, day_of_year):
        """
        Create periodic transaction that begins immediatly

        day_of_year starts at 1
        """
        day_of_year -= 1
        return self.account.add_transaction(AnnualTransaction(amount, day_of_year, self.day_offset_from_leap_year))

    def add_goal(self, amount, completion_date, duration):
        """
        Create periodic transaction that begins immediatly
        """
        completion_day = completion_date - self.opening_date
        completion_day = completion_day.days
        return self.account.add_transaction(ExpenseGoal(amount, completion_day, duration))

    def get_constituent_transactions(self):
        return self.account.get_constituent_transactions()

    def remove_transaction(self, transaction_id):
        return self.account.remove_transaction(transaction_id)

## Tests ------------------------------------------

def test_account():
    a = RealDateAccount(date(2017,1,1))

    assert(np.array_equal(a.get_balance(date(2017,1,1), date(2017,1,8)), [0] * 7))
    assert(np.array_equal(a.get_transactions(date(2017,01,1), date(2017,1,8)), [0] * 7))
    assert(a.get_daily_allowance() == 0)

    # Cannot add transaction because would go red
    assert(not a.add_day_based_transaction(-1, 2, 1))
    assert(not a.add_monthly_transaction(-1, 0))
    assert(not a.add_annual_transaction(-1, 1))
    assert(not a.add_goal(1, date(2017,1,4), 3))

    # Add valid
    assert(a.add_day_based_transaction(1, 2, 1))
    assert(np.array_equal(a.get_balance(date(2017,1,1), date(2017,1,8)), [0,1,1,2,2,3,3]))
    assert(np.array_equal(a.get_transactions(date(2017,01,1), date(2017,1,8)), [0,1,0,1,0,1,0]))
    assert(a.get_daily_allowance() == 0)

    # Add monthly transaction
    assert(a.add_monthly_transaction(1, 0))
    assert(np.array_equal(a.get_balance(date(2017,1,1), date(2017,1,8)), [1,2,2,3,3,4,4]))
    assert(np.array_equal(a.get_transactions(date(2017,01,1), date(2017,1,8)), [1,1,0,1,0,1,0]))
    assert(a.get_daily_allowance() >= .5)

    # Add annual transaction
    assert(a.add_annual_transaction(-1, 0))
    assert(np.array_equal(a.get_balance(date(2017,1,1), date(2017,1,8)), [0,1,1,2,2,3,3]))
    assert(np.array_equal(a.get_transactions(date(2017,01,1), date(2017,1,8)), [0,1,0,1,0,1,0]))
    assert(a.get_daily_allowance() == 0)

    # Cannot add a goal because no daily allowance
    assert(not a.add_goal(1, date(2017,1,4), 3))

    # Add more income
    assert(a.add_annual_transaction(1, 0))
    assert(np.array_equal(a.get_balance(date(2017,1,1), date(2017,1,8)), [1,2,2,3,3,4,4]))
    assert(np.array_equal(a.get_transactions(date(2017,01,1), date(2017,1,8)), [1,1,0,1,0,1,0]))
    assert(a.get_daily_allowance() >= .5)
    allowance = a.get_daily_allowance()

    # Can now add goal
    assert(a.add_goal(1, date(2017,1,4), 3))
    assert(np.allclose(a.get_transactions(date(2017,01,1), date(2017,1,8)), np.array([2,2,-1,3,0,3,0]) / 3.0))
    assert(np.isclose(a.get_daily_allowance() + 1.0/3, allowance))

    # However cannot add another goal
    assert(not a.add_goal(1, date(2017,1,4), 3))

    # Get ready to remove transactions
    assert(len(a.get_constituent_transactions()) == 5)

    assert(not a.remove_transaction(-1))
    assert(not a.remove_transaction(5))

    # Cannot remove income because would go into the red
    assert(not a.remove_transaction(0))
    assert(not a.remove_transaction(1))
    assert(not a.remove_transaction(3))

    # Can remove annual expense
    assert(a.remove_transaction(2))
    assert(np.allclose(a.get_transactions(date(2017,01,1), date(2017,1,8)), np.array([5,2,-1,3,0,3,0]) / 3.0))

    # Remove annual income
    assert(a.remove_transaction(3))
    assert(np.allclose(a.get_transactions(date(2017,01,1), date(2017,1,8)), np.array([2,2,-1,3,0,3,0]) / 3.0))

    # Remove remaining
    assert(a.remove_transaction(4))
    assert(not a.remove_transaction(4))
    assert(a.remove_transaction(1))

    # Back to income every other day
    assert(np.array_equal(a.get_balance(date(2017,1,1), date(2017,1,8)), [0,1,1,2,2,3,3]))
    assert(np.array_equal(a.get_transactions(date(2017,01,1), date(2017,1,8)), [0,1,0,1,0,1,0]))
    assert(a.get_daily_allowance() == 0)

    # Empty account
    assert(a.remove_transaction(0))
    assert(np.array_equal(a.get_balance(date(2017,1,1), date(2017,1,8)), [0] * 7))
    assert(np.array_equal(a.get_transactions(date(2017,01,1), date(2017,1,8)), [0] * 7))
    assert(a.get_daily_allowance() == 0)

if __name__ == '__main__':
    print 'Running real account test --',
    test_account()
    print 'pass'
