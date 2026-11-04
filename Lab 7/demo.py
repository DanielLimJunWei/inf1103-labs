"""Walks through Parts 1-4 of the lab from external code."""

from digital_product import DigitalProduct
from physical_product import PhysicalProduct
from product import Product

print("=== 1 & 2. Inheritance and overriding ===")
guitar = PhysicalProduct("P100", "Guitar", 350.0, 5, 3.2)
windows = DigitalProduct("D100", "Windows 11 Pro", 199.0, 100, 5400.0)
guitar.display_information()
windows.display_information()

print("\n=== 3.2 get_fulfilment_info() ===")
print(guitar.get_fulfilment_info())
print(windows.get_fulfilment_info())

print("\n=== 3.3 Creating a Product directly ===")
try:
    Product("X001", "Generic", 10.0, 1)
except TypeError as error:
    print(f"TypeError: {error}")

print("\n=== 4.2 Shipping costs for different weights ===")
for weight in (0.5, 3.2, 10.0):
    item = PhysicalProduct("P200", "Box", 20.0, 1, weight)
    print(f"{weight:>5} kg -> ${item.calculate_shipping_cost():.2f}")

print("\nDigitalProduct has calculate_shipping_cost():",
      hasattr(windows, "calculate_shipping_cost"))
