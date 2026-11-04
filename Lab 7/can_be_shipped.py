from abc import ABC, abstractmethod


class CanBeShipped(ABC):
    """Interface-style ABC: a contract for anything that can be shipped.

    It holds no attributes or shipping rules, so any class (not only
    products) can sign it by implementing calculate_shipping_cost().
    """

    @abstractmethod
    def calculate_shipping_cost(self):
        """Return the cost of shipping this item, in dollars."""
