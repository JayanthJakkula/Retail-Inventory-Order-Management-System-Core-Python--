from typing import Dict, List
from src.dao.order_dao import OrderDAO
from src.dao.customer_dao import CustomerDAO
from src.dao.product_dao import ProductDAO


class OrderError(Exception):
    pass


class OrderService:
    def __init__(self, order_dao: OrderDAO, customer_dao: CustomerDAO, product_dao: ProductDAO):
        self.order_dao = order_dao
        self.customer_dao = customer_dao
        self.product_dao = product_dao

    def create_order(self, cust_id: int, items: List[Dict]) -> Dict:
        # Validate customer
        cust = self.customer_dao.get_customer_by_id(cust_id)
        if not cust:
            raise OrderError(f"Customer {cust_id} not found")

        # Check products and stock
        total_amount = 0.0
        product_updates = []
        for item in items:
            prod = self.product_dao.get_product_by_id(item["prod_id"])
            if not prod:
                raise OrderError(f"Product {item['prod_id']} not found")
            if prod["stock"] < item["quantity"]:
                raise OrderError(f"Not enough stock for {prod['name']} (Available: {prod['stock']})")
            total_amount += prod["price"] * item["quantity"]
            product_updates.append((prod["prod_id"], prod["stock"] - item["quantity"], prod["price"], item["quantity"]))

        # Create order
        order = self.order_dao.create_order(cust_id, total_amount, status="PLACED")

        # Insert items + deduct stock
        for prod_id, new_stock, price, qty in product_updates:
            self.order_dao.insert_order_item(order["order_id"], prod_id, qty, price)
            self.product_dao.update_product(prod_id, {"stock": new_stock})

        return self.get_order_details(order["order_id"])

    def get_order_details(self, order_id: int) -> Dict:
        order = self.order_dao.get_order_by_id(order_id)
        if not order:
            raise OrderError(f"Order {order_id} not found")
        cust = self.customer_dao.get_customer_by_id(order["cust_id"])
        items = self.order_dao.get_order_items(order_id)
        order["customer"] = cust
        order["items"] = items
        return order

    def list_orders_by_customer(self, cust_id: int) -> List[Dict]:
        return self.order_dao.list_orders_by_customer(cust_id)

    def cancel_order(self, order_id: int) -> Dict:
        order = self.order_dao.get_order_by_id(order_id)
        if not order:
            raise OrderError("Order not found")
        if order["status"] != "PLACED":
            raise OrderError("Only PLACED orders can be cancelled")

        # Restore stock
        items = self.order_dao.get_order_items(order_id)
        for item in items:
            prod = self.product_dao.get_product_by_id(item["prod_id"])
            self.product_dao.update_product(prod["prod_id"], {"stock": prod["stock"] + item["quantity"]})

        return self.order_dao.update_order_status(order_id, "CANCELLED")

    def complete_order(self, order_id: int) -> Dict:
        order = self.order_dao.get_order_by_id(order_id)
        if not order:
            raise OrderError("Order not found")
        if order["status"] != "PLACED":
            raise OrderError("Only PLACED orders can be marked as completed")
        return self.order_dao.update_order_status(order_id, "COMPLETED")