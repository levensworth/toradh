# Why use Result

Let's imagine we are developing an application which uses `carts`, and we need to 
create the `Aggregate` for `add_to_cart` as you can see below:

```python
from dataclasses import dataclass, field
import logging
from typing import Protocol, Optional


@dataclass
class Cart:
    id: int
    items: list[str] = field(default_factory=list)


class CartService(Protocol):
    def add_item(self, cart: Cart, item: str) -> Cart: ...


class CartRepository(Protocol):
    def get_by_id(self, id: int) -> Optional[Cart]: ...

    def update_cart_items(self, cart: Cart) -> bool: ...


def add_to_cart_aggregate(
    cart_id: int, item: str, service: CartService, repository: CartRepository
) -> None:
    cart = repository.get_by_id(cart_id)
    if not cart:
        logging.error(f"cart {cart_id} not found")
        return

    updated = service.add_item(cart, item=item)
    repository.update_cart_items(updated)

```

The problem which this code is that the `CartService` and  `CartRepository` both have completely 
valid reasons for why they might fail in ways that are not clear from just ready the code above.

- What if the the item already exists in the cart?
- what if the item can't be part of the cart for business related reasons?

The code just isn't expressive enough.

## Make code more expressive:

Let's look at the above example but using `Result`:

```python
from dataclasses import dataclass, field
import logging
from typing import Protocol

from toradh import  Option, Result



@dataclass
class Cart:
    id: int
    items: list[str] = field(default_factory=list)


class InvalidItemError(RuntimeError): ...


class DuplicateItemInCartError(RuntimeError): ...


class CartNotFoundError(RuntimeError): ...


class CartService(Protocol):
    def add_item(
        self, cart: Cart, item: str
    ) -> Result[Cart, InvalidItemError | DuplicateItemInCartError]: ...


class CartRepository(Protocol):
    def get_by_id(self, id: int) -> Option[Cart]: ...

    def update_cart_items(self, cart: Cart) -> Result[bool, CartNotFoundError]: ...


def add_to_cart_aggregate(
    cart_id: int, item: str, service: CartService, repository: CartRepository
) -> None:
    cart = repository.get_by_id(cart_id)
    if cart.is_nothing():
        raise CartNotFoundError()

    service_res = service.add_item(cart, item=item)
    match service_res.kind():
        case Cart():
            repository.update_cart_items(service_res.unwrap())

        case DuplicateItemInCartError():
            logging.error(f"Item {item} already exists in cart {cart_id}")

        case InvalidItemError():
            logging.error(f"Item {item} is not valid for cart {cart}")

```

Now this is better! You can see the different possible flows within the `add_to_cart_aggregate`, without leaving 
the same abstraction layer you can understand what happens in any case. That right there is the main compelling reason 
to use this library.

## Not everything should be expressive:
We present a few primitives for you to better express different possible flows of your application. But just because 
you have the primitives does not necessarily mean you *should* use then everywhere!

You should use `Result` as opposed to rising an `Exception` only when you consider that the exception is *recoverable*
or manageable by the invoker.

You can rely on Python's error handling when the behavior is impossible to recover from, an example would be a 
`out of memory exception` or a `max recursive calls`. Basically whatever you consider as part of your program which 
does not align well with *railway programming* concepts should be kept out of the loop.

