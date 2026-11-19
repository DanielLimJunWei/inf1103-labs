from product import Product


class OrderLine:
    """One product and the quantity of it in an Order.

    An OrderLine only exists inside the Order that created it (composition). It refers to a Product but doesn't
    own it (association): the same Product can be in an Inventory and in other orders.
    """

    def __init__(self, product: Product, quantity: int) -> None:
        # Validation: the OrderLine owns the quantity rule, so no caller can create a line of 0 or -3.
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")
        self.__product: Product = product
        self.__quantity: int = quantity

    def get_product(self) -> Product:
        return self.__product

    def get_quantity(self) -> int:
        return self.__quantity

    def calculate_subtotal(self) -> float:
        return self.__product.get_price() * self.__quantity

    def display_information(self) -> None:
        print(f"{self.__product.get_product_id():<6} {self.__product.get_name():<20} "
              f"x{self.__quantity:<4} ${self.calculate_subtotal():>10,.2f}")
