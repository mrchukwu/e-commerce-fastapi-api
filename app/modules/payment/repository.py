
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.order.schemas import PaymentStatus
from app.modules.payment.model import Payment


class PaymentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, payment: Payment) -> Payment:
        self.add(payment)
        self.db.commit()
        self.db.refresh()
        return payment

    def update(self, payment: Payment) -> Payment:
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def get_pending_by_order_and_provider(
        self, order_id: int, provider: str
    ) -> Payment | None:
        statement = select(Payment).where(
            Payment.order_id == order_id,
            Payment.provider == provider,
            Payment.status == PaymentStatus.PENDING.value,
        )
        return self.db.scalars(statement).first()

    def get_by_order_and_provider(self, order_id: int, provider: str) -> Payment | None:
        statement = select(Payment).where(
            Payment.order_id == order_id,
            Payment.provider == provider,
        ).order_by(Payment.id.desc())
        return self.db.scalars(statement).first()
