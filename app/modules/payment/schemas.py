from enum import Enum

from pydantic import BaseModel

from app.modules.order.schemas import OrderStatus, PaymentStatus


class PaymentProvider(str, Enum):
    RAZORPAY = "RAZORPAY"
    STRIPE = "STRIPE"


class CreatePaymentLinkequest(BaseModel):
    order_id: int
    provider: PaymentProvider


class PaymentLinkResponse(BaseModel):
    order_id: int
    provider: PaymentProvider
    amount: float
    currency: str
    payment_link: str
    provider_payment_link_id: str


class VerifyPaymentRequest(BaseModel):
    order_id: int
    provider: PaymentProvider
    payment_id: str


class PaymentVerifyResponse(BaseModel):
    order_id: int
    payment_status: PaymentStatus
    order_status: OrderStatus
    provider: PaymentProvider
    payment_id: str
