"""
Class to calculate period transaction pay cycles
"""

import numpy as np
import copy
from transactions import PeriodicTransaction, DayBasedTransaction, MonthlyTransaction, AnnualTransaction

## Pay Cycle ------------------------------------------

class PayCycle(object):
    """
    This class calculates a pay cycles based upon periodic
    incomes and expenses

    Pay cycles should never go into the red
    """
    def __init__(self):
        # Start with a daily pay period with amount 0
        self.transactions = np.array([0])
        self.period = 1
        self._update_balance()
        self.component_periods = [self.period]

    def get_period(self):
        return self.period

    def get_transactions(self, start_day, stop_day):
        """
        Get summed transactions from start_day to stop_day
        non-inclusive of stop_day
        """
        assert(0 <= start_day and start_day < stop_day)
        
        # Extract necessary number of periods
        start_period = np.floor(start_day * 1.0 / self.period)
        stop_period = np.ceil(stop_day * 1.0 / self.period)
        transactions = np.tile(self.transactions, stop_period - start_period)
        
        # Slice section of interest
        offset_in_period = start_day % self.period
        length = stop_day - start_day
        return transactions[offset_in_period:offset_in_period + length]

    def get_balance(self, start_day, stop_day):
        """
        Get summed transactions from start_day to stop_day
        non-inclusive of stop_day
        """
        assert(0 <= start_day and start_day < stop_day)

        # Calc prior balance from full cycles
        num_full_cycles_prior = np.floor(start_day * 1.0/ self.period)
        balance_at_start = self.balance[-1] * num_full_cycles_prior

        # Calc balance from starting partial cycle
        period_start = num_full_cycles_prior * self.period
        if period_start < start_day:
            balance_at_start += np.sum(self.get_transactions(period_start, start_day))

        # Calc balance over days of interest
        balance = np.cumsum(self.get_transactions(start_day, stop_day))
        return balance + balance_at_start

    def add_transaction(self, periodic_transaction):
        """
        Returns false if transactions forced balance into the red
        """
        assert(isinstance(periodic_transaction, PeriodicTransaction))

        # Keep track of periods to allow for shrinking on transaction removal
        self.component_periods.append(periodic_transaction.get_period())

        # Pay cycle period needs to recalculated to accomidate new transaction
        new_period = least_common_multiple(self.period, periodic_transaction.get_period())

        # Period had to increase to accomidate new transaction period LCM
        if new_period != self.period:
            expansion_factor = new_period / self.period
            self.transactions = np.tile(self.transactions, expansion_factor)
        self.period = new_period

        # Add transaction amount to the period
        transaction_days = self._calculate_transaction_days(periodic_transaction.get_period(), periodic_transaction.get_transaction_days())
        self.transactions[transaction_days] += periodic_transaction.get_amount()
        self._update_balance()

    def remove_transaction(self, periodic_transaction):
        """
        Returns false if transactions forced balance into
        the red or not in the pay cycle
        """
        assert(isinstance(periodic_transaction, PeriodicTransaction))

        # Subtract the transaction amount
        transaction_days = self._calculate_transaction_days(periodic_transaction.get_period(), periodic_transaction.get_transaction_days())
        self.transactions[transaction_days] -= periodic_transaction.get_amount()
        self._update_balance()

        # Shink the period if possible, will fail on invalid transaction period
        self.component_periods.remove(periodic_transaction.get_period())
        new_period = least_common_multiple(self.component_periods)

        # Period is shrinking
        if new_period < self.period:
            self.period = new_period
            self.transactions = self.transactions[:new_period]
            self._update_balance()

        return not self.in_the_red()

    def get_discretionary_rate(self, starting_balance=0):
        """
        This is the maximum daily payout rate possible to
        keep the account from ever going into the red.

        Idealy this rate should allow the balance to grow
        by 0 over a pay cycle.

        Only valid if balance is not in the red at any point in the cycle
        """
        assert(not self.in_the_red(starting_balance))
        best_rate = self.balance[-1] * 1.0 / self.period
        possible_rates = (self.balance + starting_balance) * 1.0 / range(1,self.period+1)
        return min(np.min(possible_rates), best_rate)

    def in_the_red(self, starting_balance=0):
        # Either balance is shrinking over the pay cycle so it will eventually go red
        in_the_red = self.balance[-1] < 0
        # Or the balance (offset by starting balance) goes red at any point
        in_the_red |= np.any((self.balance + starting_balance) < 0)
        return in_the_red

    def _calculate_transaction_days(self, transaction_period, transaction_days):
        # Compute all transaction days for the new period
        expansion_factor = self.period / transaction_period

        # Convert to numpy type for element-wise ops
        transaction_days = np.array(transaction_days)
        if expansion_factor > 1:
            # Pay cycle period is larger so need to compute more transaction days        
            transaction_days_in_full_period = np.array([ transaction_days + i * transaction_period for i in xrange(0,expansion_factor) ])
            transaction_days_in_full_period = transaction_days_in_full_period.flatten()
        else:
            # Periods are same
            transaction_days_in_full_period = transaction_days
        
        return transaction_days_in_full_period

    def _update_balance(self):
        self.balance = np.cumsum(self.transactions)

## Helper Functions -----------------------------------

def least_common_multiple(a, b = None):
    """
    If a is list then LCM of whole list

    PARAMS
    a : number, list
    b : number
    """

    # Define functions within LCM scope to make "private"
    def _gcd(a,b):
        """
        Uses Euclid's algo (https://en.wikipedia.org/wiki/Euclidean_algorithm)
        """
        while b != 0:
           temp = b
           b = a % b
           a = temp
        return a

    def _least_common_multiple_helper(a,b):
        return a*b / _gcd(a,b)

    # Have two values
    if b == None:
        # One list, recurse on it
        if len(a) == 1: return a[0]
        return _least_common_multiple_helper(a[0],least_common_multiple(a[1:]))
    else:
        return _least_common_multiple_helper(a,b) 

