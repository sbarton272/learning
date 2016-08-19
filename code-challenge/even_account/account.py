"""
Account managment
"""

import numpy as np
from transactions import DayBasedTransaction, MonthlyTransaction, AnnualTransaction
from transactions import ExpenseGoal
from transactions import PeriodicTransaction, Transaction
from pay_cycle import PayCycle
from expense_goal_aggregator import ExpenseGoalAggregator

## Account ------------------------------------------

class Account(object):
    """
    Account which contains has associated incomes and expenses
    and maintains a balance

    Day 0 is the beginning and is the day the account opens
    and pay cycles are calculated to start on day 0

    PARAMS
    starting_balance : Defaults to 0, needs to be positive
    """
    def __init__(self, starting_balance = 0):
        # Start with an empty pay cycle and no payments
        self.pay_cycle = PayCycle()
        self.goals_ag = ExpenseGoalAggregator()

        assert(starting_balance >= 0)
        self.starting_balance = starting_balance

        # Keep track of all transactions
        self.transactions = {}
        self.transaction_counter = 0

    def get_balance(self, start_day, stop_day = None, include_daily_allowance = False):
        """
        Get balance values for day range, days start at 0
        Does not include stop_day. Balance is what is 
        available after the day's transactions have occurred
        """
        if stop_day == None:
            stop_day = start_day + 1
        assert(0 <= start_day and start_day < stop_day)

        balance = self.pay_cycle.get_balance(start_day, stop_day) + self.goals_ag.get_balance(start_day, stop_day) + self.starting_balance
        if include_daily_allowance:
            allowance = self.get_daily_allowance()
            balance -= start_day * allowance
            balance -= np.cumsum(np.ones(stop_day - start_day) * allowance)
        return balance

    def get_transactions(self, start_day, stop_day = None, include_daily_allowance = False):
        """
        Get summed transactions from start_day to stop_day
        non-inclusive of stop_day
        """
        if stop_day == None:
            stop_day = start_day + 1
        assert(0 <= start_day and start_day < stop_day)
        
        transactions = self.pay_cycle.get_transactions(start_day, stop_day) + self.goals_ag.get_transactions(start_day, stop_day)
        if include_daily_allowance:
            transactions -= self.get_daily_allowance()
        return transactions

    def get_constituent_transactions(self):
        return self.transactions

    def add_transaction(self, transaction):
        """
        Returns true if added and false if
        adding this adding this transaction would
        have put the account in the red.
        """
        assert(isinstance(transaction, Transaction))
        
        transaction_added = True
        if isinstance(transaction, PeriodicTransaction):
            self.pay_cycle.add_transaction(transaction)

            if self.pay_cycle.in_the_red(self.starting_balance):
                # Unable to add transaction
                self.pay_cycle.remove_transaction(transaction)
                transaction_added = False

        elif isinstance(transaction, ExpenseGoal):
            self.goals_ag.add_goal(transaction)

            if self.goals_ag.in_the_red(self.get_discretionary_rate()):
                # Unable to add transaction
                self.goals_ag.remove_goal(transaction)
                transaction_added = False

        else:
            transaction_added = False

        if transaction_added:
            self.transactions[self.transaction_counter] = transaction
            self.transaction_counter += 1
        return transaction_added

    def remove_transaction(self, transaction_id):
        """
        Returns true if added and false if
        adding this adding this transaction would
        have put the account in the red.
        """
        if transaction_id not in self.transactions:
            return False

        transaction = self.transactions[transaction_id]

        # Behave differently depending on the transaction type
        transaction_removed = True
        if isinstance(transaction, PeriodicTransaction):
            in_the_red = not self.pay_cycle.remove_transaction(transaction)

            if in_the_red or self.goals_ag.in_the_red(self.get_discretionary_rate()):
                # Unable to remove transaction
                self.pay_cycle.add_transaction(transaction)
                transaction_removed = False

        elif isinstance(transaction, ExpenseGoal):
            # Removing goals will not put us in the red because they are always expenses
            transaction_removed = self.goals_ag.remove_goal(transaction)

        if transaction_removed:
            self.transactions.pop(transaction_id)
        return transaction_removed

    def get_daily_allowance(self):
        """
        This is the maximum daily payout rate possible to
        keep the account from ever going into the red.

        This amount is fixed for all time and is less the
        amount set aside for goals.
        """
        return self.pay_cycle.get_discretionary_rate(self.starting_balance) + self.goals_ag.get_largest_goal_expense()

    def get_discretionary_rate(self):
        """
        This is the amount of money available daily
        from periodic transactions. It takes into
        account the starting balance as well.
        """
        return self.pay_cycle.get_discretionary_rate(self.starting_balance)

## Tests ------------------------------------------

