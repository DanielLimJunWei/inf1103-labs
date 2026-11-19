import csv

from inventory import Inventory
from product_factory import ProductFactory
from supplier import Supplier


def load_products(path: str, inventory: Inventory, supplier: Supplier) -> None:
    """Section 5.2: read products from a CSV file into the inventory.

    A missing file is reported without crashing. A bad row is reported and skipped, and the rest still load.
    """
    try:
        file = open(path, newline="")
    except FileNotFoundError:
        # except: only runs if open() failed.
        print(f"Products file not found: {path}")
    else:
        # else: only runs if open() worked, so the file is safe to read here.
        loaded = 0
        with file:
            reader = csv.reader(file)
            next(reader, None)  # skip the header row
            for line_number, row in enumerate(reader, start=2):
                if not row:
                    continue  # ignore blank lines
                try:
                    product_type, product_id, name, price, stock_quantity = row
                    # float("abc") and an unknown type both raise ValueError, and so do the Product checks.
                    product = ProductFactory.create(product_type, product_id, name, float(price),
                                                    int(stock_quantity), supplier)
                except ValueError as error:
                    # One bad row is skipped; the loop carries on with the next one.
                    print(f"Skipping row {line_number} ({','.join(row)}): {error}")
                    continue
                if inventory.add_product(product):
                    loaded += 1
                else:
                    print(f"Skipping row {line_number}: product {product_id} is already in the inventory.")
        print(f"{loaded} products loaded.")
    finally:
        # finally: always runs, whether the file was found or not.
        print("Load attempt finished.")
