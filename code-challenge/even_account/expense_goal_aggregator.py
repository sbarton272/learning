"""
Class to combine non-periodic transactions
"""

import numpy as np
from transactions import ExpenseGoal

## ExpenseGoalAggregator ------------------------------------------

class ExpenseGoalAggregator(object):
    """
    This class combines ExpenseGoal objs into a single set of
    goals expenses per day.

    The assumption is that the account holder saves the same amount
    each day towards the goal up until the deadline. Therefore
    goals are treated like expenses in terms of account balance and
    transactions. Aka money set aside for goals is subtracted from
    daily discretionary spending.
    """
    def __init__(self):
        # Start with no transactions
        self.transactions = np.array([0])
        self.first_day = 0
        self._update_balance()
        self.goals = []

    def get_first_day(self):
        return self.first_day

    def get_completed_by_day(self):
        return self.first_day + len(self.transactions)

    def get_transactions(self, start_day, stop_day):
        """
        Get summed transactions from start_day to stop_day
        non-inclusive of stop_day
        """
        assert(0 <= start_day and start_day < stop_day)
        
        transactions = np.zeros(stop_day - start_day)

        # Extract overlapping section with goals
        last_goal_day = self.first_day + len(self.transactions)
        if (start_day < last_goal_day) and (stop_day > self.first_day):
            # Get overlaping section
            overlap_start = max(self.first_day, start_day) - self.first_day
            overlap_end = min(last_goal_day, stop_day) - self.first_day
            overlap = self.transactions[overlap_start:overlap_end]
            
            # Add overlap
            start_offset = max(self.first_day, start_day) - start_day
            transactions[start_offset:start_offset+len(overlap)] += overlap

        return transactions 

    def get_balance(self, start_day, stop_day):
        """
        Get summed transactions from start_day to stop_day
        non-inclusive of stop_day
        """
        assert(0 <= start_day and start_day < stop_day)
        
        # Get prior balance
        prior_balance = 0
        if start_day > self.first_day:
            prior_balance = np.sum(self.get_transactions(self.first_day, stop_day))

        transactions = self.get_transactions(start_day, stop_day)
        return np.cumsum(transactions) + prior_balance

    def get_largest_goal_expense(self):
        return np.min(self.transactions)

    def add_goal(self, goal):
        """
        Returns false if transactions sum on any day to larger
        than daily allowance
        """
        assert(isinstance(goal, ExpenseGoal))
        self.goals.append(goal)
        self._aggregate_goals()
        self._update_balance()
        return True

    def remove_goal(self, goal):
        """
        Returns false if the goal wasn't already present or
        if removing the goal causes the balance to be less than
        the daily_allowance
        """
        assert(isinstance(goal, ExpenseGoal))

        if goal not in self.goals:
            return False

        # Can remove the goal
        self.goals.remove(goal)
        self._aggregate_goals()
        self._update_balance()
        return True

    def in_the_red(self, daily_allowance):
        """
        If goal daily expenditures ever account for more
        than our fixed daily rate than we are in trouble
        """
        return (self.get_largest_goal_expense() + daily_allowance) < 0

    def _aggregate_goals(self):
        if len(self.goals) == 0:
            self.transactions = np.array([0])
            self.first_day = 0
            return

        first_day = np.min([g.get_first_day() for g in self.goals])
        completed_day = np.max([g.get_first_day() + g.get_duration() for g in self.goals])

        # Fill in transactions
        transactions = np.zeros(completed_day - first_day)
        for g in self.goals:
            transactions[g.get_transaction_days() - first_day] += g.get_amount()

        self.first_day = first_day
        self.transactions = transactions

    def _update_balance(self):
        self.balance = np.cumsum(self.transactions)

## Tests ------------------------------------------

def test_add_remove_goal():
    e = ExpenseGoalAggregator()

    # No goals yet
    assert(e.get_first_day() == 0)
    assert(np.array_equal(e.get_transactions(0,1),[0]))
    assert(np.array_equal(e.get_balance(0,2),[0,0]))

    g = ExpenseGoal(3,4,3)

    # Add a goal
    assert(e.add_goal(g))
    assert(e.get_first_day() == 1)
    assert(np.array_equal(e.get_transactions(1,4),[-1, -1, -1]))
    assert(np.array_equal(e.get_balance(0,4),[0, -1, -2, -3]))  
    assert(np.array_equal(e.get_balance(4,5),[-3]))  

    # Add a goal
    g = ExpenseGoal(5,5)
    assert(e.add_goal(g))
    assert(e.get_first_day() == 0)
    assert(np.array_equal(e.get_transactions(0,5),[-1, -2, -2, -2, -1]))
    assert(np.array_equal(e.get_balance(0,5),[-1, -3, -5, -7, -8]))

    # Try removing non-present goal
    g = ExpenseGoal(43,42)
    assert(not e.remove_goal(g))
    assert(e.get_first_day() == 0)
    assert(np.array_equal(e.get_transactions(0,5),[-1, -2, -2, -2, -1]))
    assert(np.array_equal(e.get_balance(0,5),[-1, -3, -5, -7, -8]))

    # Remove goal
    g = ExpenseGoal(5,5)
    assert(e.remove_goal(g))
    assert(e.get_first_day() == 1)
    assert(np.array_equal(e.get_transactions(1,4),[-1, -1, -1]))
    assert(np.array_equal(e.get_balance(1,4),[-1, -2, -3]))  

    # Remove last goal
    g = ExpenseGoal(3,4,3)
    assert(e.remove_goal(g))
    assert(e.get_first_day() == 0)
    assert(np.array_equal(e.get_transactions(0,1),[0]))
    assert(np.array_equal(e.get_balance(0,2),[0,0]))

def test_get_transactions():
    e = ExpenseGoalAggregator()

    # No transactions yet
    assert(np.array_equal(e.get_transactions(0,1),[0]))

    g = ExpenseGoal(5,6,5)
    assert(e.add_goal(g))
    assert(e.get_first_day() == 1)
    assert(np.array_equal(e.get_transactions(1,2),[-1]))
    assert(np.array_equal(e.get_transactions(1,6),[-1, -1, -1, -1, -1]))
    assert(np.array_equal(e.get_transactions(0,7),[0, -1, -1, -1, -1, -1, 0]))
    assert(np.array_equal(e.get_transactions(0,1),[0]))
    assert(np.array_equal(e.get_transactions(6,7),[0]))

def test_in_the_red():
    e = ExpenseGoalAggregator()

    # No transactions yet
    assert(not e.in_the_red(0))
    assert(e.in_the_red(-1))

    g = ExpenseGoal(5,6,5)
    assert(e.add_goal(g))
    assert(e.get_first_day() == 1)
    assert(np.array_equal(e.get_transactions(0,7),[0, -1, -1, -1, -1, -1, 0]))
    assert(e.in_the_red(0))
    assert(not e.in_the_red(1))
    assert(not e.in_the_red(2))

if __name__ == '__main__':
    print 'Running goal ag test --',
    test_add_remove_goal()
    test_get_transactions()
    test_in_the_red()
    print 'pass'