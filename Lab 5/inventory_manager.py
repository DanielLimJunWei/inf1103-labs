# Each product is a dictionary, and the inventory is a list of them.
inventory = [
    {"id": "P001", "name": "Laptop", "price": 1200.00, "stock": 15},
    {"id": "P002", "name": "Mouse", "price": 25.50, "stock": 40},
    {"id": "P003", "name": "Keyboard", "price": 45.00, "stock": 25},
]

for product in inventory:
    print(f"ID: {product['id']} | Name: {product['name']} | "
          f"Price: ${product['price']:.2f} | Stock: {product['stock']}")
