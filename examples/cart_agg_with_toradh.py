from dataclasses import dataclass, field
import logging
from typing import Protocol

from toradh.result import Option, Result


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
    if cart.is_none():
        raise CartNotFoundError()

    service_res = service.add_item(cart, item=item)
    match service_res.kind():
        case Cart():
            repository.update_cart_items(service_res.unwrap())

        case DuplicateItemInCartError():
            logging.error(f"Item {item} already exists in cart {cart_id}")

        case InvalidItemError():
            logging.error(f"Item {item} is not valid for cart {cart}")
