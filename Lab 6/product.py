class Product:
    """Represents and manages a single product in the inventory."""

    def __init__(self, product_id, name, price, stock):
        # Double underscores mark these as private: outside code should go
        # through the methods below instead of changing them directly.
        self.__product_id = product_id
        self.__name = name
        self.__price = price
        self.__stock = stock

    def get_product_id(self):
        return self.__product_id

    def get_name(self):
        return self.__name

    def get_price(self):
        return self.__price

    def get_stock(self):
        return self.__stock

    def update_stock(self, quantity):
        # The Product decides what counts as a valid stock level, so a bad
        # value from anywhere in the program can't put it into a broken state.
        if quantity < 0:
            print(f"Error: Stock cannot be negative ({quantity}).")
            return
        self.__stock = quantity

    def display_information(self):
        print(f"ID: {self.__product_id} | Name: {self.__name} | "
              f"Price: ${self.__price:.2f} | Stock: {self.__stock}")
