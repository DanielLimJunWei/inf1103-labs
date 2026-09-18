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


total_inventory = 0
failed_entries = 0

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

    if total_inventory > 500:
        print(f"ALERT: Overstock detected! Total inventory is {total_inventory}, which exceeds the 500 unit limit.")
        break
    else:
        print(f"Accepted {quantity} units (tax: {tax:.2f}). Current total: {total_inventory}")

print("\n--- Audit Report ---")
print(f"Total Units Processed: {total_inventory}")
print(f"Number of Failed/Rejected Entries: {failed_entries}")
