import json
import os
from typing import Callable

from can_be_shipped import CanBeShipped
from discount_strategy import BulkDiscount, DiscountStrategy, NoDiscount, PercentageDiscount, StudentDiscount
from inventory import Inventory
from order import Order
from product import Product
from product_factory import ProductFactory
from product_loader import load_products
from supplier import Supplier

# Docker overrides this so the file lands in the mounted volume
# instead of inside the container, where it would be lost on exit.
INVENTORY_FILE = os.environ.get("INVENTORY_FILE", "inventory.json")
PRODUCTS_CSV = os.environ.get("PRODUCTS_CSV", "products.csv")

# The menu's discount choices. Choosing one only looks it up here, so adding a discount
# means a new class and a new row, with no change to Order and no if/elif chain.
DISCOUNT_OPTIONS: dict[str, tuple[str, Callable[[], DiscountStrategy]]] = {
    "1": ("No discount", NoDiscount),
    "2": ("10% off", lambda: PercentageDiscount(10)),
    "3": ("$20 off orders of $200 or more", lambda: BulkDiscount(200, 20)),
    "4": ("Student discount (5% off)", StudentDiscount),
}


# ---------- File handling ----------

def get_supplier(record: dict, suppliers: dict[str, Supplier]) -> Supplier:
    # Products with the same supplier ID share one Supplier object, as they would in real life.
    supplier_id = record["id"]
    if supplier_id not in suppliers:
        suppliers[supplier_id] = Supplier(supplier_id, record["name"], record["contact_email"])
    return suppliers[supplier_id]


def create_product(record: dict, supplier: Supplier) -> Product:
    # The factory decides which subclass to rebuild from the saved "type".
    # It raises ValueError for an unknown type or an invalid price or stock.
    return ProductFactory.create(record.get("type", ""), record["id"], record["name"], record["price"],
                                 record["stock"], supplier, weight=record.get("weight", 0.0),
                                 download_size=record.get("download_size", 0.0))


def load_inventory() -> tuple[Inventory, dict[str, Supplier]]:
    inventory = Inventory()
    suppliers: dict[str, Supplier] = {}

    if not os.path.exists(INVENTORY_FILE):
        print(f"{INVENTORY_FILE} not found. Starting with an empty inventory.")
        return inventory, suppliers

    try:
        with open(INVENTORY_FILE, "r") as file:
            records = json.load(file)
    except json.JSONDecodeError:
        print(f"Warning: {INVENTORY_FILE} is corrupted. Starting with an empty inventory.")
        return inventory, suppliers

    for record in records:
        try:
            product = create_product(record, get_supplier(record["supplier"], suppliers))
        except KeyError as missing:
            print(f"Warning: Skipping {record.get('id', '?')}, missing field {missing}.")
            continue
        except ValueError as error:
            print(f"Warning: Skipping {record.get('id', '?')}, {error}")
            continue
        inventory.add_product(product)

    print(f"{INVENTORY_FILE} found.")
    print("Inventory loaded successfully.")
    return inventory, suppliers


def save_inventory(inventory: Inventory) -> None:
    # Each product builds its own dictionary, including its type and supplier.
    records = [product.to_dict() for product in inventory.get_products()]

    # indent=4 keeps the file readable if it is opened by hand.
    with open(INVENTORY_FILE, "w") as file:
        json.dump(records, file, indent=4)
    print(f"Inventory saved successfully to {INVENTORY_FILE}.")


# ---------- User input ----------

def get_positive_float(prompt: str) -> float:
    # Section 5.1: keep asking until the user types a number greater than zero.
    while True:
        try:
            value = float(input(prompt))   # "abc" raises ValueError here
            if value <= 0:
                print("Please enter a number greater than zero.")
                continue
            return value
        except ValueError:
            print("Please enter a valid number, e.g. 12.50")


def get_non_negative(prompt: str, convert: type) -> int | float:
    # Keep asking so one typo doesn't throw away the rest of the entry.
    while True:
        entry = input(prompt).strip()
        try:
            value = convert(entry)
        except ValueError:
            print(f"Error: '{entry}' is not a valid number. Please try again.")
            continue

        if value < 0:
            print(f"Error: Negative values are not allowed ({entry}).")
            continue

        return value


def get_product_type() -> str:
    while True:
        print("Product Type:")
        print("1. Physical Product")
        print("2. Digital Product")
        choice = input("Enter product type: ").strip()
        if choice in ("1", "2"):
            return choice
        print(f"Error: '{choice}' is not a valid type. Please enter 1 or 2.")


def choose_supplier(suppliers: dict[str, Supplier]) -> Supplier:
    # An existing supplier is reused; a new ID creates a new Supplier object.
    if suppliers:
        print("Existing suppliers: " + ", ".join(f"{s.get_supplier_id()} ({s.get_name()})"
                                                for s in suppliers.values()))
    while True:
        supplier_id = input("Supplier ID: ").strip().upper()
        if supplier_id:
            break
        print("Error: Supplier ID cannot be empty.")
    if supplier_id in suppliers:
        return suppliers[supplier_id]

    print("New supplier.")
    name = input("Supplier Name: ").strip() or supplier_id
    email = input("Supplier Email: ").strip()
    suppliers[supplier_id] = Supplier(supplier_id, name, email)
    return suppliers[supplier_id]


# ---------- Menu actions ----------

