import argparse
import json
from src.dao.product_dao import ProductDAO
from src.services.product_service import ProductService
from src.dao.customer_dao import CustomerDAO
from src.services.customer_service import CustomerService
from src.dao.order_dao import OrderDAO
from src.services.order_service import OrderService
from src.dao.payment_dao import PaymentDAO
from src.services.payment_service import PaymentService, PaymentError


class RetailCLI:
    def __init__(self):
        self.product_service = ProductService(ProductDAO())
        self.customer_service = CustomerService(CustomerDAO())
        self.order_service = OrderService(OrderDAO(), CustomerDAO(), ProductDAO())
        self.payment_service = PaymentService(
            PaymentDAO(),
            OrderDAO(),
            self.order_service
        )

    # ----------------- PRODUCTS -----------------
    def cmd_product_add(self, args):
        try:
            p = self.product_service.add_product(
                args.name, args.sku, args.price, args.stock, args.category
            )
            print(json.dumps(p, indent=2, default=str))
        except Exception as e:
            print("Error:", e)

    def cmd_product_list(self, args):
        ps = self.product_service.dao.list_products(limit=100)
        print(json.dumps(ps, indent=2, default=str))

    # ----------------- CUSTOMERS -----------------
    def cmd_customer_add(self, args):
        try:
            c = self.customer_service.add_customer(
                args.name, args.email, args.phone, args.city
            )
            print(json.dumps(c, indent=2, default=str))
        except Exception as e:
            print("Error:", e)

    def cmd_customer_update(self, args):
        try:
            c = self.customer_service.update_customer(args.id, args.phone, args.city)
            print(json.dumps(c, indent=2, default=str))
        except Exception as e:
            print("Error:", e)

    def cmd_customer_delete(self, args):
        try:
            c = self.customer_service.delete_customer(args.id)
            print("Deleted:", json.dumps(c, indent=2, default=str))
        except Exception as e:
            print("Error:", e)

    def cmd_customer_list(self, args):
        cs = self.customer_service.list_customers()
        print(json.dumps(cs, indent=2, default=str))

    def cmd_customer_search(self, args):
        try:
            if args.email:
                c = self.customer_service.search_by_email(args.email)
                print(json.dumps(c, indent=2, default=str))
            elif args.city:
                cs = self.customer_service.search_by_city(args.city)
                print(json.dumps(cs, indent=2, default=str))
        except Exception as e:
            print("Error:", e)

    # ----------------- ORDERS -----------------
    def cmd_order_create(self, args):
        try:
            items = []
            for item in args.item:
                pid, qty = item.split(":")
                items.append({"prod_id": int(pid), "quantity": int(qty)})
            o = self.order_service.create_order(args.customer, items)
            print(json.dumps(o, indent=2, default=str))
            # Optional: create payment right after order creation
            # payment = self.payment_service.create_payment_for_order(o["id"])
            # print("Payment record created:", json.dumps(payment, indent=2, default=str))
        except Exception as e:
            print("Error:", e)

    def cmd_order_show(self, args):
        try:
            o = self.order_service.get_order_details(args.id)
            print(json.dumps(o, indent=2, default=str))
        except Exception as e:
            print("Error:", e)

    def cmd_order_list(self, args):
        try:
            os = self.order_service.list_orders_by_customer(args.customer)
            print(json.dumps(os, indent=2, default=str))
        except Exception as e:
            print("Error:", e)

    def cmd_order_cancel(self, args):
        try:
            o = self.order_service.cancel_order(args.id)
            # Also refund payment when order cancelled
            refund = self.payment_service.refund_payment(args.id)
            print(json.dumps({"order": o, "payment_refund": refund}, indent=2, default=str))
        except (Exception, PaymentError) as e:
            print("Error:", e)

    def cmd_order_complete(self, args):
        try:
            # Mark order as complete and process payment
            payment = self.payment_service.process_payment(args.id, args.method)
            print(json.dumps(payment, indent=2, default=str))
        except (Exception, PaymentError) as e:
            print("Error:", e)

    # ----------------- PAYMENTS -----------------
    def cmd_payment_create(self, args):
        try:
            payment = self.payment_service.create_payment_for_order(args.order)
            print(json.dumps(payment, indent=2, default=str))
        except (Exception, PaymentError) as e:
            print("Error:", e)

    def cmd_payment_process(self, args):
        try:
            payment = self.payment_service.process_payment(args.order, args.method)
            print(json.dumps(payment, indent=2, default=str))
        except (Exception, PaymentError) as e:
            print("Error:", e)

    def cmd_payment_refund(self, args):
        try:
            refund = self.payment_service.refund_payment(args.order)
            print(json.dumps(refund, indent=2, default=str))
        except (Exception, PaymentError) as e:
            print("Error:", e)

    # ----------------- ARG PARSER -----------------
    def build_parser(self):
        parser = argparse.ArgumentParser(prog="retail-cli")
        sub = parser.add_subparsers(dest="cmd")

        # PRODUCTS
        p_prod = sub.add_parser("product", help="product commands")
        pprod_sub = p_prod.add_subparsers(dest="action")

        addp = pprod_sub.add_parser("add")
        addp.add_argument("--name", required=True)
        addp.add_argument("--sku", required=True)
        addp.add_argument("--price", type=float, required=True)
        addp.add_argument("--stock", type=int, default=0)
        addp.add_argument("--category", default=None)
        addp.set_defaults(func=self.cmd_product_add)

        listp = pprod_sub.add_parser("list")
        listp.set_defaults(func=self.cmd_product_list)

        # CUSTOMERS
        p_cust = sub.add_parser("customer", help="customer commands")
        pcust_sub = p_cust.add_subparsers(dest="action")

        addc = pcust_sub.add_parser("add")
        addc.add_argument("--name", required=True)
        addc.add_argument("--email", required=True)
        addc.add_argument("--phone", required=True)
        addc.add_argument("--city", required=True)
        addc.set_defaults(func=self.cmd_customer_add)

        updatec = pcust_sub.add_parser("update")
        updatec.add_argument("--id", type=int, required=True)
        updatec.add_argument("--phone")
        updatec.add_argument("--city")
        updatec.set_defaults(func=self.cmd_customer_update)

        deletec = pcust_sub.add_parser("delete")
        deletec.add_argument("--id", type=int, required=True)
        deletec.set_defaults(func=self.cmd_customer_delete)

        listc = pcust_sub.add_parser("list")
        listc.set_defaults(func=self.cmd_customer_list)

        searchc = pcust_sub.add_parser("search")
        searchc.add_argument("--email")
        searchc.add_argument("--city")
        searchc.set_defaults(func=self.cmd_customer_search)

        # ORDERS
        p_order = sub.add_parser("order", help="order commands")
        porder_sub = p_order.add_subparsers(dest="action")

        createo = porder_sub.add_parser("create")
        createo.add_argument("--customer", type=int, required=True)
        createo.add_argument("--item", required=True, nargs="+", help="prod_id:qty")
        createo.set_defaults(func=self.cmd_order_create)

        showo = porder_sub.add_parser("show")
        showo.add_argument("--id", type=int, required=True)
        showo.set_defaults(func=self.cmd_order_show)

        listo = porder_sub.add_parser("list")
        listo.add_argument("--customer", type=int, required=True)
        listo.set_defaults(func=self.cmd_order_list)

        cano = porder_sub.add_parser("cancel")
        cano.add_argument("--id", type=int, required=True)
        cano.set_defaults(func=self.cmd_order_cancel)

        completo = porder_sub.add_parser("complete")
        completo.add_argument("--id", type=int, required=True)
        completo.add_argument("--method", choices=["Cash", "Card", "UPI"], required=True)
        completo.set_defaults(func=self.cmd_order_complete)

        # PAYMENTS
        p_pay = sub.add_parser("payment", help="payment commands")
        ppay_sub = p_pay.add_subparsers(dest="action")

        createp = ppay_sub.add_parser("create")
        createp.add_argument("--order", type=int, required=True)
        createp.set_defaults(func=self.cmd_payment_create)

        processp = ppay_sub.add_parser("process")
        processp.add_argument("--order", type=int, required=True)
        processp.add_argument("--method", choices=["Cash", "Card", "UPI"], required=True)
        processp.set_defaults(func=self.cmd_payment_process)

        refundp = ppay_sub.add_parser("refund")
        refundp.add_argument("--order", type=int, required=True)
        refundp.set_defaults(func=self.cmd_payment_refund)

        return parser

    def run(self):
        parser = self.build_parser()
        args = parser.parse_args()
        if not hasattr(args, "func"):
            parser.print_help()
            return
        args.func(args)


if __name__ == "__main__":
    RetailCLI().run()
