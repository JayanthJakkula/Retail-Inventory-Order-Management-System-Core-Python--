from typing import Optional, Dict, List
from src.config import get_supabase


class CustomerDAO:
    def __init__(self):
        self.sb = get_supabase()

    def create_customer(self, name: str, email: str, phone: str, city: str) -> Optional[Dict]:
        payload = {"name": name, "email": email, "phone": phone, "city": city}
        self.sb.table("customers").insert(payload).execute()
        resp = self.sb.table("customers").select("*").eq("email", email).limit(1).execute()
        return resp.data[0] if resp.data else None

    def get_customer_by_id(self, cust_id: int) -> Optional[Dict]:
        resp = self.sb.table("customers").select("*").eq("cust_id", cust_id).limit(1).execute()
        return resp.data[0] if resp.data else None

    def get_customer_by_email(self, email: str) -> Optional[Dict]:
        resp = self.sb.table("customers").select("*").eq("email", email).limit(1).execute()
        return resp.data[0] if resp.data else None

    def update_customer(self, cust_id: int, fields: Dict) -> Optional[Dict]:
        self.sb.table("customers").update(fields).eq("cust_id", cust_id).execute()
        resp = self.sb.table("customers").select("*").eq("cust_id", cust_id).limit(1).execute()
        return resp.data[0] if resp.data else None

    def delete_customer(self, cust_id: int) -> Optional[Dict]:
        resp_before = self.sb.table("customers").select("*").eq("cust_id", cust_id).limit(1).execute()
        row = resp_before.data[0] if resp_before.data else None
        self.sb.table("customers").delete().eq("cust_id", cust_id).execute()
        return row

    def list_customers(self, limit: int = 100) -> List[Dict]:
        resp = self.sb.table("customers").select("*").order("cust_id").limit(limit).execute()
        return resp.data or []

    def search_by_city(self, city: str) -> List[Dict]:
        resp = self.sb.table("customers").select("*").eq("city", city).execute()
        return resp.data or []

    def has_orders(self, cust_id: int) -> bool:
        resp = self.sb.table("orders").select("order_id").eq("cust_id", cust_id).limit(1).execute()
        return len(resp.data) > 0

