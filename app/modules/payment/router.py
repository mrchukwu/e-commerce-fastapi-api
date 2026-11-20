from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.common.dependencies import get_current_user, get_db
from app.modules.payment.schemas import (
    CreatePaymentLinkequest,
    PaymentLinkResponse,
    VerifyPaymentRequest,
)
from app.modules.payment.service import PaymentService
from app.modules.users.model import User

router = APIRouter()


@router.post("/create-link", response_model=PaymentLinkResponse)
def create_payment(
    payload: CreatePaymentLinkequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = PaymentService(db)
    return service.create_payment(current_user, payload)


@router.post("/verify", response_model=dict)
def verify_payment(
    payload: VerifyPaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = PaymentService(db)
    return service.verify_payment(current_user, payload)