## Tests ------------------------------------------

def test_least_common_multiple():
    assert(least_common_multiple(1,1) == 1)
    assert(least_common_multiple(0,2) == 0)
    assert(least_common_multiple(3,15) == 15)
    assert(least_common_multiple([3,15]) == 15)
    assert(least_common_multiple([3,15,3,3]) == 15)
    assert(least_common_multiple([3]) == 3)

def test_transaction_add_remove():
    p1 = PayCycle()
    
    # Add transaction of same period
    t1 = DayBasedTransaction(100,1)
    p1.add_transaction(t1)
    assert(p1.get_period() == 1)
    assert(np.array_equal(p1.get_balance(0,1), [100]))
    assert(np.array_equal(p1.get_transactions(0,1), [100]))
    assert(np.array_equal(p1.get_transactions(0,3), [100, 100, 100]))
    assert(np.array_equal(p1.get_balance(0,3), [100, 200, 300]))
    assert(np.array_equal(p1.get_balance(2,3), [300]))

    # Add transaction of longer period
    t2 = DayBasedTransaction(-50, 6)
    p1.add_transaction(t2)
    assert(p1.get_period() == 6)
    transactions = [50, 100, 100, 100, 100, 100]
    assert(np.array_equal(p1.get_transactions(0,6), transactions))
    assert(np.array_equal(p1.get_balance(0,6), np.cumsum(transactions)))

    # Add transaction of shorter period
    t3 = DayBasedTransaction(25, 3, 1)
    p1.add_transaction(t3)
    assert(p1.get_period() == 6)
    assert(np.array_equal(p1.get_transactions(0,6), [50, 125, 100, 100, 125, 100]))
    assert(np.array_equal(p1.get_transactions(0,7), [50, 125, 100, 100, 125, 100, 50]))
    assert(np.array_equal(p1.get_transactions(1,7), [125, 100, 100, 125, 100, 50]))

    # Test add and remove
    p2 = PayCycle()

    # Add transaction of longer period
    t4 = DayBasedTransaction(100,2)
    p2.add_transaction(t4)
    assert(p2.get_period() == 2)
    assert(np.array_equal(p2.get_transactions(0,2), [100, 0]))
    assert(np.array_equal(p2.get_balance(0,2), [100, 100]))

    # Add another transaction of longer period
    t5 = DayBasedTransaction(50,4,2)
    p2.add_transaction(t5)
    assert(p2.get_period() == 4)
    assert(np.array_equal(p2.get_transactions(0,4), [100, 0, 150, 0]))
    assert(np.array_equal(p2.get_balance(0,4), [100, 100, 250, 250]))

    # Remove first transaction
    p2.remove_transaction(t4)
    assert(p2.get_period() == 4)
    assert(np.array_equal(p2.get_transactions(0,4), [0, 0, 50, 0]))
    assert(np.array_equal(p2.get_balance(0,4), [0, 0, 50, 50]))

    # Remove second transaction
    p2.remove_transaction(t5)
    assert(p2.get_period() == 1)
    assert(np.array_equal(p2.get_transactions(0,4), [0, 0, 0, 0]))
    assert(np.array_equal(p2.get_balance(0,1), [0]))

def test_discretionary_rate():
    p = PayCycle()
    
    # No discretionary funds
    assert(p.get_discretionary_rate() == 0)

    # With starting balance still can't overspend balance
    assert(p.get_discretionary_rate(5) == 0)

    # Add income
    p.add_transaction(DayBasedTransaction(2,3))
    assert(np.array_equal(p.get_balance(0,3), [2, 2, 2]))
    assert(p.get_discretionary_rate() == 2.0/3)
    assert(p.get_discretionary_rate(10) == 2.0/3)

    # Add expense, no funds for discretionary
    p.add_transaction(DayBasedTransaction(-2,3,1))
    assert(np.array_equal(p.get_balance(0,3), [2, 0, 0]))
    assert(p.get_discretionary_rate() == 0)
    assert(p.get_discretionary_rate(10) == 0)

    # Add income, funds later in the pay cycle
    p.add_transaction(DayBasedTransaction(3,3,2))
    assert(np.array_equal(p.get_balance(0,3), [2, 0, 3]))
    # Cannot disperse daily to avoid going red on 0 balance day
    assert(p.get_discretionary_rate() == 0)
    assert(p.get_discretionary_rate(1) == .5)
    assert(p.get_discretionary_rate(2) == 1)

def test_in_the_red():
    p = PayCycle()
    
    assert(not p.in_the_red())

    # Add expense
    assert(not p.add_transaction(DayBasedTransaction(-1,1)))
    assert(np.array_equal(p.get_balance(0,1), [-1]))
    assert(p.in_the_red())

    # Add income
    assert(not p.add_transaction(DayBasedTransaction(1,3)))
    assert(np.array_equal(p.get_balance(0,3), [0, -1, -2]))
    assert(p.in_the_red())
    
    # Add income
    assert(not p.add_transaction(DayBasedTransaction(2,3,2)))
    assert(np.array_equal(p.get_balance(0,3), [0, -1, 0]))
    assert(p.in_the_red())
    assert(not p.in_the_red(1))

if __name__ == '__main__':
    print 'Running pay cycle test --',
    test_least_common_multiple()
    test_transaction_add_remove()
    test_discretionary_rate()
    test_in_the_red()
    print 'pass'