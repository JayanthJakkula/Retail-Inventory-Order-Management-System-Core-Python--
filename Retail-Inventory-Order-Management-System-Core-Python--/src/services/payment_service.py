from typing import Dict
from src.dao.payment_dao import PaymentDAO
from src.dao.order_dao import OrderDAO
from src.services.order_service import OrderService

class PaymentError(Exception):
    pass

class PaymentService:
    def __init__(self, payment_dao: PaymentDAO, order_dao: OrderDAO, order_service: OrderService):
        self.payment_dao = payment_dao
        self.order_dao = order_dao
        self.order_service = order_service

    def create_payment_for_order(self, order_id: int) -> Dict:
        order = self.order_dao.get_order_by_id(order_id)
        if not order:
            raise PaymentError("Order not found")

        # If payment exists attempt? Or always create new? Up to business logic.
        existing = self.payment_dao.get_payment_by_order(order_id)
        if existing and existing["status"] != "REFUNDED":
            raise PaymentError("Payment already exists for this order")

        payment = self.payment_dao.create_payment(order_id, order["total_amount"])
        return payment

    def process_payment(self, order_id: int, method: str) -> Dict:
        # Mark payment as PAID and set method, change order status to COMPLETED
        payment = self.payment_dao.get_payment_by_order(order_id)
        if not payment:
            raise PaymentError("Payment record not found")

        if payment["status"] == "PAID":
            raise PaymentError("Payment already processed")

        # Update payment
        updated = self.payment_dao.update_payment(payment["id"], {"status": "PAID", "method": method})

        # Update order status
        self.order_dao.update_order_status(order_id, "COMPLETED")

        return updated

    def refund_payment(self, order_id: int) -> Dict:
        payment = self.payment_dao.get_payment_by_order(order_id)
        if not payment:
            raise PaymentError("Payment record not found")

        if payment["status"] != "PENDING" and payment["status"] != "PAID":
            raise PaymentError("Cannot refund payment with status " + payment["status"])

        # Update payment status to REFUNDED
        updated_payment = self.payment_dao.update_payment(payment["id"], {"status": "REFUNDED"})

        # Also ensure order status is CANCELLED if not already
        order = self.order_service.order_dao.get_order_by_id(order_id)
        if order and order["status"] != "CANCELLED":
            self.order_service.order_dao.update_order_status(order_id, "CANCELLED")

        return updated_payment
