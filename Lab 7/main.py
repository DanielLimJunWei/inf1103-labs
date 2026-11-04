import json
import os

from can_be_shipped import CanBeShipped
from digital_product import DigitalProduct
from inventory import Inventory
from physical_product import PhysicalProduct

# Docker overrides this so the file lands in the mounted volume
# instead of inside the container, where it would be lost on exit.
INVENTORY_FILE = os.environ.get("INVENTORY_FILE", "inventory.json")


# ---------- File handling ----------

def create_product(record):
    # The saved "type" decides which subclass to rebuild.
    product_type = record.get("type")
    if product_type == "physical":
        return PhysicalProduct(record["id"], record["name"], record["price"],
                               record["stock"], record["weight"])
    if product_type == "digital":
        return DigitalProduct(record["id"], record["name"], record["price"],
                              record["stock"], record["download_size"])
    return None


def load_inventory():
    inventory = Inventory()

    if not os.path.exists(INVENTORY_FILE):
        print(f"{INVENTORY_FILE} not found. Starting with an empty inventory.")
        return inventory

    try:
        with open(INVENTORY_FILE, "r") as file:
            records = json.load(file)
    except json.JSONDecodeError:
        print(f"Warning: {INVENTORY_FILE} is corrupted. Starting with an empty inventory.")
        return inventory

    for record in records:
        try:
            product = create_product(record)
        except KeyError as missing:
            print(f"Warning: Skipping {record.get('id', '?')}, missing field {missing}.")
            continue
        if product is None:
            print(f"Warning: Skipping {record.get('id', '?')}, unknown product type.")
            continue
        inventory.add_product(product)

    print(f"{INVENTORY_FILE} found.")
    print("Inventory loaded successfully.")
    return inventory


def save_inventory(inventory):
    # Each product builds its own dictionary, including its type.
    records = [product.to_dict() for product in inventory.get_products()]

    # indent=4 keeps the file readable if it is opened by hand.
    with open(INVENTORY_FILE, "w") as file:
        json.dump(records, file, indent=4)
    print(f"Inventory saved successfully to {INVENTORY_FILE}.")


# ---------- User input ----------

def get_non_negative(prompt, convert):
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


def get_product_type():
    while True:
        print("Product Type:")
        print("1. Physical Product")
        print("2. Digital Product")
        choice = input("Enter product type: ").strip()
        if choice in ("1", "2"):
            return choice
        print(f"Error: '{choice}' is not a valid type. Please enter 1 or 2.")


# ---------- Menu actions ----------

def add_product(inventory):
    print("\nAdd New Product")
    product_type = get_product_type()

    # IDs are stored in uppercase so "p004" and "P004" count as the same product.
    product_id = input("Product ID: ").strip().upper()
    if not product_id:
        print("Error: Product ID cannot be empty.")
        return
    if inventory.search_product(product_id) is not None:
        print(f"Error: Product {product_id} already exists. Use Update Stock instead.")
        return

    name = input("Product Name: ").strip()
    if not name:
        print("Error: Product name cannot be empty.")
        return

    price = get_non_negative("Price: ", float)
    stock = get_non_negative("Stock Quantity: ", int)

    if product_type == "1":
        weight = get_non_negative("Weight (kg): ", float)
        product = PhysicalProduct(product_id, name, price, stock, weight)
    else:
        download_size = get_non_negative("Download Size (MB): ", float)
        product = DigitalProduct(product_id, name, price, stock, download_size)

    inventory.add_product(product)
    print("\nProduct added successfully!")


def update_stock(inventory):
    print("\nUpdate Stock")
    product_id = input("Enter Product ID: ").strip().upper()
    product = inventory.search_product(product_id)
    if product is None:
        print("\nProduct not found.")
        return

    print("\nProduct Found:")
    print(f"Name: {product.get_name()}")
    print(f"Current Stock: {product.get_stock()}")

    product.update_stock(get_non_negative("\nNew Stock Quantity: ", int))
    print("\nStock updated successfully!")


def search_product(inventory):
    print("\nSearch Product")
    product_id = input("Enter Product ID: ").strip().upper()
    product = inventory.search_product(product_id)
    if product is None:
        print("\nProduct not found.")
        return

    print("\nProduct Found")
    print("-" * 56)
    product.display_information()
    print(f"Fulfilment: {product.get_fulfilment_info()}")
    # Only products that signed the CanBeShipped contract have a shipping cost.
    if isinstance(product, CanBeShipped):
        print(f"Shipping Cost: ${product.calculate_shipping_cost():.2f}")
    print("-" * 56)


def show_menu():
    print("\n----------- MENU -----------")
    print("1. Display All Products")
    print("2. Add Product")
    print("3. Update Stock")
    print("4. Search Product")
    print("5. Save Inventory")
    print("6. Exit")
    print("----------------------------")


def main():
    print("=" * 40)
    print("INVENTORY MANAGEMENT SYSTEM")
    print("=" * 40)
    print()

    inventory = load_inventory()

    while True:
        show_menu()
        option = input("\nEnter option: ").strip()

        if option == "1":
            inventory.display_all()
        elif option == "2":
            add_product(inventory)
        elif option == "3":
            update_stock(inventory)
        elif option == "4":
            search_product(inventory)
        elif option == "5":
            print("\nSaving inventory...")
            save_inventory(inventory)
        elif option == "6":
            # Save on exit too, so changes aren't lost if option 5 was skipped.
            print("\nSaving inventory before exit...")
            save_inventory(inventory)
            print("\nThank you for using Inventory Management System.")
            print("Program terminated.")
            break
        else:
            print(f"Error: '{option}' is not a valid option. Please enter 1-6.")


if __name__ == "__main__":
    main()
