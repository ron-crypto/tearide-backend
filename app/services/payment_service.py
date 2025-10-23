from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional, List
from datetime import datetime
import uuid

from app.models.payment import Payment, PaymentMethod, PaymentStatus, PaymentMethodType
from app.schemas.payment import PaymentRequest, PaymentMethodCreate

class PaymentService:
    def __init__(self, db: Session):
        self.db = db
    
    def process_payment(self, payment_data: PaymentRequest, user_id: str) -> Payment:
        """Process a payment."""
        payment = Payment(
            id=str(uuid.uuid4()),
            amount=payment_data.amount,
            method=payment_data.method,
            status=PaymentStatus.COMPLETED,  # Mock successful payment
            transaction_id=str(uuid.uuid4()),
            description=payment_data.description,
            user_id=user_id,
            ride_id=payment_data.ride_id,
            completed_at=datetime.utcnow()
        )
        
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        
        return payment
    
    def get_payment_methods(self, user_id: str) -> List[PaymentMethod]:
        """Get user's payment methods."""
        return self.db.query(PaymentMethod).filter(PaymentMethod.user_id == user_id).all()
    
    def add_payment_method(self, method_data: PaymentMethodCreate, user_id: str) -> PaymentMethod:
        """Add a new payment method for user."""
        # If this is set as default, unset other defaults
        if method_data.is_default:
            self.db.query(PaymentMethod).filter(
                PaymentMethod.user_id == user_id,
                PaymentMethod.is_default == True
            ).update({"is_default": False})
        
        payment_method = PaymentMethod(
            id=str(uuid.uuid4()),
            type=method_data.type,
            name=method_data.name,
            phone_number=method_data.phone_number,
            is_default=method_data.is_default,
            user_id=user_id
        )
        
        self.db.add(payment_method)
        self.db.commit()
        self.db.refresh(payment_method)
        
        return payment_method
    
    def get_payment_history(self, user_id: str, page: int = 1, limit: int = 20) -> tuple[List[Payment], int]:
        """Get user's payment history."""
        payments = self.db.query(Payment).filter(
            Payment.user_id == user_id
        ).offset((page - 1) * limit).limit(limit).all()
        
        total = self.db.query(Payment).filter(Payment.user_id == user_id).count()
        
        return payments, total
    
    def get_payment_by_id(self, payment_id: str) -> Optional[Payment]:
        """Get payment by ID."""
        return self.db.query(Payment).filter(Payment.id == payment_id).first()
    
    def refund_payment(self, payment_id: str) -> Payment:
        """Refund a payment."""
        payment = self.get_payment_by_id(payment_id)
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        
        if payment.status != PaymentStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only completed payments can be refunded"
            )
        
        payment.status = PaymentStatus.REFUNDED
        self.db.commit()
        self.db.refresh(payment)
        
        return payment

