from product import Product


# A DigitalProduct is-a Product, but it is not shipped, so it does not
# implement CanBeShipped.
class DigitalProduct(Product):
    """A product that is delivered to the customer as a download."""

    def __init__(self, product_id, name, price, stock, download_size):
        # Reuse Product's constructor for the shared attributes.
        super().__init__(product_id, name, price, stock)
        self.__download_size = download_size

    def get_download_size(self):
        return self.__download_size

    def display_information(self):
        # The parent prints the common details; this class only adds its own.
        super().display_information()
        print(f"    Type: Digital | Download Size: {self.__download_size:.1f} MB")

    def to_dict(self):
        record = super().to_dict()
        record["type"] = "digital"
        record["download_size"] = self.__download_size
        return record

    def get_fulfilment_info(self):
        return f"{self.get_name()} is delivered digitally through a download link."
