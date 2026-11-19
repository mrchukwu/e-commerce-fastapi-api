
from app.modules.payment.service import PaymentService
from sqlalchemy.orm import Session
from app.common.dependencies import get_db
from app.modules.users.model import User
from app.common.dependencies import get_current_user
from concurrent.interpreters import get_current
from fastapi import Depends
from app.modules.payment.schemas import CreatePaymentLinkequest
from fastapi import APIRouter

router = APIRouter()

@router.post("/create-link", response_model = CreatePaymentLinkequest)
def create_payment(
  payload: CreatePaymentLinkequest,
  current_user: User = Depends(get_current_user),
  db: Session = Depends(get_db)
):
  service = PaymentService(db)
  return service.create_payment(current_user, payload)




