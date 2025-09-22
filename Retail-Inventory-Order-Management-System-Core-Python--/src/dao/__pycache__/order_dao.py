from typing import Dict, List, Optional
from src.config import get_supabase


class OrderDAO:
    def __init__(self):
        self.sb = get_supabase()

    def create_order(self, cust_id: int, total_amount: float, status: str = "PLACED") -> Dict:
        payload = {"cust_id": cust_id, "total_amount": total_amount, "status": status}
        resp = self.sb.table("orders").insert(payload).execute()
        order_id = resp.data[0]["order_id"]
        return self.get_order_by_id(order_id)

    def insert_order_item(self, order_id: int, prod_id: int, qty: int, price: float):
        payload = {"order_id": order_id, "prod_id": prod_id, "quantity": qty, "price": price}
        self.sb.table("order_items").insert(payload).execute()

    def get_order_by_id(self, order_id: int) -> Optional[Dict]:
        resp = self.sb.table("orders").select("*").eq("order_id", order_id).limit(1).execute()
        return resp.data[0] if resp.data else None

    def get_order_items(self, order_id: int) -> List[Dict]:
        resp = self.sb.table("order_items").select("*").eq("order_id", order_id).execute()
        return resp.data or []

    def list_orders_by_customer(self, cust_id: int) -> List[Dict]:
        resp = self.sb.table("orders").select("*").eq("cust_id", cust_id).order("order_id").execute()
        return resp.data or []

    def update_order_status(self, order_id: int, status: str) -> Optional[Dict]:
        self.sb.table("orders").update({"status": status}).eq("order_id", order_id).execute()
        return self.get_order_by_id(order_id)

    def delete_order_items(self, order_id: int):
        self.sb.table("order_items").delete().eq("order_id", order_id).execute()

