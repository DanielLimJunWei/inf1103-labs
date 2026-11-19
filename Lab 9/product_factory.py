from digital_product import DigitalProduct
from physical_product import PhysicalProduct
from product import Product
from supplier import Supplier


class ProductFactory:
    """Factory pattern: the one place that decides which Product subclass to create.

    The rest of the program asks the factory for a Product and never names PhysicalProduct or DigitalProduct.
    A new product type means one new branch here (the factory still breaks OCP), but nothing else changes.
    """

    @staticmethod
    def create(product_type: str, product_id: str, name: str, price: float, stock_quantity: int,
               supplier: Supplier, weight: float = 0.0, download_size: float = 0.0) -> Product:
        # weight is only used for physical products and download_size only for digital ones.
        # Both default to 0.0 because the products.csv file has neither column.
        kind = product_type.strip().lower()
        if kind == "physical":
            return PhysicalProduct(product_id, name, price, stock_quantity, supplier, weight)
        elif kind == "digital":
            return DigitalProduct(product_id, name, price, stock_quantity, supplier, download_size)
        else:
            raise ValueError(f"Unknown product type: {product_type}")
