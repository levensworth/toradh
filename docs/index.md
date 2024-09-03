# Welcome to Toradh

Your python minimalistic library for better error management and flow control.

## Installation:

Simply run:

```
pip install toradh
```

## Usage

`toradh` has 2 main primitives available for use, `Result` and `Option`.

### `Option`:

The use for the `Option` primitive is to offer a better alternative to the default
`typing.Optional` which translates into `T | None` (where `T` represents any value).

Here you have some examples:

```python
from toradh import Optional, Option
from dataclasses import dataclass
from contextlib import suppress


@dataclass
class User:
    id: int
    surname: Optional[str]

user = User(id=1, surname=Option.of('doe'))
user.surname.is_some() # returns True
user.surname.unwrap() # 'doe'
user.surname.unwrap_or('default')# 'doe'

empty_user = User(id=1, surname=Option.of(None))
empty_user.surname.is_some() # returns False
with suppress(ValueError):
    empty_user.surname.unwrap() # raise ValueError
empty_user.surname.unwrap_or('default')# 'default'

```

### `Result`:
```python

from toradh import Result, Ok, Err

def make_payment(to: str, amount: int) -> Result[bool, KeyError | ValueError]:
    """Function which performs a payment transaction to a given address by incrementing 
    it's original balance by the given amount.
    
    Args:
        to (str): Address to which the deposit will be given.
        amount (int): Amount to deposit.

    Return:
        Result[bool, KeyError | ValueError]: True if operation successfully completed, False
        if the payment failed for runtime reasons.
        
        Errors:
            KeyError: Means the address does not exists
            ValueError: Means the amount is not a positive integer.
    """
    return Ok(True)

def handle_successful_payment(*args) -> None:
    ...



payment_result = make_payment(to='0x001', amount=-100)

match payment_result.kind():
    case True:
        # then it was a successful invocation
        handle_successful_payment(...)
    case False:
        handle_failed_payment(...)
    case KeyError():
        # the address was wrong
        alert_wrong_address(...)
    case ValueError():
        # the amount was incorrect
        alert_illegal_amount(...)

```

