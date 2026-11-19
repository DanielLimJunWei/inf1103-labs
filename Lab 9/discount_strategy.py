from abc import ABC, abstractmethod


class DiscountStrategy(ABC):
    """Strategy pattern: one way of discounting an order total.

    Every strategy provides the same apply() method, so Order can use any of them without knowing which one it has.
    A new kind of discount is a new subclass here; Order never changes.
    """

    @abstractmethod
    def apply(self, total: float) -> float:
        pass

    @abstractmethod
    def describe(self) -> str:
        """A short label for the receipt, e.g. "10% off"."""


class NoDiscount(DiscountStrategy):
    """The default: the total stays the same."""

    def apply(self, total: float) -> float:
        return total

    def describe(self) -> str:
        return "No discount"


class PercentageDiscount(DiscountStrategy):
    """Takes a percentage off, e.g. PercentageDiscount(10) takes 10% off."""

    def __init__(self, percentage: float) -> None:
        # Validation: the strategy protects its own rule, so it can never make a total negative.
        if not 0 < percentage <= 100:
            raise ValueError("Percentage must be more than 0 and at most 100.")
        self.__percentage: float = percentage

    def get_percentage(self) -> float:
        return self.__percentage

    def apply(self, total: float) -> float:
        return total * (1 - self.__percentage / 100)

    def describe(self) -> str:
        return f"{self.__percentage:g}% off"


class BulkDiscount(DiscountStrategy):
    """Takes a fixed amount off any total of at least the threshold, e.g. BulkDiscount(200, 20)."""

    def __init__(self, threshold: float, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Discount amount must be greater than zero.")
        if threshold < amount:
            # Otherwise a total between the two would go below zero.
            raise ValueError("Threshold must be at least the discount amount.")
        self.__threshold: float = threshold
        self.__amount: float = amount

    def apply(self, total: float) -> float:
        if total >= self.__threshold:
            return total - self.__amount
        return total

    def describe(self) -> str:
        return f"${self.__amount:g} off orders of ${self.__threshold:g} or more"


class StudentDiscount(PercentageDiscount):
    """Section 2.4: a fourth strategy added without changing Order. A student discount is a 5% percentage discount."""

    def __init__(self) -> None:
        super().__init__(5)

    def describe(self) -> str:
        return "Student discount (5% off)"
