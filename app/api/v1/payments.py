from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import verify_token
from app.services.payment_service import PaymentService
from app.services.auth_service import AuthService
from app.schemas.payment import (
    PaymentRequest, PaymentResponse, PaymentHistory, 
    PaymentMethodCreate, PaymentMethodResponse
)
from app.schemas.common import SuccessResponse

router = APIRouter(prefix="/payments", tags=["Payments"])

def get_current_user(token: str = Depends(verify_token), db: Session = Depends(get_db)):
    """Get current authenticated user."""
    auth_service = AuthService(db)
    user = auth_service.get_user_by_email(token["sub"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.post("/process", response_model=PaymentResponse)
async def process_payment(
    payment_data: PaymentRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process a payment."""
    payment_service = PaymentService(db)
    return payment_service.process_payment(payment_data, current_user.id)

@router.get("/methods", response_model=List[PaymentMethodResponse])
async def get_payment_methods(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's payment methods."""
    payment_service = PaymentService(db)
    return payment_service.get_payment_methods(current_user.id)

@router.post("/methods", response_model=PaymentMethodResponse)
async def add_payment_method(
    method_data: PaymentMethodCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a new payment method."""
    payment_service = PaymentService(db)
    return payment_service.add_payment_method(method_data, current_user.id)

@router.get("/history", response_model=PaymentHistory)
async def get_payment_history(
    page: int = 1,
    limit: int = 20,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's payment history."""
    payment_service = PaymentService(db)
    payments, total = payment_service.get_payment_history(current_user.id, page, limit)
    
    return PaymentHistory(
        payments=payments,
        total=total,
        page=page,
        limit=limit
    )

@router.post("/{payment_id}/refund", response_model=PaymentResponse)
async def refund_payment(
    payment_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Refund a payment."""
    payment_service = PaymentService(db)
    return payment_service.refund_payment(payment_id)

