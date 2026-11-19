
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.order.repository import OrderRepository
from app.modules.order.schemas import OrderStatus, PaymentStatus
from app.modules.payment.model import Payment
from app.modules.payment.repository import PaymentRepository
from app.modules.payment.schemas import CreatePaymentLinkequest, PaymentLinkResponse
from app.modules.users.model import User
from app.modules.users.schemas import UserRole


class PaymentService:
    def __init__(self, db: Session):
        self.orderRepository = OrderRepository(db)
        self.paymentRepository = PaymentRepository(db)

    def _get_owned_oder(self, order_id: int, current_user: User):
        order = self.orderRepository.get_by_id(order_id)

        if order is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_Found, detail="order not found"
            )

        if (
            order.user_id != current_user.id
            and current_user.role != UserRole.ADMIN.value
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="access denied"
            )
            return order

    def create_payment(
        self, current_user: User, payload: CreatePaymentLinkequest
    ) -> PaymentLinkResponse:
        order = self._get_owned_oder(payload.order_id, current_user)

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
                payment_link=existing_payment.currency,
                provider_payment_link_id=existing_payment.provider_payment_link_id,
            )

        payment = Payment(
            order_id=order.id,
            user_id=current_user.id,
            provider=payload.provider.value,
            amount=order.total_amount,
            currency="NIG",
            status=PaymentStatus.PENDING.value,
            payment_link="dummy link",
            provider_payment_link_id="dummy payment link id",
        )

        db_payment = self.paymentRepository.create(payment)

        return PaymentLinkResponse(
          order_id=order.id,
          procider = payload.provider,
          amount=db_payment.amount,
          curency=db_payment.currency,
          payment_link=db_payment.payment_link_url,
          provider_payment_link_id=db_payment.provider_payment_link_id
        )
