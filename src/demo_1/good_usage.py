"""Same SOLID classes from domain.py, but used with good patterns.

Run: uv run python -m demo_1.good_usage
"""
from dataclasses import dataclass
from enum import Enum

from demo_1.domain import DiscountPolicy, NoDiscount, Order, OrderService, PercentageDiscount
from demo_1.infra import ConsoleNotifier, InMemoryOrderRepository


# Improvement 1: strong types at the boundary (Enum instead of free-form strings).
class CustomerType(Enum):
    REGULAR = "regular"
    VIP = "vip"
    EMPLOYEE = "employee"


# Improvement 2: Registry/Factory. Adding a customer type = adding one line here, no if/elif.
DISCOUNTS: dict[CustomerType, DiscountPolicy] = {
    CustomerType.REGULAR: NoDiscount(),
    CustomerType.VIP: PercentageDiscount(20),
    CustomerType.EMPLOYEE: PercentageDiscount(30),
}


# Improvement 3: immutable DTO representing already-validated input.
@dataclass(frozen=True)
class CheckoutRequest:
    customer_type: CustomerType
    email: str
    items: tuple[tuple[str, float], ...]

    @classmethod
    def parse(cls, customer_type: str, email: str, items: list[tuple[str, float]]) -> "CheckoutRequest":
        """Validation at the boundary: a typo like 'vpi' fails loudly."""
        try:
            kind = CustomerType(customer_type)
        except ValueError:
            raise ValueError(f"Unknown customer type: {customer_type!r}") from None
        if "@" not in email:
            raise ValueError(f"Invalid email: {email!r}")
        if not items:
            raise ValueError("The order has no items")
        return cls(kind, email, tuple(items))


# Improvement 4: use case with injected dependencies, no globals or internal wiring.
class CheckoutUseCase:
    def __init__(self, discounts: dict[CustomerType, DiscountPolicy], repo, notifier) -> None:
        self._discounts = discounts
        self._repo = repo
        self._notifier = notifier

    def execute(self, request: CheckoutRequest) -> Order:
        service = OrderService(self._discounts[request.customer_type], self._repo, self._notifier)
        order = Order(request.email)
        for name, price in request.items:
            order.add_item(name, price)  # the entity protects its own invariants
        return service.checkout(order)


# Improvement 5: single composition root; the only place that knows the concrete classes.
def build_app() -> tuple[CheckoutUseCase, InMemoryOrderRepository]:
    repo = InMemoryOrderRepository()
    return CheckoutUseCase(DISCOUNTS, repo, ConsoleNotifier()), repo


def main() -> None:
    use_case, repo = build_app()
    requests = [
        ("vip", "ana@x.com", [("keyboard", 100.0), ("mouse", 50.0)]),
        ("employee", "luis@x.com", [("monitor", 300.0)]),
        ("vpi", "typo@x.com", [("cable", 10.0)]),  # now fails explicitly
        ("regular", "eva@x.com", [("cable", -5.0)]),  # invalid price: rejected by the entity
    ]
    for raw in requests:
        try:
            use_case.execute(CheckoutRequest.parse(*raw))
        except ValueError as e:
            print(f"[rejected] {e}")
    print(f"Saved orders: {len(repo.orders)}")


if __name__ == "__main__":
    main()
