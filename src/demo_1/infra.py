"""Concrete implementations (interchangeable thanks to LSP)."""
from demo_1.domain import Order


class InMemoryOrderRepository:
    def __init__(self) -> None:
        self.orders: list[Order] = []

    def save(self, order: Order) -> None:
        self.orders.append(order)


class ConsoleNotifier:
    def send(self, to: str, message: str) -> None:
        print(f"[email -> {to}] {message}")
