total_inventory = 0

while True:
    entry = input("Enter stock quantity (or 'quit' to finish): ").strip()

    if entry.lower() == "quit":
        break

    quantity = int(entry)
