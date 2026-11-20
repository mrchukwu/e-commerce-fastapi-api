from decimal import Decimal

import razorpay
import stripe
from fastapi import HTTPException, status

from app.core.config import settings


class RazorPayProvider:
    def __init__(self) -> None:
        self.client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

    def create_payment_link(
        self, order_id: int, amount: float, user_email: str, user_name: str
    ) -> dict:

        # 1 ruppes = 100 paisa
        create_payment_link_request = {
            "amount": amount,
            "currency": "NGN",
            "accept_partial": False,
            "refrence_id": f"order_{order_id}",
            "description": f"payment for order #{order_id}",
            "customer": {"name": user_name, "email": user_email},
            "notify": {"sms": False, "email": False},
            "callback_url": "http://localhost:8000/api/v1/payments/razorpay/callback",
            "callback_method": "GET",
        }

        try:
            response = self.client.payment_link.create(create_payment_link_request)
        except Exception as exc:
            raise HTTPException(
                status_code=status.WS_1014_BAD_GATEWAY,
                detail="unavle to create razorpay payment link",
            )

        print(f"response {response}")

        return {
            "payment_link": response["short_url"],
            "provder_payment_link_id": response["id"],
        }

    def get_payment_details(self, payment_id: str) -> dict:
        try:
            payment = self.client.payment.fetch(payment_id)

        except Exception as exc:
            raise HTTPException(
                status_code=status.WS_1014_BAD_GATEWAY,
                detail="unable to verify razorpay payment",
            )

        print("payment details", payment["id"], payment["amount", payment["status"]])

        return {
            "payment_id": payment["id"],
            "amount": payment["amout"],
            "status": payment["status"],
            "is_paid": payment["status"] == "captured",
        }


class StripeProvider:
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY

    def create_payment_link(
        self, order_id: int, amount: float, user_email: str, user_name: str
    ) -> dict:

        try:
            unit_amount = int(Decimal(str(amount)) * 100)

            session = stripe.checkout.Session.create(
                mode="payment",
                customer_email=user_email,
                line_items=[
                    {
                        "price_data": {
                            "currency": "ngn",
                            "product_data": {
                                "name": f"Order #{order_id}",
                                "description": f"Payment for order #{order_id} by {user_name}",
                            },
                            "unit_amount": unit_amount,
                        },
                        "quantity": 1,
                    }
                ],
                success_url="http://localhost:8000/api/v1/payments/success",
                cancel_url="http://localhost:8000/api/v1/payments/failed",
                metadata={"order_id": str(order_id)},
            )

            return {"payment_link": session.url, "provider_payment_link_id": session.id}

        except Exception as exc:
            print(f"Stripe error: {exc}")
            raise HTTPException(
                status_code=502, detail="Unable to create Stripe payment link"
            )

    def get_payment_details(self, payment_id: str) -> dict:

        try:
            session = stripe.checkout.Session.retrieve(payment_id)

            return {
                "payment_id": session.id,
                "amount": session.amount_total,
                "currency": session.currency,
                "status": session.payment_status,
                "session_status": session.status,
                "order_id": session.metadata.get("order_id"),
                "is_paid": session.payment_status == "paid",
            }

        except Exception as exc:
            print(f"Stripe verification error: {exc}")

            raise HTTPException(
                status_code=502, detail="Unable to fetch Stripe payment details"
            )


# class StripeProvider:
#     def __init__(self):
#         stripe.api_key = settings.STRIPE_SECRET_KEY

#     def create_payment_link(
#         self, order_id: int, amount: float, user_email: str, user_name: str
#     ) -> dict:
#         try:
#             session = stripe.checkout.Session.create(
#                 mode="payment",
#                 customer_email=user_email,
#                 line_items=[
#                     {
#                         "price_data": {
#                             "currency": "NGN",
#                             "product_data": {
#                                 "name": f"Order #{order_id}",
#                                 "description": f"payment for order #{order_id} by {user_name}",
#                             },
#                             "unit_amount": round(int(amount * 100), 2),
#                         },
#                         "quantity": 1,
#                     }
#                 ],
#                 success_url="http://localhost:8000/api/v1/payments/success",
#                 cancel_url="http://localhost:8000/api/v1/payments/failed",
#                 metadata={"order_id": str(order_id)},
#             )

#             print(f"session ----- {session}")
#             return {"payment_link": session.url, "provider_payment_link_id": session.id}

#         except Exception as exc:
#             raise HTTPException(
#                 status_code=status.HTTP_502_BAD_GATEWAY,
#                 detail="unable to create stripe payment link",
#             )


#     def get_payment_details(self, payment_id: str) -> dict:
#         try:
#             session = stripe.checkout.Session.retrieve(payment_id)

#             return {
#             "payment_id": session.id,
#             "amount": session.amount_total,
#             "currency": session.currency,
#             "status": session.payment_status,
#             "session_status": session.status,
#             "order_id": session.metadata.get("order_id"),
#             "is_paid": session.payment_status == "paid",
#         }

#         except Exception as exc:
#             print(f"Stripe error: {exc}")

#         raise HTTPException(
#             status_code=status.HTTP_502_BAD_GATEWAY,
#             detail="Unable to fetch payment details",
#         )
