from discount_strategy import DiscountStrategy, NoDiscount
from order_line import OrderLine
from product import Product


class Order:
    """A customer order, made up of OrderLine objects.

    Composition: the Order creates its own OrderLines and is the only thing that manages them. They are never
    passed in, handed to another Order or kept after a line is removed.

    Association: the Order uses a DiscountStrategy that was created outside it. The strategy isn't part of the
    order, and two orders can share the same strategy object.
    """

    def __init__(self, order_id: str, discount: DiscountStrategy | None = None) -> None:
        self.__order_id: str = order_id
        self.__order_lines: list[OrderLine] = []
        # A new NoDiscount() for each order. A default of discount=NoDiscount() in the brackets would be created
        # once and shared by every order (the mutable default trap).
        self.__discount: DiscountStrategy = discount if discount is not None else NoDiscount()

    def get_order_id(self) -> str:
        return self.__order_id

    def get_discount(self) -> DiscountStrategy:
        return self.__discount

    def set_discount(self, discount: DiscountStrategy) -> None:
        # Swap the strategy on an existing order; the lines stay the same.
        self.__discount = discount

    def add_order_line(self, product: Product, quantity: int) -> None:
        # The OrderLine is created here, inside the Order, never outside it.
        # OrderLine checks its own quantity and raises ValueError, so a bad line is never added.
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

    def calculate_subtotal(self) -> float:
        # Each line works out its own subtotal; the order only adds them up.
        return sum(line.calculate_subtotal() for line in self.__order_lines)

    def calculate_total(self) -> float:
        # No if/elif about discount types: the strategy decides.
        total = sum(line.calculate_subtotal() for line in self.__order_lines)
        return self.__discount.apply(total)

    def display_order(self) -> None:
        print(f"\nOrder {self.__order_id}")
        print("-" * 46)
        if not self.__order_lines:
            print("No items in this order.")
        for line in self.__order_lines:
            line.display_information()
        print("-" * 46)
        print(f"{'Subtotal':<33}${self.calculate_subtotal():>10,.2f}")
        print(f"Discount: {self.__discount.describe()}")
        print(f"{'Total':<33}${self.calculate_total():>10,.2f}")