def test_account_transaction_add_remove():
    a = Account()

    # Test starts with nothing
    assert(np.array_equal(a.get_balance(0,4), [0,0,0,0]))

    # Basic transaction
    t1 = DayBasedTransaction(25, 3)
    assert(a.add_transaction(t1))
    assert(np.array_equal(a.get_balance(0,4), [25,25,25,50]))
    assert(np.array_equal(a.get_balance(1,4), [25,25,50]))
    assert(np.array_equal(a.get_balance(4,7), [50,50,75]))
    assert(np.array_equal(a.get_balance(7,10), [75,75,100]))
    assert(a.get_daily_allowance() == 25.0 / 3)

    t2 = DayBasedTransaction(-5, 3)
    assert(a.add_transaction(t2))
    assert(np.array_equal(a.get_balance(0,4), [20,20,20,40]))
    assert(a.get_daily_allowance() == 20.0 / 3)

    # Test in the red
    t = DayBasedTransaction(-50, 3)
    assert(not a.add_transaction(t))
    # Check that account stayed the same
    assert(np.array_equal(a.get_balance(0,4), [20,20,20,40]))

    # Test unable to remove transaction because not added
    assert(not a.remove_transaction(4))

    # Test unable to remove income first because go into the red
    assert(not a.remove_transaction(0))
    
    # Test remove expense
    assert(a.remove_transaction(1))
    assert(np.array_equal(a.get_balance(0,4), [25,25,25,50]))
    assert(a.get_daily_allowance() == 25.0 / 3)

    # Test remove income
    assert(a.remove_transaction(0))    
    assert(np.array_equal(a.get_balance(0,4), [0,0,0,0]))
    assert(a.get_daily_allowance() == 0)

def test_account_goals():
    a = Account()

    # Test starts with nothing
    assert(np.array_equal(a.get_balance(0,4), [0,0,0,0]))

    # Cannot add goal because not making any money
    t = ExpenseGoal(3,3)
    assert(not a.add_transaction(t))
    assert(np.array_equal(a.get_balance(0,4), [0,0,0,0]))

    # Cannot remove because not added
    assert(not a.remove_transaction(t))
    assert(np.array_equal(a.get_balance(0,4), [0,0,0,0]))

    # Add some income, 1 per day
    t = DayBasedTransaction(1,1)
    assert(a.add_transaction(t))
    assert(np.array_equal(a.get_transactions(0,4), [1,1,1,1]))
    assert(np.array_equal(a.get_balance(0,4), [1,2,3,4]))
    assert(a.get_daily_allowance() == 1)
    assert(a.get_discretionary_rate() == 1)

    # Can now add a goal
    t = ExpenseGoal(3,3)
    assert(a.add_transaction(t))
    assert(np.array_equal(a.get_transactions(0,5), [0,0,0,1,1]))
    assert(np.array_equal(a.get_balance(0,5), [0,0,0,1,2]))
    assert(a.get_daily_allowance() == 0)
    assert(a.get_discretionary_rate() == 1)

def test_get_transactions():
    a = Account(100)

    # Test no transactions to start
    assert(np.array_equal(a.get_transactions(0,4), [0,0,0,0]))
    assert(np.array_equal(a.get_transactions(0,4, True), [0,0,0,0]))

    t = MonthlyTransaction(200,3)
    assert(a.add_transaction(t))
    assert(np.array_equal(a.get_transactions(0,5), [0,0,0,200,0]))

    t = ExpenseGoal(3,3)
    assert(a.add_transaction(t))
    assert(np.array_equal(a.get_transactions(0,5), [-1,-1,-1,200,0]))

def test_account_starting_balance():
    a = Account(1)

    # Test starting balance
    assert(np.array_equal(a.get_balance(0,4), [1,1,1,1]))
    assert(a.get_daily_allowance() == 0)

    t = DayBasedTransaction(2,3)
    assert(a.add_transaction(t))
    assert(np.array_equal(a.get_balance(0,4), [3,3,3,5]))
    assert(np.array_equal(a.get_transactions(0,4), [2,0,0,2]))
    trans = np.array([2,0,0,2]) - (2.0/3)
    assert(np.allclose(a.get_balance(0,4,True), np.cumsum(trans) + 1))
    assert(np.array_equal(a.get_transactions(0,4,True), trans))
    assert(a.get_daily_allowance() == 2.0/3)

    t = DayBasedTransaction(-2,3,1)
    assert(a.add_transaction(t))
    assert(np.array_equal(a.get_balance(0,4), [3,1,1,3]))
    assert(a.get_daily_allowance() == 0)

    t = DayBasedTransaction(3,3,2)
    assert(a.add_transaction(t))
    assert(np.array_equal(a.get_balance(0,4), [3,1,4,6]))
    assert(a.get_daily_allowance() == .5)

if __name__ == '__main__':
    print 'Running account test --',
    test_account_transaction_add_remove()
    test_account_goals()
    test_get_transactions()
    test_account_starting_balance()
    print 'pass'
