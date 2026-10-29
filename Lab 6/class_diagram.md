# Lab 6 UML Class Diagram

`-` = private (by convention, `__name` in Python) · `+` = public

```
+--------------------------------------------+
|                  Product                   |
+--------------------------------------------+
| - __product_id : String                    |
| - __name       : String                    |
| - __price      : float                     |
| - __stock      : int                       |
+--------------------------------------------+
| + __init__(product_id, name, price, stock) |
| + get_product_id() : String                |
| + get_name()       : String                |
| + get_price()      : float                 |
| + get_stock()      : int                   |
| + update_stock(quantity : int) : void      |
| + display_information() : void             |
+--------------------------------------------+
                      ^
                      | 0..*  (Inventory holds many Products)
                      |
+--------------------------------------------+
|                 Inventory                  |
+--------------------------------------------+
| - __products : list[Product]               |
+--------------------------------------------+
| + __init__()                               |
| + add_product(product : Product) : bool    |
| + search_product(product_id : String)      |
|                     : Product or None      |
| + display_all() : void                     |
| + get_products() : list[Product]           |
+--------------------------------------------+
```

## Responsibilities (Single Responsibility Principle)

| Part | Responsibility |
|---|---|
| **Product** | Stores one product's information and manages its own stock |
| **Inventory** | Stores, adds, searches and displays a collection of Products |
| **main.py** | Shows the menu, gets user input, calls Inventory methods, and loads/saves `inventory.json` |
