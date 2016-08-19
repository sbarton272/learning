import numpy as np

## Transaction Classes --------------------------------


class Transaction(object):
    """
    Abstract base class for all transactions

    PARAMS
    amount : number, positive for income, negative for expense
    """
    def __init__(self, amount):
        self.amount = amount

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
            and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return type(self).__name__ + '(' + str(self.__dict__) + ')'

    def __repr__(self):
        return str(self)

    def get_amount(self):
        return self.amount

    def get_transaction_days(self):
        pass

class PeriodicTransaction(Transaction):
    """
    Abstract base class for all periodic transactions

    PARAMS
    amount : number, positive for income, negative for expense
    """
    def __init__(self, amount):
        super(PeriodicTransaction, self).__init__(amount)

    def get_period(self):
        pass

class DayBasedTransaction(PeriodicTransaction):
    """
    Transaction with a period in days.

    Ex. Biweekly or every 14 days

    PARAMS
    amount :            See base class (PeriodicTransaction)
    period_in_days :    number, transaction repeats this often
    day_offset :        number of days until this transaction starts
                        into the cycle. Ex) Biweekly on 3rd day
                        This value can also be thought of as phase offset
                        and is always less than the period_in_days
    """

    def __init__(self, amount, period_in_days, day_offset=0):
        super(DayBasedTransaction, self).__init__(amount)
        
        assert(period_in_days > 0)
        self.period_in_days = period_in_days

        assert(0 <= day_offset and day_offset < period_in_days)        
        self.day_offset = day_offset

    def get_period(self):
        return self.period_in_days

    def get_transaction_days(self):
        # Within one period the transaction day takes place at the offset
        return [self.day_offset]

    def __str__(self):
        return "%s(amount:%d, period:%d, offset:%d)" % (type(self).__name__, self.amount, self.period_in_days, self.day_offset)

