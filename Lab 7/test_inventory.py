"""Part 7 checks. Run with: python -m unittest -v"""

import os
import tempfile
import unittest

import main
from can_be_shipped import CanBeShipped
from digital_product import DigitalProduct
from inventory import Inventory
from physical_product import PhysicalProduct
from product import Product


class TestProducts(unittest.TestCase):

    def setUp(self):
        self.laptop = PhysicalProduct("P001", "Laptop", 1200.0, 15, 2.5)
        self.software = DigitalProduct("D001", "Windows 11 Pro", 199.0, 100, 5400.0)

    def test_physical_stores_weight(self):
        self.assertEqual(self.laptop.get_weight(), 2.5)
        self.assertEqual(self.laptop.get_name(), "Laptop")  # inherited getter

    def test_digital_stores_download_size(self):
        self.assertEqual(self.software.get_download_size(), 5400.0)

    def test_both_implement_fulfilment_info(self):
        self.assertIn("shipping", self.laptop.get_fulfilment_info())
        self.assertIn("digitally", self.software.get_fulfilment_info())

    def test_product_cannot_be_instantiated(self):
        with self.assertRaises(TypeError):
            Product("X001", "Generic", 10.0, 1)

    def test_physical_shipping_cost_depends_on_weight(self):
        light = PhysicalProduct("P002", "Mouse", 25.5, 45, 0.1)
        self.assertAlmostEqual(light.calculate_shipping_cost(), 5.20)
        self.assertAlmostEqual(self.laptop.calculate_shipping_cost(), 10.00)

    def test_digital_is_not_shippable(self):
        self.assertIsInstance(self.laptop, CanBeShipped)
        self.assertNotIsInstance(self.software, CanBeShipped)


class TestInventory(unittest.TestCase):

    def setUp(self):
        self.inventory = Inventory()
        self.inventory.add_product(PhysicalProduct("P001", "Laptop", 1200.0, 15, 2.5))
        self.inventory.add_product(DigitalProduct("D001", "Windows 11 Pro", 199.0, 100, 5400.0))

    def test_rejects_duplicate_id(self):
        duplicate = DigitalProduct("P001", "Other", 1.0, 1, 1.0)
        self.assertFalse(self.inventory.add_product(duplicate))

    def test_search_and_update_stock(self):
        product = self.inventory.search_product("D001")
        product.update_stock(80)
        self.assertEqual(self.inventory.search_product("D001").get_stock(), 80)
        self.assertIsNone(self.inventory.search_product("Z999"))

    def test_json_save_and_load_keeps_types(self):
        with tempfile.TemporaryDirectory() as folder:
            main.INVENTORY_FILE = os.path.join(folder, "inventory.json")
            main.save_inventory(self.inventory)
            loaded = main.load_inventory()

        laptop = loaded.search_product("P001")
        software = loaded.search_product("D001")
        self.assertIsInstance(laptop, PhysicalProduct)
        self.assertEqual(laptop.get_weight(), 2.5)
        self.assertIsInstance(software, DigitalProduct)
        self.assertEqual(software.get_download_size(), 5400.0)


if __name__ == "__main__":
    unittest.main()
