from typing import Optional, Dict, List
from src.dao.customer_dao import CustomerDAO


class CustomerError(Exception):
    pass


class CustomerService:
    def __init__(self, dao: CustomerDAO):
        self.dao = dao

    def add_customer(self, name: str, email: str, phone: str, city: str) -> Dict:
        if not email or not email.strip():
            raise CustomerError("Email is required")
        if self.dao.get_customer_by_email(email):
            raise CustomerError(f"Customer with email '{email}' already exists")
        return self.dao.create_customer(name, email, phone, city)

    def update_customer(self, cust_id: int, phone: Optional[str] = None, city: Optional[str] = None) -> Dict:
        fields = {}
        if phone:
            fields["phone"] = phone
        if city:
            fields["city"] = city
        if not fields:
            raise CustomerError("Nothing to update")
        return self.dao.update_customer(cust_id, fields)

    def delete_customer(self, cust_id: int) -> Dict:
        if self.dao.has_orders(cust_id):
            raise CustomerError("Cannot delete customer with existing orders")
        return self.dao.delete_customer(cust_id)

    def list_customers(self, limit: int = 100) -> List[Dict]:
        return self.dao.list_customers(limit)

    def search_by_email(self, email: str) -> Optional[Dict]:
        return self.dao.get_customer_by_email(email)

    def search_by_city(self, city: str) -> List[Dict]:
        return self.dao.search_by_city(city)