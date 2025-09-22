from typing import Optional, Dict
from src.config import get_supabase

def _sb():
    return get_supabase()

class PaymentDAO:

    def create_payment(self, order_id: int, amount: float) -> Optional[Dict]:
        payload = {
            "order_id": order_id,
            "amount": amount,
            "status": "PENDING",
            "method": None
        }
        # Insert and then fetch
        _sb().table("payments").insert(payload).execute()
        resp = _sb().table("payments").select("*").eq("order_id", order_id).order("id", desc=True).limit(1).execute()
        return resp.data[0] if resp.data else None

    def get_payment_by_order(self, order_id: int) -> Optional[Dict]:
        resp = _sb().table("payments").select("*").eq("order_id", order_id).limit(1).execute()
        return resp.data[0] if resp.data else None

    def update_payment(self, payment_id: int, fields: Dict) -> Optional[Dict]:
        _sb().table("payments").update(fields).eq("id", payment_id).execute()
        resp = _sb().table("payments").select("*").eq("id", payment_id).limit(1).execute()
        return resp.data[0] if resp.data else None