def add_product(inventory: Inventory, suppliers: dict[str, Supplier]) -> None:
    print("\nAdd New Product")
    product_type = get_product_type()

    # IDs are stored in uppercase so "p004" and "P004" count as the same product.
    product_id = input("Product ID: ").strip().upper()
    if not product_id:
        print("Error: Product ID cannot be empty.")
        return
    if inventory.find_product(product_id) is not None:
        print(f"Error: Product {product_id} already exists. Use Update Stock instead.")
        return

    name = input("Product Name: ").strip()
    if not name:
        print("Error: Product name cannot be empty.")
        return

    price = get_positive_float("Price: ")
    stock = get_non_negative("Stock Quantity: ", int)
    supplier = choose_supplier(suppliers)

    # The factory creates the product; main.py no longer names PhysicalProduct or DigitalProduct.
    if product_type == "1":
        product = ProductFactory.create("physical", product_id, name, price, stock, supplier,
                                        weight=get_non_negative("Weight (kg): ", float))
    else:
        product = ProductFactory.create("digital", product_id, name, price, stock, supplier,
                                        download_size=get_non_negative("Download Size (MB): ", float))

    inventory.add_product(product)
    print("\nProduct added successfully!")


def update_stock(inventory: Inventory) -> None:
    print("\nUpdate Stock")
    product_id = input("Enter Product ID: ").strip().upper()
    product = inventory.find_product(product_id)
    if product is None:
        print("\nProduct not found.")
        return

    print("\nProduct Found:")
    print(f"Name: {product.get_name()}")
    print(f"Current Stock: {product.get_stock()}")

    try:
        product.update_stock(get_non_negative("\nNew Stock Quantity: ", int))
    except ValueError as error:
        print(f"Error: {error}")
        return
    print("\nStock updated successfully!")


def search_product(inventory: Inventory) -> None:
    print("\nSearch Product")
    product_id = input("Enter Product ID: ").strip().upper()
    product = inventory.find_product(product_id)
    if product is None:
        print("\nProduct not found.")
        return

    print("\nProduct Found")
    print("-" * 72)
    product.display_information()
    product.get_supplier().display_information()
    print(f"Fulfilment: {product.get_fulfilment_info()}")
    # Only products that signed the CanBeShipped contract have a shipping cost.
    if isinstance(product, CanBeShipped):
        print(f"Shipping Cost: ${product.calculate_shipping_cost():.2f}")
    print("-" * 72)


def create_order(inventory: Inventory, order_number: int) -> None:
    order = Order(f"ORD{order_number:03d}")
    print(f"\nCreate Order {order.get_order_id()} (press Enter on Product ID to finish)")
    while True:
        product_id = input("Product ID: ").strip().upper()
        if not product_id:
            break
        product = inventory.find_product(product_id)
        if product is None:
            print("Product not found.")
            continue
        quantity = get_non_negative("Quantity: ", int)
        try:
            # OrderLine rejects a quantity of 0 itself; main.py only reports it and asks again.
            order.add_order_line(product, quantity)
        except ValueError as error:
            print(f"Error: {error}")

    order.set_discount(choose_discount())
    order.display_order()


def choose_discount() -> DiscountStrategy:
    print("\nDiscount:")
    for key, (label, _) in DISCOUNT_OPTIONS.items():
        print(f"{key}. {label}")
    while True:
        choice = input("Choose a discount: ").strip()
        if choice in DISCOUNT_OPTIONS:
            _, make_strategy = DISCOUNT_OPTIONS[choice]
            return make_strategy()
        print(f"Error: '{choice}' is not a valid option. Please enter 1-{len(DISCOUNT_OPTIONS)}.")


def import_products(inventory: Inventory, suppliers: dict[str, Supplier]) -> None:
    print("\nImport Products from CSV")
    path = input(f"CSV file (press Enter for {PRODUCTS_CSV}): ").strip() or PRODUCTS_CSV
    print("Which supplier supplies these products?")
    load_products(path, inventory, choose_supplier(suppliers))


def show_menu() -> None:
    print("\n----------- MENU -----------")
    print("1. Display All Products")
    print("2. Add Product")
    print("3. Update Stock")
    print("4. Search Product")
    print("5. Create Order")
    print("6. Import Products from CSV")
    print("7. Save Inventory")
    print("8. Exit")
    print("----------------------------")


def main() -> None:
    print("=" * 40)
    print("INVENTORY MANAGEMENT SYSTEM")
    print("=" * 40)
    print()

    inventory, suppliers = load_inventory()
    orders_created = 0

    while True:
        show_menu()
        option = input("\nEnter option: ").strip()

        if option == "1":
            inventory.display_all()
        elif option == "2":
            add_product(inventory, suppliers)
        elif option == "3":
            update_stock(inventory)
        elif option == "4":
            search_product(inventory)
        elif option == "5":
            orders_created += 1
            create_order(inventory, orders_created)
        elif option == "6":
            import_products(inventory, suppliers)
        elif option == "7":
            print("\nSaving inventory...")
            save_inventory(inventory)
        elif option == "8":
            # Save on exit too, so changes aren't lost if option 7 was skipped.
            print("\nSaving inventory before exit...")
            save_inventory(inventory)
            print("\nThank you for using Inventory Management System.")
            print("Program terminated.")
            break
        else:
            print(f"Error: '{option}' is not a valid option. Please enter 1-8.")


if __name__ == "__main__":
    main()
