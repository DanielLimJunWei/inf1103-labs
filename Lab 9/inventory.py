from product import Product


class Inventory:
    """Manages a collection of Product objects (physical or digital).

    Aggregation: the Inventory holds references to Products that were created elsewhere. Removing a product, or
    emptying the inventory, doesn't destroy the product: it can be used on its own or added to another Inventory.
    """

    def __init__(self) -> None:
        # Typed with the base class, so any Product (and any future subclass) fits.
        self.__products: list[Product] = []

    def add_product(self, product: Product) -> bool:
        # Returns False instead of adding a second product with the same ID.
        if self.find_product(product.get_product_id()) is not None:
            return False
        self.__products.append(product)
        return True

    def remove_product(self, product_id: str) -> Product | None:
        # Only the reference is removed; the product is handed back so it can be reused.
        product = self.find_product(product_id)
        if product is not None:
            self.__products.remove(product)
        return product

    def find_product(self, product_id: str) -> Product | None:
        for product in self.__products:
            if product.get_product_id() == product_id:
                return product
        return None

    def display_all(self) -> None:
        print("\nCurrent Inventory")
        print("-" * 72)
        if not self.__products:
            print("No products in inventory.")
        for product in self.__products:
            # Each product knows how to display itself, whatever its type (polymorphism).
            product.display_information()
        print("-" * 72)

    def get_products(self) -> list[Product]:
        # Hand out a copy so callers can read the products but can't add or
        # remove items without going through add_product().
        return self.__products.copy()
