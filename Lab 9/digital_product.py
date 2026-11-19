from product import Product
from supplier import Supplier


# A DigitalProduct is-a Product, but it is not shipped, so it does not
# implement CanBeShipped.
class DigitalProduct(Product):
    """A product that is delivered to the customer as a download.

    Its stock is the number of licences left to sell, so update_stock() keeps exactly the meaning Product gives it.
    """

    def __init__(self, product_id: str, name: str, price: float, stock: int, supplier: Supplier,
                 download_size: float) -> None:
        # Reuse Product's constructor for the shared attributes, including the supplier.
        super().__init__(product_id, name, price, stock, supplier)
        if download_size < 0:
            raise ValueError("Download size cannot be negative.")
        self.__download_size: float = download_size

    def get_download_size(self) -> float:
        return self.__download_size

    def display_information(self) -> None:
        # The parent prints the common details; this class only adds its own.
        super().display_information()
        print(f"    Type: Digital | Download Size: {self.__download_size:.1f} MB | "
              f"Supplier: {self.get_supplier().get_name()}")

    def to_dict(self) -> dict:
        record = super().to_dict()
        record["type"] = "digital"
        record["download_size"] = self.__download_size
        return record

    def get_fulfilment_info(self) -> str:
        return f"{self.get_name()} is delivered digitally through a download link."
