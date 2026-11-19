"""Walks through Sections 2-5 of Lab 9, one "Predict first" check at a time. Run with: python demo.py"""

import sys
import traceback
from unittest import mock

from discount_strategy import BulkDiscount, NoDiscount, PercentageDiscount, StudentDiscount
from inventory import Inventory
from main import get_positive_float
from order import Order
from product_factory import ProductFactory
from product_loader import load_products
from supplier import Supplier

supplier = Supplier("S001", "TechSource Pte Ltd", "sales@techsource.example")
keyboard = ProductFactory.create("physical", "P010", "Keyboard", 50.00, 30, supplier, weight=0.8)
antivirus = ProductFactory.create("digital", "D010", "Antivirus Suite", 49.90, 200, supplier, download_size=350.0)

print("=== 2.3 Strategy: an order whose lines add up to 250 ===")
order = Order("ORD001", BulkDiscount(200, 20))
order.add_order_line(keyboard, 5)            # 5 x 50.00 = 250.00
print("Lines add up to:", order.calculate_subtotal())
print("With BulkDiscount(200, 20):", order.calculate_total())
order.set_discount(PercentageDiscount(10))   # same order, new strategy
print("After set_discount(PercentageDiscount(10)):", order.calculate_total())

print("\n--- No strategy given: Order uses NoDiscount() ---")
plain = Order("ORD002")
plain.add_order_line(keyboard, 5)
print(type(plain.get_discount()).__name__, plain.calculate_total())

print("\n=== 2.4 A fourth strategy, Order unchanged ===")
order.set_discount(StudentDiscount())
print("With StudentDiscount():", order.calculate_total())
order.display_order()

print("\n--- Can two orders share one strategy object? ---")
ten_percent = PercentageDiscount(10)
order_a, order_b = Order("ORD003", ten_percent), Order("ORD004", ten_percent)
order_a.add_order_line(keyboard, 2)          # 100.00
order_b.add_order_line(antivirus, 1)         # 49.90
print("Same strategy object:", order_a.get_discount() is order_b.get_discount())
print("Totals:", order_a.calculate_total(), round(order_b.calculate_total(), 2))
del order_a
print("order_b still has its discount after order_a is deleted:", order_b.get_discount().describe())

print("\n=== 3.2 Factory: ProductFactory.create(\"service\", ...) ===")
try:
    ProductFactory.create("service", "S001", "Installation", 30.00, 5, supplier)
except ValueError:
    # Printing the traceback shows what Python would print if nothing caught the error:
    # the program would stop here, and nothing below this line would run.
    traceback.print_exc(file=sys.stdout)
print("Caught it, so the program carries on.")
print("Factory returns:", type(keyboard).__name__, "and", type(antivirus).__name__, "(both are a Product)")

print("\n=== 4. Validation: each class checks its own rule ===")
attempts = [
    ("price 0", lambda: ProductFactory.create("physical", "P020", "Pen", 0, 5, supplier)),
    ("stock -1", lambda: ProductFactory.create("digital", "D020", "Game", 9.99, -1, supplier)),
    ("order quantity 0", lambda: order.add_order_line(keyboard, 0)),
    ("update_stock(-5) on a DigitalProduct", lambda: antivirus.update_stock(-5)),
]
for label, attempt in attempts:
    try:
        attempt()
        print(f"{label}: accepted")
    except ValueError as error:
        print(f"{label}: ValueError: {error}")
print("Antivirus stock is still", antivirus.get_stock())

print("\n=== 5.1 get_positive_float: the user types abc, then -5, then 12.50 ===")
typed = iter(["abc", "-5", "12.50"])


def fake_input(prompt: str) -> str:
    # Shows the prompt and the "typed" value, as if a person had entered it.
    value = next(typed)
    print(prompt + value)
    return value


with mock.patch("builtins.input", fake_input):
    price = get_positive_float("Price: ")
print("Returned:", price)

print("\n=== 5.2 load_products(\"products.csv\") ===")
store = Inventory()
load_products("products.csv", store, supplier)
store.display_all()

print("\n--- The same call after renaming the file ---")
load_products("products_renamed.csv", Inventory(), supplier)
