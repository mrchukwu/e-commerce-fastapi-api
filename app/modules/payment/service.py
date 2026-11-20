from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.order.repository import OrderRepository
from app.modules.order.schemas import OrderStatus, PaymentStatus
from app.modules.payment.model import Payment
from app.modules.payment.provider import RazorPayProvider, StripeProvider
from app.modules.payment.repository import PaymentRepository
from app.modules.payment.schemas import (
    CreatePaymentLinkequest,
    PaymentLinkResponse,
    PaymentProvider,
    PaymentVerifyResponse,
    VerifyPaymentRequest,
)
from app.modules.users.model import User
from app.modules.users.schemas import UserRole


class PaymentService:
    def __init__(self, db: Session):
        self.orderRepository = OrderRepository(db)
        self.paymentRepository = PaymentRepository(db)

    def _get_provider(self, provider: PaymentProvider):
        if provider == PaymentProvider.RAZORPAY:
            return RazorPayProvider()
        if provider == PaymentProvider.STRIPE:
            return StripeProvider()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="unsupported provider"
        )

    def _get_owned_order(self, order_id: int, current_user: User):
        order = self.orderRepository.get_by_id(order_id)

        # 1. Order must exist
        if order is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found",
            )

        # 2. Order must belong to this user (or user is admin)
        if (
            order.user_id != current_user.id
            and current_user.role != UserRole.ADMIN.value
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )
        # 3. ✅ Return OUTSIDE the if blocks — was missing before
        return order

    def create_payment(
        self, current_user: User, payload: CreatePaymentLinkequest
    ) -> PaymentLinkResponse:
        order = self._get_owned_order(payload.order_id, current_user)

        if order.status != OrderStatus.PENDING.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="payment link can be created for pending order",
            )

        if order.payment_status == PaymentStatus.PAID:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="order is already paid",
            )

        existing_payment = self.paymentRepository.get_by_order_and_provider(
            order.id, payload.provider.value
        )

        if existing_payment is not None:
            return PaymentLinkResponse(
                order_id=order.id,
                provider=payload.provider,
                amount=existing_payment.amount,
                currency=existing_payment.currency,
                payment_link=existing_payment.payment_link_url,
                provider_payment_link_id=existing_payment.provider_payment_link_id,
            )

        provider = self._get_provider(payload.provider)

        provider_response = provider.create_payment_link(
            order_id=order.id,
            amount=order.total_amount,
            user_email=current_user.email,
            user_name=current_user.full_name,
        )

        payment = Payment(
            order_id=order.id,
            user_id=current_user.id,
            provider=payload.provider.value,
            amount=order.total_amount,
            currency="NGN",
            status=PaymentStatus.PENDING.value,
            payment_link_url=provider_response["payment_link"],
            provider_payment_link_id=provider_response["provider_payment_link_id"],
        )

        db_payment = self.paymentRepository.create(payment)

        return PaymentLinkResponse(
            order_id=order.id,
            provider=payload.provider,
            amount=db_payment.amount,
            currency=db_payment.currency,
            payment_link=db_payment.payment_link_url,
            provider_payment_link_id=db_payment.provider_payment_link_id,
        )

    def verify_payment(self, current_user: User, payload: VerifyPaymentRequest) -> dict:
        order = self._get_owned_order(payload.order_id, current_user)

        payment = self.paymentRepository.get_by_order_and_provider(
            order.id, payload.provider.value
        )

        if payment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="payment not found"
            )

        if payment.status == PaymentStatus.PAID.value:
            return PaymentVerifyResponse(
                order_id=order.id,
                payment_status=PaymentStatus.PAID,
                order_status=order.status,
                provider=payload.provider,
                payment_id=payment.provider_payment_id,
                # payment_id=payment.provider_payment_link_id or payload.payment_id,
            ).model_dump()

        provider = self._get_provider(payload.provider)

        # Verify using the provider's Checkout Session ID
        if payload.payment_id != payment.provider_payment_link_id:
            raise HTTPException(status_code=400, detail="Invalid payment session ID")

        provider_payment = provider.get_payment_details(payload.payment_id)

        # Verify order metadata
        if str(provider_payment["order_id"]) != str(order.id):
            raise HTTPException(
                status_code=400, detail="Payment order reference mismatch"
            )

        # Verify currency
        if provider_payment["currency"].lower() != payment.currency.lower():
            raise HTTPException(
                status_code=400, detail="Payment currency does not match"
            )

        # Convert database amount to kobo
        expected_amount = int(
            (Decimal(str(order.total_amount)) * 100).quantize(Decimal("1"))
        )
        # Compare Stripe amount in kobo
        if provider_payment["amount"] != expected_amount:
            raise HTTPException(
                status_code=400, detail="Payment amount does not match order amount"
            )

        # Confirm payment
        if not provider_payment["is_paid"]:
            raise HTTPException(status_code=400, detail="Payment not completed")

        # Update payment
        payment.status = PaymentStatus.PAID.value
        payment.provider_payment_id = provider_payment["payment_id"]

        # Update order
        order.payment_status = PaymentStatus.PAID.value
        order.status = OrderStatus.CONFIRMED.value

        self.orderRepository.update(order)

        return PaymentVerifyResponse(
            order_id=order.id,
            payment_status=PaymentStatus.PAID,
            order_status=order.status,
            provider=payload.provider,
            payment_id=payment.provider_payment_id,
        ).model_dump()
