# demo-1: SOLID classes, good vs. bad usage

A small Python demo showing that **well-designed classes are not enough**.
The classes in `domain.py` follow SOLID, but the code that *uses* them can still
be fragile if it ignores good design patterns and data-flow practices.

## Project structure

```
src/demo_1/
├── domain.py       # SOLID classes: Order, OrderService, discount policies, Protocols
├── infra.py        # Concrete implementations: in-memory repository, console notifier
├── bad_usage.py    # Same classes, used with anti-patterns
└── good_usage.py   # Same classes, used with good patterns
```

## SOLID in `domain.py`

- **SRP:** `OrderService` only orchestrates checkout; storage and notification live elsewhere.
- **OCP:** add a new discount by writing a new `DiscountPolicy`; `OrderService` stays untouched.
- **LSP:** `NoDiscount` and `PercentageDiscount` are fully interchangeable.
- **ISP:** `DiscountPolicy`, `OrderRepository` and `Notifier` are tiny Protocols.
- **DIP:** `OrderService` depends on those Protocols, injected via its constructor.

## Bad vs. good usage

| `bad_usage.py` | `good_usage.py` |
|---|---|
| Global mutable `repo` | Dependencies injected, no globals |
| `if/elif` on strings to pick a policy | `Enum` + registry (`DISCOUNTS`) |
| Wiring rebuilt inside business logic | Single composition root (`build_app()`) |
| Client mutates `order.items` directly | `Order.add_item()` protects invariants |
| Raw strings/dicts as input | Frozen `CheckoutRequest` DTO validated at the boundary |
| `isinstance` on concrete types | Client never inspects concrete types |
| Typo `"vpi"` silently charges full price | Typo `"vpi"` is rejected with a clear error |

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)

## Run

From the project root:

```bash
# Good usage
uv run python -m demo_1.good_usage

# Bad usage
uv run python -m demo_1.bad_usage

# Compare side by side
uv run python -m demo_1.bad_usage && echo "-----" && uv run python -m demo_1.good_usage
```
