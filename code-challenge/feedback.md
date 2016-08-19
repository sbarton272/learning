# Feedback

So this work didn't pass muster....

Obviously I'm more out of practice than anticipated.

## Initial thoughts
- SW at Nest has been lots of small changes, I've lost sense of larger design
- My python best practices knowledge is lacking
- **(S) I should have created greater clarity around the requirements and key interfaces**
- Bottom-up design lead to lots of rethinking around logic blocks which made the effort take longer
- Perhaps there were more python components I could have taken advantage of?
- (S) Take a day or two away from the project to come back later and review
- (T) Don't work when I'm really sick (or tired) because quality will suffer
- (C) Write test cases as I go
- (S) Make use of a python test framework
- (S) Make use of python doc strings on all methods
- (C) Break down the larger problem
- (S) Stay humble because I have a lot to learn
- Better documentation, try pydoc

## Specific sw concerns
- Decide on a commit style/format
- Docstrings are important in python
- The periodic vs not transaction breakdown was confusing
- The aggregation layer was not truly necessary
- Pylint is worth a shot, also take a look at a style guide https://www.python.org/dev/peps/pep-0008/
- Check out type annotations :)
- Was I designing around balances or transactions?
- How would the account move forward in time?
- 

## A cleaner architecture
- Transactions are ok
- Expense goal was hackey
- Should have been a way for Account to treat all transactions the same
- Daily allowance calculator is the only part that cares about periodicity