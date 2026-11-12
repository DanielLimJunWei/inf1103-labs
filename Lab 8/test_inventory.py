"""Lab 8 Section 9 checks (plus the Lab 7 ones). Run with: python -m unittest -v"""

import json
import os
import tempfile
import typing
import unittest

import main
from can_be_shipped import CanBeShipped
from digital_product import DigitalProduct
from inventory import Inventory
from order import Order
from order_line import OrderLine
from physical_product import PhysicalProduct
from product import Product
from supplier import Supplier


def make_supplier() -> Supplier:
    return Supplier("S001", "TechSource Pte Ltd", "sales@techsource.example")


class TestAssociation(unittest.TestCase):

    def test_product_stores_a_reference_to_its_supplier(self):
        supplier = make_supplier()
        laptop = PhysicalProduct("P001", "Laptop", 1200.0, 15, supplier, 2.5)
        self.assertIs(laptop.get_supplier(), supplier)

    def test_supplier_and_products_exist_independently(self):
        supplier = make_supplier()
        laptop = PhysicalProduct("P001", "Laptop", 1200.0, 15, supplier, 2.5)
        software = DigitalProduct("D001", "Windows 11 Pro", 199.0, 100, supplier, 5400.0)
        del supplier  # only the variable goes; the products still refer to the Supplier object
        self.assertEqual(laptop.get_supplier().get_name(), "TechSource Pte Ltd")
        self.assertIs(laptop.get_supplier(), software.get_supplier())
        del laptop    # deleting a product doesn't affect the supplier either
        self.assertEqual(software.get_supplier().get_supplier_id(), "S001")


class TestAggregation(unittest.TestCase):

    def setUp(self):
        self.mouse = PhysicalProduct("P002", "Mouse", 25.5, 45, make_supplier(), 0.1)

    def test_a_product_can_be_moved_between_inventories_without_being_destroyed(self):
        inventory_a, inventory_b = Inventory(), Inventory()
        inventory_a.add_product(self.mouse)
        removed = inventory_a.remove_product("P002")
        self.assertIs(removed, self.mouse)
        self.assertIsNone(inventory_a.find_product("P002"))
        self.mouse.update_stock(40)  # still usable on its own
        self.assertEqual(self.mouse.get_stock(), 40)
        inventory_b.add_product(self.mouse)
        self.assertIs(inventory_b.find_product("P002"), self.mouse)

    def test_removing_a_missing_product_returns_none(self):
        self.assertIsNone(Inventory().remove_product("Z999"))

    def test_duplicate_ids_are_rejected(self):
        inventory = Inventory()
        self.assertTrue(inventory.add_product(self.mouse))
        self.assertFalse(inventory.add_product(self.mouse))


class TestComposition(unittest.TestCase):

    def setUp(self):
        supplier = make_supplier()
        self.laptop = PhysicalProduct("P001", "Laptop", 1200.0, 15, supplier, 2.5)
        self.software = DigitalProduct("D001", "Windows 11 Pro", 199.0, 100, supplier, 5400.0)

    def test_order_creates_its_own_order_lines_and_totals_them(self):
        order = Order("ORD001")
        order.add_order_line(self.laptop, 2)
        order.add_order_line(self.software, 3)
        lines = order.get_order_lines()
        self.assertEqual(len(lines), 2)
        self.assertTrue(all(isinstance(line, OrderLine) for line in lines))
        self.assertAlmostEqual(lines[0].calculate_subtotal(), 2400.0)
        self.assertAlmostEqual(order.calculate_total(), 2400.0 + 597.0)

    def test_order_lines_refer_to_products_but_are_not_shared_between_orders(self):
        order1, order2 = Order("ORD001"), Order("ORD002")
        order1.add_order_line(self.laptop, 1)
        order2.add_order_line(self.laptop, 1)
        line1, line2 = order1.get_order_lines()[0], order2.get_order_lines()[0]
        self.assertIs(line1.get_product(), line2.get_product())  # one Product
        self.assertIsNot(line1, line2)                           # two separate OrderLines

    def test_order_lines_can_only_be_changed_through_the_order(self):
        order = Order("ORD001")
        order.add_order_line(self.laptop, 1)
        self.assertIsInstance(order.get_order_lines(), tuple)    # read-only view
        self.assertTrue(order.remove_order_line("P001"))
        self.assertEqual(order.get_order_lines(), ())
        self.assertFalse(order.remove_order_line("P001"))
        self.assertEqual(self.laptop.get_name(), "Laptop")      # the product itself is untouched


class TestTypeHints(unittest.TestCase):

    def test_relationships_are_typed_with_the_right_classes(self):
        self.assertIs(typing.get_type_hints(Product.__init__)["supplier"], Supplier)
        self.assertIs(typing.get_type_hints(OrderLine.__init__)["product"], Product)
        self.assertEqual(typing.get_type_hints(Inventory.find_product)["return"], Product | None)
        self.assertEqual(typing.get_type_hints(Order.add_order_line)["return"], type(None))
        self.assertIs(typing.get_type_hints(OrderLine.calculate_subtotal)["return"], float)


class TestLiskovAndPolymorphism(unittest.TestCase):

    def setUp(self):
        supplier = make_supplier()
        self.products: list[Product] = [PhysicalProduct("P001", "Laptop", 1200.0, 15, supplier, 2.5),
                                        DigitalProduct("D001", "Windows 11 Pro", 199.0, 100, supplier, 5400.0)]

    def test_both_subclasses_keep_the_meaning_of_update_stock(self):
        for product in self.products:
            product.update_stock(7)
            self.assertEqual(product.get_stock(), 7)
            product.update_stock(-1)  # rejected the same way by both
            self.assertEqual(product.get_stock(), 7)

    def test_each_product_gives_its_own_fulfilment_info_through_a_product_reference(self):
        inventory = Inventory()
        for product in self.products:
            inventory.add_product(product)
        messages = [product.get_fulfilment_info() for product in inventory.get_products()]
        self.assertIn("physical shipping", messages[0])
        self.assertIn("digitally", messages[1])

    def test_product_cannot_be_instantiated_and_only_physical_is_shippable(self):
        with self.assertRaises(TypeError):
            Product("X001", "Generic", 10.0, 1, make_supplier())
        self.assertIsInstance(self.products[0], CanBeShipped)
        self.assertNotIsInstance(self.products[1], CanBeShipped)


class TestPersistence(unittest.TestCase):

    def test_json_save_and_load_keeps_types_and_suppliers(self):
        supplier = make_supplier()
        inventory = Inventory()
        inventory.add_product(PhysicalProduct("P001", "Laptop", 1200.0, 15, supplier, 2.5))
        inventory.add_product(DigitalProduct("D001", "Windows 11 Pro", 199.0, 100, supplier, 5400.0))
        with tempfile.TemporaryDirectory() as folder:
            main.INVENTORY_FILE = os.path.join(folder, "inventory.json")
            main.save_inventory(inventory)
            with open(main.INVENTORY_FILE) as file:
                self.assertEqual(json.load(file)[0]["supplier"]["id"], "S001")
            loaded, suppliers = main.load_inventory()

        laptop, software = loaded.find_product("P001"), loaded.find_product("D001")
        self.assertIsInstance(laptop, PhysicalProduct)
        self.assertIsInstance(software, DigitalProduct)
        self.assertEqual(laptop.get_weight(), 2.5)
        # Products from the same supplier share one Supplier object again after loading
        self.assertIs(laptop.get_supplier(), software.get_supplier())
        self.assertEqual(list(suppliers), ["S001"])


if __name__ == "__main__":
    unittest.main()
