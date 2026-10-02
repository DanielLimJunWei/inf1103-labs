import json
import os

# Docker overrides this so the file lands in the mounted volume
# instead of inside the container, where it would be lost on exit.
INVENTORY_FILE = os.environ.get("INVENTORY_FILE", "inventory.json")


def load_inventory():
    if not os.path.exists(INVENTORY_FILE):
        print(f"{INVENTORY_FILE} not found. Starting with an empty inventory.")
        return []

    try:
        with open(INVENTORY_FILE, "r") as file:
            inventory = json.load(file)
    except json.JSONDecodeError:
        print(f"Warning: {INVENTORY_FILE} is corrupted. Starting with an empty inventory.")
        return []

    print(f"{INVENTORY_FILE} found.")
    print("Inventory loaded successfully.")
    return inventory


def save_inventory(inventory):
    # indent=4 keeps the file readable if it is opened by hand.
    with open(INVENTORY_FILE, "w") as file:
        json.dump(inventory, file, indent=4)
    print(f"Inventory saved successfully to {INVENTORY_FILE}.")


def format_product(product):
    return (f"ID: {product['id']} | Name: {product['name']} | "
            f"Price: ${product['price']:.2f} | Stock: {product['stock']}")


def find_product(inventory, product_id):
    for product in inventory:
        if product["id"] == product_id:
            return product
    return None


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


def display_all(inventory):
    print("\nCurrent Inventory")
    print("-" * 48)
    if not inventory:
        print("No products in inventory.")
    for product in inventory:
        print(format_product(product))
    print("-" * 48)


def add_product(inventory):
    print("\nAdd New Product")
    # IDs are stored in uppercase so "p004" and "P004" count as the same product.
    product_id = input("Product ID: ").strip().upper()
    if not product_id:
        print("Error: Product ID cannot be empty.")
        return
    if find_product(inventory, product_id) is not None:
        print(f"Error: Product {product_id} already exists. Use Update Stock instead.")
        return

    name = input("Product Name: ").strip()
    if not name:
        print("Error: Product name cannot be empty.")
        return

    price = get_non_negative("Price: ", float)
    stock = get_non_negative("Stock Quantity: ", int)

    inventory.append({"id": product_id, "name": name, "price": price, "stock": stock})
    print("\nProduct added successfully!")


def update_stock(inventory):
    print("\nUpdate Stock")
    product_id = input("Enter Product ID: ").strip().upper()
    product = find_product(inventory, product_id)
    if product is None:
        print("\nProduct not found.")
        return

    print("\nProduct Found:")
    print(f"Name: {product['name']}")
    print(f"Current Stock: {product['stock']}")

    product["stock"] = get_non_negative("\nNew Stock Quantity: ", int)
    print("\nStock updated successfully!")


def search_product(inventory):
    print("\nSearch Product")
    product_id = input("Enter Product ID: ").strip().upper()
    product = find_product(inventory, product_id)
    if product is None:
        print("\nProduct not found.")
        return

    print("\nProduct Found")
    print("-" * 48)
    print(f"ID: {product['id']}")
    print(f"Name: {product['name']}")
    print(f"Price: ${product['price']:.2f}")
    print(f"Stock: {product['stock']}")
    print("-" * 48)


# Each product is a dictionary, and the inventory is a list of them.
# The products now come from inventory.json instead of being hard-coded.
inventory = load_inventory()
display_all(inventory)
save_inventory(inventory)
