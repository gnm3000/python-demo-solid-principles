"""The classes in domain.py are SOLID, but THIS code that uses them is a design mess.

Run: uv run python -m solid_demo.bad_usage
"""
from solid_demo.domain import NoDiscount, Order, OrderService, PercentageDiscount
from solid_demo.infra import ConsoleNotifier, InMemoryOrderRepository

# Anti-pattern 1: shared global mutable state.
repo = InMemoryOrderRepository()


def process(customer_type, email, items):
    # Anti-pattern 2: if/elif on strings to pick a strategy (instead of Factory/Registry/Strategy map).
    #   Every new policy forces an edit to this function: OCP is violated "from the outside".
    if customer_type == "vip":
        discount = PercentageDiscount(20)
    elif customer_type == "employee":
        discount = PercentageDiscount(30)
    elif customer_type == "regular":
        discount = NoDiscount()
    else:
        discount = NoDiscount()

    # Anti-pattern 3: the wiring (composition root) lives inside the business function and is
    #   rebuilt on every call; there is no central container or factory.
    service = OrderService(discount, repo, ConsoleNotifier())

    order = Order(email)
    # Anti-pattern 4: the client fills the object's internals by hand (no Builder / add_item method).
    for name, price in items:
        order.items[name] = price

    result = service.checkout(order)

    # Anti-pattern 5: breaks encapsulation and duplicates service logic by reaching into the
    #   concrete repo via a global and doing isinstance on the concrete type.
    if isinstance(discount, PercentageDiscount):
        print("   (discount applied, saved:", len(repo.orders), ")")
    return result


def main() -> None:
    process("vip", "ana@x.com", [("keyboard", 100.0), ("mouse", 50.0)])
    process("employee", "luis@x.com", [("monitor", 300.0)])
    process("regular", "eva@x.com", [("cable", 10.0)])
    process("vpi", "typo@x.com", [("cable", 10.0)])  # typo in string: silently falls back to NoDiscount


if __name__ == "__main__":
    main()
