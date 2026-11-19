class Supplier:
    """A company that supplies products.

    A Supplier is associated with the Products it supplies: neither one is part of the other, and each can exist
    without the other.
    """

    def __init__(self, supplier_id: str, name: str, contact_email: str) -> None:
        self.__supplier_id: str = supplier_id
        self.__name: str = name
        self.__contact_email: str = contact_email

    def get_supplier_id(self) -> str:
        return self.__supplier_id

    def get_name(self) -> str:
        return self.__name

    def get_contact_email(self) -> str:
        return self.__contact_email

    def display_information(self) -> None:
        print(f"Supplier: {self.__supplier_id} | {self.__name} | {self.__contact_email}")

    def to_dict(self) -> dict:
        return {"id": self.__supplier_id, "name": self.__name, "contact_email": self.__contact_email}
