import os

# Docker overrides this so the file lands in the mounted volume
# instead of inside the container, where it would be lost on exit.
INVENTORY_FILE = os.environ.get("INVENTORY_FILE", "inventory.txt")


def get_valid_input():
    entry = input("Enter stock quantity (or 'quit' to finish): ").strip()

    if entry.lower() == "quit":
        return "quit"

    # A leading "-" isn't a digit, so isdigit() alone can't tell a negative
    # number apart from plain garbage text -- check for it separately.
    is_negative_number = entry.startswith("-") and entry[1:].isdigit()

    if not entry.isdigit() and not is_negative_number:
        print(f"Error: '{entry}' is not a valid number. Please try again.")
        return None

    quantity = int(entry)

    if quantity < 0:
        print(f"Error: Negative values are not allowed ({quantity}).")
        return None

    return quantity


def process_delivery(current_total, new_value):
    return current_total + new_value


def calculate_tax(amount):
    return amount * 0.10


def generate_report(total_units, failed_attempts, deliveries_processed):
    print("\n--- Audit Report ---")
    print(f"Total Deliveries Processed: {deliveries_processed}")
    print(f"Total Units Processed: {total_units}")
    print(f"Number of Failed/Rejected Entries: {failed_attempts}")


# Read the previously saved inventory (line 1 is the running total).
total_inventory = 0
try:
    with open(INVENTORY_FILE, "r") as file:
        lines = file.read().splitlines()
    total_inventory = int(lines[0]) if lines else 0
    print(f"Loaded saved inventory: total {total_inventory}.")
except FileNotFoundError:
    print("No saved inventory found. Starting with an empty inventory.")
except ValueError:
    print(f"Warning: {INVENTORY_FILE} is corrupted. Starting with an empty inventory.")
    total_inventory = 0
failed_entries = 0
deliveries_processed = 0

while True:
    result = get_valid_input()

    if result == "quit":
        break

    if result is None:
        failed_entries += 1
        continue

    quantity = result
    tax = calculate_tax(quantity)
    total_inventory = process_delivery(total_inventory, quantity)
    deliveries_processed += 1

    if total_inventory > 500:
        print(f"ALERT: Overstock detected! Total inventory is {total_inventory}, which exceeds the 500 unit limit.")
        break
    else:
        print(f"Accepted {quantity} units (tax: {tax:.2f}). Current total: {total_inventory}")

generate_report(total_inventory, failed_entries, deliveries_processed)
