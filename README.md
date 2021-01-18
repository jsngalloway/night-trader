# Night Trader
*Day trading doesn't stop at night*
### Project plan
```
nighttrader/
|
|--- nighttrader/
|    |--- __init__.py
|    |--- datasourcer.py (gets from API and maintains history of commodity value)
|    |--- predictors/
|    |    |--- __init__.py
|    |    |--- linear.py (performs basic linear regression to determine momentum)
|    |
|    |--- trader.py (buys or sells given commodity in given amount)
|    |--- runner.py (auths, gets data, runs predictions, ~makes trades~)
|
|--- data/
|
|--- tests/
|    |--- datasourcer_tests.py
|    |--- predictors/
|    |    |--- linear_tests.py
|    |
|    |--- trader_tests.py
|    |--- runner_tests.py
|
|--- .gitignore
|
|--- LICENSE
|
|--- README.md
```
