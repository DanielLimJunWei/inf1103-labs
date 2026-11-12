from order_line import OrderLine
from product import Product


class Order:
    """A customer order, made up of OrderLine objects.

    Composition: the Order creates its own OrderLines and is the only thing that manages them. They are never
    passed in, handed to another Order or kept after a line is removed.
    """

    def __init__(self, order_id: str) -> None:
        self.__order_id: str = order_id
        self.__order_lines: list[OrderLine] = []

    def get_order_id(self) -> str:
        return self.__order_id

    def add_order_line(self, product: Product, quantity: int) -> None:
        # The OrderLine is created here, inside the Order, never outside it.
        self.__order_lines.append(OrderLine(product, quantity))

    def remove_order_line(self, product_id: str) -> bool:
        for line in self.__order_lines:
            if line.get_product().get_product_id() == product_id:
                # Nothing else refers to the line, so it is gone with it.
                self.__order_lines.remove(line)
                return True
        return False

    def get_order_lines(self) -> tuple[OrderLine, ...]:
        # A tuple can be read but not added to, so lines can only be added through add_order_line().
        return tuple(self.__order_lines)

    def calculate_total(self) -> float:
        # Each line works out its own subtotal; the order only adds them up.
        return sum(line.calculate_subtotal() for line in self.__order_lines)

    def display_order(self) -> None:
        print(f"\nOrder {self.__order_id}")
        print("-" * 46)
        if not self.__order_lines:
            print("No items in this order.")
        for line in self.__order_lines:
            line.display_information()
        print("-" * 46)
        print(f"{'Total':<33}${self.calculate_total():>10,.2f}")
