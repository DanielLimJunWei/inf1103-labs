total_inventory = 0
failed_entries = 0

while True:
    entry = input("Enter stock quantity (or 'quit' to finish): ").strip()

    if entry.lower() == "quit":
        break

    if not entry.isdigit():
        print(f"Error: '{entry}' is not a valid number. Please try again.")
        failed_entries += 1
        continue

    quantity = int(entry)
