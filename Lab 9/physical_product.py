from can_be_shipped import CanBeShipped
from product import Product
from supplier import Supplier

# Shipping rule: a flat handling fee plus a charge for every kilogram.
BASE_SHIPPING_FEE = 5.00
COST_PER_KG = 2.00


# A PhysicalProduct is-a Product (inheritance) and mustbeableto be shipped
# (it implements the CanBeShipped interface).
class PhysicalProduct(Product, CanBeShipped):
    """A product that is stored in a warehouse and shipped to the customer."""

    def __init__(self, product_id: str, name: str, price: float, stock: int, supplier: Supplier,
                 weight: float) -> None:
        # Reuse Product's constructor for the shared attributes, including the supplier.
        super().__init__(product_id, name, price, stock, supplier)
        if weight < 0:
            raise ValueError("Weight cannot be negative.")
        self.__weight: float = weight

    def get_weight(self) -> float:
        return self.__weight

    def display_information(self) -> None:
        # The parent prints the common details; this class only adds its own.
        super().display_information()
        print(f"    Type: Physical | Weight: {self.__weight:.2f} kg | Supplier: {self.get_supplier().get_name()}")

    def to_dict(self) -> dict:
        record = super().to_dict()
        record["type"] = "physical"
        record["weight"] = self.__weight
        return record

    def get_fulfilment_info(self) -> str:
        return f"{self.get_name()} requires physical shipping to the customer."

    def calculate_shipping_cost(self) -> float:
        return BASE_SHIPPING_FEE + COST_PER_KG * self.__weight
