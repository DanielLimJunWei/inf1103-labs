"""Lab 9 Section 7: validation and exception handling checks. Run from the Lab 9 folder with: python -m unittest -v"""

import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest import mock

from inventory import Inventory
from main import get_positive_float
from order import Order
from product_factory import ProductFactory
from product_loader import load_products
from supplier import Supplier

CSV_TEXT = """product_type,product_id,name,price,stock_quantity
physical,P001,Desk Lamp,25.00,10
digital,D001,Photo Editor,49.90,100
service,S001,Installation,30.00,5
physical,P002,Office Chair,abc,3
physical,P003,Monitor Stand,39.50,7
"""


def make_supplier() -> Supplier:
    return Supplier("S001", "TechSource Pte Ltd", "sales@techsource.example")


class TestValidation(unittest.TestCase):

    def test_price_must_be_greater_than_zero(self):
        for price in (0, -5):
            with self.assertRaises(ValueError):
                ProductFactory.create("physical", "P001", "Desk Lamp", price, 10, make_supplier())

    def test_stock_cannot_be_negative(self):
        with self.assertRaises(ValueError):
            ProductFactory.create("digital", "D001", "Photo Editor", 49.9, -1, make_supplier())
        product = ProductFactory.create("digital", "D001", "Photo Editor", 49.9, 0, make_supplier())
        self.assertEqual(product.get_stock(), 0)   # 0 is allowed: sold out, not broken

    def test_update_stock_rejects_negative_and_keeps_the_old_value(self):
        product = ProductFactory.create("physical", "P001", "Desk Lamp", 25.0, 10, make_supplier())
        with self.assertRaises(ValueError):
            product.update_stock(-3)
        self.assertEqual(product.get_stock(), 10)

    def test_order_line_quantity_must_be_greater_than_zero(self):
        lamp = ProductFactory.create("physical", "P001", "Desk Lamp", 25.0, 10, make_supplier())
        new_order = Order("ORD001")
        for quantity in (0, -2):
            with self.assertRaises(ValueError):
                new_order.add_order_line(lamp, quantity)
        self.assertEqual(new_order.get_order_lines(), ())   # no bad line was added


class TestUserInput(unittest.TestCase):

    def test_get_positive_float_keeps_asking_until_the_value_is_valid(self):
        output = io.StringIO()
        with mock.patch("builtins.input", side_effect=["abc", "-5", "12.50"]) as fake_input, \
                redirect_stdout(output):
            value = get_positive_float("Price: ")
        self.assertEqual(value, 12.5)
        self.assertEqual(fake_input.call_count, 3)
        self.assertEqual(output.getvalue().splitlines(),
                         ["Please enter a valid number, e.g. 12.50",
                          "Please enter a number greater than zero."])


class TestLoadProducts(unittest.TestCase):

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.folder.name, "products.csv")
        with open(self.path, "w", newline="") as file:
            file.write(CSV_TEXT)

    def tearDown(self):
        self.folder.cleanup()

    def load(self, path: str) -> tuple[Inventory, list[str]]:
        inventory, output = Inventory(), io.StringIO()
        with redirect_stdout(output):
            load_products(path, inventory, make_supplier())
        return inventory, output.getvalue().splitlines()

    def test_valid_rows_load_and_bad_rows_are_reported_and_skipped(self):
        inventory, lines = self.load(self.path)
        self.assertEqual([p.get_product_id() for p in inventory.get_products()], ["P001", "D001", "P003"])
        self.assertIn("Unknown product type: service", lines[0])
        self.assertIn("could not convert string to float: 'abc'", lines[1])
        self.assertEqual(lines[2:], ["3 products loaded.", "Load attempt finished."])

    def test_missing_file_is_handled_without_crashing(self):
        missing = os.path.join(self.folder.name, "renamed.csv")
        inventory, lines = self.load(missing)
        self.assertEqual(inventory.get_products(), [])
        self.assertEqual(lines, [f"Products file not found: {missing}", "Load attempt finished."])

    def test_loading_twice_skips_products_already_in_the_inventory(self):
        inventory, output = Inventory(), io.StringIO()
        with redirect_stdout(output):
            load_products(self.path, inventory, make_supplier())
            load_products(self.path, inventory, make_supplier())
        self.assertEqual(len(inventory.get_products()), 3)
        self.assertIn("0 products loaded.", output.getvalue())


if __name__ == "__main__":
    unittest.main()
