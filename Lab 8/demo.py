"""Walks through Sections 2-4, 6 and 7 of Lab 8 from external code, including each "Predict first" check."""

from digital_product import DigitalProduct
from inventory import Inventory
from order import Order
from physical_product import PhysicalProduct
from product import Product
from supplier import Supplier


def show_product_details(product: Product) -> None:
    # Works for any Product: it only uses what every Product promises (LSP).
    product.display_information()
    print(product.get_fulfilment_info())


print("=== 2. Association: Supplier and Product ===")
supplier = Supplier("S001", "TechSource Pte Ltd", "sales@techsource.example")
laptop = PhysicalProduct("P001", "Laptop", 1200.0, 15, supplier, 2.5)
antivirus = DigitalProduct("D002", "Antivirus Suite", 49.9, 200, supplier, 350.0)
laptop.get_supplier().display_information()
antivirus.get_supplier().display_information()
print("Supplier and products are separate objects:", laptop.get_supplier() is not laptop)
print("Both products point to the same Supplier object:", laptop.get_supplier() is antivirus.get_supplier())

print("\n--- Predict first: del supplier ---")
del supplier
laptop.get_supplier().display_information()  # still works: the product keeps its own reference
antivirus.get_supplier().display_information()

print("\n=== 3. Aggregation: Inventory and Product ===")
mouse = PhysicalProduct("P002", "Mouse", 25.5, 45, laptop.get_supplier(), 0.1)  # exists before any inventory
inventory_a = Inventory()
inventory_b = Inventory()
inventory_a.add_product(mouse)
print("In A:", inventory_a.find_product("P002") is mouse)

print("\n--- Predict first: does the Product still work after it is removed from A? ---")
removed = inventory_a.remove_product("P002")
print("Still in A:", inventory_a.find_product("P002") is not None)
print("Removed object is the same Mouse:", removed is mouse)
mouse.update_stock(40)
mouse.display_information()
inventory_b.add_product(mouse)
print("Same Mouse now in B:", inventory_b.find_product("P002") is mouse)

print("\n=== 4. Composition: Order and OrderLine ===")
order1 = Order("ORD001")
order1.add_order_line(laptop, 2)
order1.add_order_line(antivirus, 3)
order1.add_order_line(mouse, 1)
order1.display_order()

print("\n--- Predict first: the same Product in two Orders ---")
order2 = Order("ORD002")
order2.add_order_line(laptop, 1)
line_1 = order1.get_order_lines()[0]
line_2 = order2.get_order_lines()[0]
print("Same Product object in both lines:", line_1.get_product() is line_2.get_product())
print("Same OrderLine object:", line_1 is line_2)
print(f"id(product) {id(line_1.get_product()) == id(line_2.get_product())}, "
      f"id(line) {id(line_1) == id(line_2)}")

order1.remove_order_line("D002")
print("\nAfter removing D002 from ORD001:")
order1.display_order()

print("\n=== 6. Liskov Substitution: show_product_details(product: Product) ===")
for product in (laptop, antivirus):
    show_product_details(product)
    product.update_stock(product.get_stock() - 1)  # both keep Product's meaning of update_stock
    print("Stock after selling one:", product.get_stock())
    product.update_stock(-5)                       # both reject a negative stock the same way

print("\n=== 7. Polymorphism: one loop over Product references ===")
store = Inventory()
for product in (laptop, antivirus, mouse):
    store.add_product(product)
for product in store.get_products():
    product.display_information()
    print(product.get_fulfilment_info())
