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