class MonthlyTransaction(PeriodicTransaction):
    """
    Transaction occuring monthly. Periodic every 4 years

    Ex. 1st of every month

    PARAMS
    amount :            See base class (PeriodicTransaction)
    day_of_month :      number, day starts at 0 (1st of month)
                        - defaults to 0
                        - range 0-30
                        - round to last day on short months
                          Ex) day_of_month=30 translates to Jan 31,
                              Feb 28, Mar 31, etc.
    day_offset_from_leap_year : Number of days since end of prev leap year
    """
    # Monthly transactions will repeat every 4 years thanks to leap year
    # I'm making an assumption that the leap year falls within the 4th year
    MONTH_LENGTHS_4_YR = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31] * 3 + [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    PERIOD_LENGTH_DAYS = sum(MONTH_LENGTHS_4_YR)
    # Start at day 0 and ignore final month length
    DAY_OF_MONTH_START = np.insert(np.cumsum(MONTH_LENGTHS_4_YR[:-1]), 0, 0)

    def __init__(self, amount, day_of_month=0, day_offset_from_leap_year=0):
        super(MonthlyTransaction, self).__init__(amount)
        
        assert(0 <= day_of_month and day_of_month < 31)
        self.day_of_month = day_of_month

        # Calculate payment days, using offset capped by month duration, note off by 1 because our month starts at day 0
        capped_day_of_month = [ min(day_of_month, month_len - 1) for month_len in self.MONTH_LENGTHS_4_YR ]
        transaction_days = self.DAY_OF_MONTH_START + capped_day_of_month

        # Calculate out over two cycles, shift by offset from leap year and take first 4 yr worth of positive transaction days
        transaction_days = np.append(transaction_days, transaction_days + self.PERIOD_LENGTH_DAYS)
        transaction_days = np.tile(transaction_days, 2) - day_offset_from_leap_year
        first_pos_ind = np.argmax(transaction_days >= 0)
        self.transaction_days = transaction_days[first_pos_ind:first_pos_ind + len(self.MONTH_LENGTHS_4_YR)]

    def get_period(self):
        return self.PERIOD_LENGTH_DAYS

    def get_transaction_days(self):
        return self.transaction_days

    def __str__(self):
        return "%s(amount:%d, day of month:%d)" % (type(self).__name__, self.amount, self.day_of_month)

class AnnualTransaction(PeriodicTransaction):
    """
    Transaction occuring annually. Periodic every 4 years

    Ex. 5th of every year

    PARAMS
    amount :           See base class (PeriodicTransaction)
    day_of_year :      number, day starts at 0 (1st of year)
                        - defaults to 0
                        - range 0-365
                        - 365 rounds to last day of year in
                          non-leap years
    day_offset_from_leap_year : Number of days since end of prev leap year
    """
    # Annual transactions will repeat every 4 years thanks to leap year
    # I'm making an assumption that the leap year falls within the 4th year
    YEAR_LENGTHS_4_YR = [365] * 3 + [366]
    PERIOD_LENGTH_DAYS = sum(YEAR_LENGTHS_4_YR)
    # Start at day 0 and ignore final year length
    DAY_OF_YEAR_START = np.insert(np.cumsum(YEAR_LENGTHS_4_YR[:-1]), 0, 0)

    def __init__(self, amount, day_of_year=0, day_offset_from_leap_year=0):
        super(AnnualTransaction, self).__init__(amount)
        
        assert(0 <= day_of_year and day_of_year < 366)
        assert(0 <= day_offset_from_leap_year and day_offset_from_leap_year < self.PERIOD_LENGTH_DAYS)
        self.day_of_year = day_of_year

        # Calculate payment days, using offset capped by year duration, note off by 1 because our year starts at day 0
        capped_day_of_year = [ min(day_of_year, year_len - 1) for year_len in self.YEAR_LENGTHS_4_YR ]
        transaction_days = self.DAY_OF_YEAR_START + capped_day_of_year
        
        # Calculate out over two cycles, shift by offset from leap year and take first 4 yr worth of positive transaction days
        transaction_days = np.append(transaction_days, transaction_days + self.PERIOD_LENGTH_DAYS)
        transaction_days = np.tile(transaction_days, 2) - day_offset_from_leap_year
        first_pos_ind = np.argmax(transaction_days >= 0)
        self.transaction_days = transaction_days[first_pos_ind:first_pos_ind + len(self.YEAR_LENGTHS_4_YR)]

    def get_period(self):
        return self.PERIOD_LENGTH_DAYS

    def get_transaction_days(self):
        return self.transaction_days
    
    def __str__(self):
        return "%s(amount:%d, day of month:%d)" % (type(self).__name__, self.amount, self.day_of_year)

class ExpenseGoal(Transaction):
    """
    Goals are savings targets that are treated similarly to expenses.
    A goal has a specified amount and a target date. A duration
    can also be set which specifies over which days you'll be saving
    for the goal.

    If duration is not set then it is assumed that we'll begin
    saving for the goal immediatly

    PARAMS
    amount : number, positive
    day_completed : day that goal will be completed by, greater than day 0
    duration : length of goal, inclusive of target_day
    """
    def __init__(self, amount, day_completed, duration=None):
        assert(amount >= 0)
        super(ExpenseGoal, self).__init__(-amount)

        assert(day_completed > 0)
        self.day_completed = day_completed

        # Length of goal, if None assume by the start date
        assert(duration == None or (0 < duration and duration <= day_completed))
        if duration == None:
            duration = day_completed
        self.duration = duration

    def get_transaction_days(self):
        # Savings withheld towards goal daily
        return np.arange(self.day_completed - self.duration, self.day_completed)

    def get_amount(self):
        return float(self.amount) / self.duration

    def get_first_day(self):
        return self.day_completed - self.duration

    def get_duration(self):
        return self.duration
    
    def __str__(self):
        return "%s(amount:%d, completion day:%d, duration:%d)" % (type(self).__name__, self.amount, self.day_completed, self.duration)

## Tests ------------------------------------------

def test_transaction_classes():

    t = DayBasedTransaction(100, 14, 2) # Biweekly income
    assert(t.get_period() == 14)
    assert(t.get_amount() == 100)
    assert(np.array_equal(t.get_transaction_days(), [2]))

    t = MonthlyTransaction(1)
    assert(t.get_period() == 1461)
    assert(t.get_amount() == 1)
    # Jan transaction
    assert(t.get_transaction_days()[0] == 0)
    # Feb transaction
    assert(t.get_transaction_days()[1] == 31)
    # March transaction    
    assert(t.get_transaction_days()[2] == 31 + 28)
    # March of leap year (4th year of period)
    assert(t.get_transaction_days()[2 + 12*3] == 31 + 29 + 365*3)

    # Test rounding to last day of the month
    t = MonthlyTransaction(1, 30)
    assert(t.get_period() == 1461)
    assert(t.get_amount() == 1)
    # Jan transaction
    assert(t.get_transaction_days()[0] == 30)
    # Feb transaction
    assert(t.get_transaction_days()[1] == 30 + 28)
    # March transaction
    assert(t.get_transaction_days()[2] == 30 + 28 + 31)

    # Test offset by 3 years (fall within leap year)
    t = MonthlyTransaction(1, 30, 365*3)
    assert(t.get_period() == 1461)
    assert(t.get_amount() == 1)
    # Jan transaction
    assert(t.get_transaction_days()[0] == 30)
    # Feb transaction (leap year len)
    assert(t.get_transaction_days()[1] == 30 + 29)
    # March transaction
    assert(t.get_transaction_days()[2] == 30 + 29 + 31)

    # Test offset by 3 years and 5 days (fall within leap year)
    t = MonthlyTransaction(1, 30, 365*3 + 5)
    assert(t.get_period() == 1461)
    assert(t.get_amount() == 1)
    # Jan transaction
    assert(t.get_transaction_days()[0] == 25)
    # Feb transaction (leap year len)
    assert(t.get_transaction_days()[1] == 25 + 29)
    # March transaction
    assert(t.get_transaction_days()[2] == 25 + 29 + 31)

    t = AnnualTransaction(1)
    assert(t.get_period() == 1461)
    assert(t.get_amount() == 1)
    assert(np.array_equal(t.get_transaction_days(), [0, 365, 365*2, 365*3]))

    # Test non-leap year rounding
    t = AnnualTransaction(-1, 365)
    assert(t.get_period() == 1461)
    assert(t.get_amount() == -1)
    assert(np.array_equal(t.get_transaction_days(), [364, 364 + 365, 364 + 365*2, 365*4]))

    # Test offset by 1 year
    t = AnnualTransaction(-1, 0, 365)
    assert(t.get_period() == 1461)
    assert(t.get_amount() == -1)
    assert(np.array_equal(t.get_transaction_days(), [0, 365, 365*2, 365*3 + 1]))

    # Test offset by 3 year (aka first year is leap)
    t = AnnualTransaction(-1, 0, 365*3)
    assert(t.get_period() == 1461)
    assert(t.get_amount() == -1)
    assert(np.array_equal(t.get_transaction_days(), [0, 366, 365*2 + 1, 365*3 + 1]))

    # Test offset (1 year, 10 days) and non-leap year rounding
    t = AnnualTransaction(-1, 365, 365 + 10)
    assert(t.get_period() == 1461)
    assert(t.get_amount() == -1)
    # Transaction days fall in [reg year, reg year, leap year, reg year]
    assert(np.array_equal(t.get_transaction_days(), [364 - 10, 365 + 364 - 10, 365*2 + 1 + 364 - 10, 365*3 + 1 + 364 - 10]))

    # Test goal
    t = ExpenseGoal(3,3)
    assert(t.get_amount() == -1)
    assert(np.array_equal(t.get_transaction_days(), [0,1,2]))
    assert(t.get_first_day() == 0)
    assert(t.get_duration() == 3)

    # Test goal with shorted duration
    t = ExpenseGoal(3,3,1)
    assert(t.get_amount() == -3)
    assert(np.array_equal(t.get_transaction_days(), [2]))
    assert(t.get_first_day() == 2)
    assert(t.get_duration() == 1)

if __name__ == '__main__':
    print 'Running transactions test --',
    test_transaction_classes()
    print 'pass'