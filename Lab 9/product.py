from abc import ABC, abstractmethod

from supplier import Supplier


class Product(ABC):
    """Abstract base class for every product in the inventory.

    Inheriting from ABC and having an @abstractmethod means Product itself
    can't be created: every product must be a PhysicalProduct or DigitalProduct.
    """

    def __init__(self, product_id: str, name: str, price: float, stock: int, supplier: Supplier) -> None:
        # Validation: Product owns the price and stock rules, so every subclass gets them
        # and no product can be created in a broken state.
        if price <= 0:
            raise ValueError("Price must be greater than zero.")
        if stock < 0:
            raise ValueError("Stock quantity cannot be negative.")
        # Double underscores mark these as private: outside code should go
        # through the methods below instead of changing them directly.
        self.__product_id: str = product_id
        self.__name: str = name
        self.__price: float = price
        self.__stock: int = stock
        # Association: the Supplier is created elsewhere and only referred to here.
        # Deleting the product doesn't delete the supplier, and the other way round.
        self.__supplier: Supplier = supplier

    def get_product_id(self) -> str:
        return self.__product_id

    def get_name(self) -> str:
        return self.__name

    def get_price(self) -> float:
        return self.__price

    def get_stock(self) -> int:
        return self.__stock

    def get_supplier(self) -> Supplier:
        return self.__supplier

    def update_stock(self, quantity: int) -> None:
        # The Product decides what counts as a valid stock level, so a bad
        # value from anywhere in the program can't put it into a broken state.
        # Every subclass keeps this meaning (Liskov Substitution).
        # Lab 9: it now raises ValueError instead of printing, so the caller decides what to tell the user.
        if quantity < 0:
            raise ValueError(f"Stock quantity cannot be negative ({quantity}).")
        self.__stock = quantity

    def display_information(self) -> None:
        print(f"ID: {self.__product_id} | Name: {self.__name} | "
              f"Price: ${self.__price:.2f} | Stock: {self.__stock}")

    def to_dict(self) -> dict:
        # Subclasses extend this with their own type and extra attributes.
        return {"id": self.__product_id,
                "name": self.__name,
                "price": self.__price,
                "stock": self.__stock,
                "supplier": self.__supplier.to_dict()}

    @abstractmethod
    def get_fulfilment_info(self) -> str:
        """Return how this kind of product reaches the customer."""
