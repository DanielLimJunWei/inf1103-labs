"""Lab 9 Section 7: Strategy and Factory checks. Run from the Lab 9 folder with: python -m unittest -v"""

import inspect
import unittest

import main
import order
from digital_product import DigitalProduct
from discount_strategy import (BulkDiscount, DiscountStrategy, NoDiscount, PercentageDiscount,
                               StudentDiscount)
from order import Order
from physical_product import PhysicalProduct
from product import Product
from product_factory import ProductFactory
from supplier import Supplier


def make_supplier() -> Supplier:
    return Supplier("S001", "TechSource Pte Ltd", "sales@techsource.example")


def order_of_250(discount: DiscountStrategy | None = None) -> Order:
    keyboard = ProductFactory.create("physical", "P010", "Keyboard", 50.0, 30, make_supplier())
    new_order = Order("ORD001", discount)
    new_order.add_order_line(keyboard, 5)
    return new_order


class FlatTenOff(DiscountStrategy):
    """A strategy that only exists in this test file, to prove Order needs no change for a new one."""

    def apply(self, total: float) -> float:
        return total - 10

    def describe(self) -> str:
        return "$10 off"


class TestStrategy(unittest.TestCase):

    def test_each_strategy_works_on_its_own(self):
        self.assertEqual(NoDiscount().apply(250), 250)
        self.assertAlmostEqual(PercentageDiscount(10).apply(250), 225)
        self.assertEqual(BulkDiscount(200, 20).apply(250), 230)
        self.assertEqual(BulkDiscount(200, 20).apply(199.99), 199.99)   # under the threshold
        self.assertEqual(BulkDiscount(200, 20).apply(200), 180)         # "200 or more" includes 200
        self.assertAlmostEqual(StudentDiscount().apply(250), 237.5)

    def test_order_uses_no_discount_when_none_is_given(self):
        new_order = order_of_250()
        self.assertIsInstance(new_order.get_discount(), NoDiscount)
        self.assertEqual(new_order.calculate_total(), 250)

    def test_each_order_gets_its_own_default_no_discount(self):
        self.assertIsNot(Order("A").get_discount(), Order("B").get_discount())

    def test_order_totals_through_its_strategy(self):
        self.assertEqual(order_of_250(BulkDiscount(200, 20)).calculate_total(), 230)

    def test_set_discount_changes_the_strategy_on_an_existing_order(self):
        new_order = order_of_250(BulkDiscount(200, 20))
        new_order.set_discount(PercentageDiscount(10))
        self.assertAlmostEqual(new_order.calculate_total(), 225)
        self.assertEqual(len(new_order.get_order_lines()), 1)   # the lines are untouched

    def test_a_new_strategy_works_without_changing_order(self):
        self.assertEqual(order_of_250(FlatTenOff()).calculate_total(), 240)

    def test_order_has_no_discount_if_elif_logic(self):
        # calculate_total() has no if/elif at all, and Order never names a concrete discount except the default.
        lines = [line.strip() for line in inspect.getsource(Order.calculate_total).splitlines()]
        self.assertFalse([line for line in lines if line.startswith(("if ", "elif ", "else"))])
        source = inspect.getsource(order)
        for name in ("PercentageDiscount", "BulkDiscount", "StudentDiscount"):
            self.assertNotIn(name, source)

    def test_two_orders_can_share_one_strategy(self):
        shared = PercentageDiscount(10)
        first, second = order_of_250(shared), order_of_250(shared)
        self.assertIs(first.get_discount(), second.get_discount())
        self.assertAlmostEqual(first.calculate_total(), second.calculate_total())

    def test_discount_strategy_cannot_be_created(self):
        with self.assertRaises(TypeError):
            DiscountStrategy()

    def test_invalid_discount_settings_are_rejected(self):
        for bad in (lambda: PercentageDiscount(0), lambda: PercentageDiscount(150),
                    lambda: BulkDiscount(200, 0), lambda: BulkDiscount(10, 20)):
            with self.assertRaises(ValueError):
                bad()


class TestFactory(unittest.TestCase):

    def test_factory_creates_the_right_subclass_as_a_product(self):
        supplier = make_supplier()
        lamp = ProductFactory.create("physical", "P001", "Desk Lamp", 25.0, 10, supplier, weight=1.2)
        editor = ProductFactory.create("digital", "D001", "Photo Editor", 49.9, 100, supplier,
                                       download_size=800.0)
        self.assertIsInstance(lamp, PhysicalProduct)
        self.assertIsInstance(editor, DigitalProduct)
        self.assertIsInstance(lamp, Product)
        self.assertEqual(lamp.get_weight(), 1.2)
        self.assertEqual(editor.get_download_size(), 800.0)

    def test_type_text_is_not_case_sensitive(self):
        product = ProductFactory.create(" Physical ", "P001", "Desk Lamp", 25.0, 10, make_supplier())
        self.assertIsInstance(product, PhysicalProduct)

    def test_unknown_type_raises_a_clear_value_error(self):
        with self.assertRaises(ValueError) as caught:
            ProductFactory.create("service", "S001", "Installation", 30.0, 5, make_supplier())
        self.assertEqual(str(caught.exception), "Unknown product type: service")

    def test_main_creates_products_only_through_the_factory(self):
        source = inspect.getsource(main)
        self.assertNotIn("PhysicalProduct(", source)
        self.assertNotIn("DigitalProduct(", source)
        self.assertIn("ProductFactory.create(", source)


if __name__ == "__main__":
    unittest.main()
