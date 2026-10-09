"""Classes that DO apply SOLID."""
from dataclasses import dataclass, field
from typing import Protocol


@dataclass
class Order:
    customer_email: str
    items: dict[str, float] = field(default_factory=dict)  # name -> price
    total: float = 0.0

    def add_item(self, name: str, price: float) -> None:
        """Invariants are protected inside the entity."""
        if price <= 0:
            raise ValueError(f"Invalid price for {name!r}: {price}")
        if name in self.items:
            raise ValueError(f"Duplicate item: {name!r}")
        self.items[name] = price


# --- Abstractions (ISP: small interfaces, DIP: the service depends on them) ---
class DiscountPolicy(Protocol):
    def apply(self, subtotal: float) -> float: ...


class OrderRepository(Protocol):
    def save(self, order: Order) -> None: ...


class Notifier(Protocol):
    def send(self, to: str, message: str) -> None: ...


# --- OCP + LSP: new policies without touching OrderService; all interchangeable ---
class NoDiscount:
    def apply(self, subtotal: float) -> float:
        return subtotal


class PercentageDiscount:
    def __init__(self, percent: float) -> None:
        self._percent = percent

    def apply(self, subtotal: float) -> float:
        return subtotal * (1 - self._percent / 100)


# --- SRP: only orchestrates the use case; DIP: collaborators are injected ---
class OrderService:
    def __init__(self, discount: DiscountPolicy, repo: OrderRepository, notifier: Notifier) -> None:
        self._discount = discount
        self._repo = repo
        self._notifier = notifier

    def checkout(self, order: Order) -> Order:
        order.total = self._discount.apply(sum(order.items.values()))
        self._repo.save(order)
        self._notifier.send(order.customer_email, f"Order confirmed: ${order.total:.2f}")
        return order
