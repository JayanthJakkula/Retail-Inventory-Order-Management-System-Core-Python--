from typing import List, Dict
from datetime import datetime, timedelta
from src.config import get_supabase

class ReportingService:

    def __init__(self):
        self._sb = get_supabase()

    def top_selling_products(self, top_n: int = 5) -> List[Dict]:
        # Sum up quantities in order_items, join products to get name
        # group by product, order by total quantity desc, limit top_n
        # Supabase might allow `.rpc()` or you could write raw SQL view
        resp = (
            self._sb.table("order_items")
            .select("prod_id, quantity, products(name)")
            .execute()
        )
        items = resp.data or []
        # aggregate in Python
        agg = {}
        for itm in items:
            pid = itm["prod_id"]
            qty = itm["quantity"]
            prodname = itm.get("products", {}).get("name", "")
            if pid in agg:
                agg[pid]["quantity"] += qty
            else:
                agg[pid] = {"prod_id": pid, "quantity": qty, "name": prodname}

        sorted_list = sorted(agg.values(), key=lambda x: x["quantity"], reverse=True)
        return sorted_list[:top_n]

    def total_revenue_last_month(self) -> float:
        now = datetime.utcnow()
        one_month_ago = now - timedelta(days=30)
        resp = (
            self._sb.table("payments")
            .select("amount, status, payments!inner(order_id:orders(status,created_at))")
            .gte("created_at", one_month_ago.isoformat())
            .eq("status", "PAID")
            .execute()
        )
        payments = resp.data or []
        # Sum the amounts
        total = sum(p["amount"] for p in payments)
        return total

    def orders_per_customer(self) -> List[Dict]:
        resp = (
            self._sb.table("orders")
            .select("customer_id, created_at")
            .execute()
        )
        orders = resp.data or []
        agg = {}
        for o in orders:
            cid = o["customer_id"]
            agg[cid] = agg.get(cid, 0) + 1

        result = [{"customer_id": cid, "orders_count": cnt} for cid, cnt in agg.items()]
        return result

    def customers_more_than_n_orders(self, n: int = 2) -> List[Dict]:
        all_customers = self.orders_per_customer()
        filtered = [c for c in all_customers if c["orders_count"] > n]
        return filtered
