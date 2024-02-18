# Autotraders
[![Downloads](https://static.pepy.tech/badge/autotraders)](https://pepy.tech/project/autotraders)
[![Python package](https://github.com/cosmictraders/autotraders/actions/workflows/python-package.yml/badge.svg)](https://github.com/cosmictraders/autotraders/actions/workflows/python-package.yml)

A spacetraders API focused on automation and ease of use
## Usage
First you need a client, which can be generated 
```python
from autotraders import session
s = session.get_session("YOUR_TOKEN_HERE")
```
And now you're all set to use they actual API.

## Ships

```python
from autotraders.ship import Ship
from autotraders.session import get_session

# create a session here
session = get_session("YOUR TOKEN HERE")
ship = Ship("SYMBOL-Here", session)  # This makes an API request
ships = Ship.all(session)  # This also only makes one API request
ship.dock()
ship.refuel()
ship.orbit()  # All these functions make API calls (one each), but the line below doesn't make any
print(ship.fuel.current + "/" + ship.fuel.total)
```
## Contract
```python
from autotraders.faction.contract import Contract
from autotraders.session import get_session

# create a session here
session = get_session("YOUR TOKEN HERE")
contract = Contract("id-here", session)
contracts = Contract.all(session)
contract.accept()
print(contract.accepted) # True
contract.deliver("SHIP_SYMBOL", "ALUMINUM_ORE", 30)
contract.fulfill()
print(contract.fulfilled) # True
```
