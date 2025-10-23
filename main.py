from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime, timedelta

from database import get_db, engine, Base
from models import User, Ride, Payment, Notification, UserRole, RideStatus, RideType, PaymentMethod as PaymentMethodEnum, PaymentStatus
from schemas import (
    UserCreate, User as UserSchema, LoginRequest, RegisterRequest, AuthResponse,
    RideRequest, Ride as RideSchema, RideHistory, RideEstimate,
    PaymentRequest, PaymentResponse, PaymentHistory, PaymentMethodCreate, PaymentMethodResponse,
    NotificationResponse, NotificationHistory, ErrorResponse
)
from auth import get_password_hash, verify_password, create_access_token, create_refresh_token, get_current_user, get_current_active_user
from config import settings

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TeaRide API",
    description="Backend API for TeaRide mobile application",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "TeaRide API is running"}

# Auth endpoints
@app.post("/auth/register", response_model=AuthResponse)
async def register(user_data: RegisterRequest, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.phone == user_data.phone)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or phone already exists"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        id=str(uuid.uuid4()),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
        phone=user_data.phone,
        hashed_password=hashed_password,
        role=user_data.role,
        is_verified=True  # For development, auto-verify users
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    
    return AuthResponse(
        user=UserSchema.from_orm(user),
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@app.post("/auth/login", response_model=AuthResponse)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Update last active
    user.last_active_at = datetime.utcnow()
    db.commit()
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    
    return AuthResponse(
        user=UserSchema.from_orm(user),
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@app.post("/auth/logout")
async def logout(current_user: User = Depends(get_current_active_user)):
    # In a real implementation, you might want to blacklist the token
    return {"message": "Successfully logged out"}

@app.get("/auth/me", response_model=UserSchema)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    return UserSchema.from_orm(current_user)

@app.put("/auth/profile", response_model=UserSchema)
async def update_profile(
    profile_data: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    for field, value in profile_data.items():
        if hasattr(current_user, field) and value is not None:
            setattr(current_user, field, value)
    
    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)
    
    return UserSchema.from_orm(current_user)

# Ride endpoints
@app.post("/rides/request", response_model=RideSchema)
async def request_ride(
    ride_data: RideRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # For now, create a simple ride request
    # In a real implementation, you'd calculate fare, find nearby drivers, etc.
    ride = Ride(
        id=str(uuid.uuid4()),
        status=RideStatus.REQUESTED,
        pickup_address=ride_data.pickup,
        destination_address=ride_data.destination,
        pickup_latitude=0.0,  # Would be geocoded in real implementation
        pickup_longitude=0.0,
        destination_latitude=0.0,
        destination_longitude=0.0,
        ride_type=ride_data.ride_type,
        fare=ride_data.estimated_fare or 100.0,  # Default fare
        distance=5.0,  # Default distance
        duration=15,  # Default duration
        notes=ride_data.notes,
        passenger_id=current_user.id
    )
    
    db.add(ride)
    db.commit()
    db.refresh(ride)
    
    return RideSchema.from_orm(ride)

@app.get("/rides/active", response_model=RideSchema)
async def get_active_ride(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    ride = db.query(Ride).filter(
        Ride.passenger_id == current_user.id,
        Ride.status.in_([RideStatus.REQUESTED, RideStatus.ACCEPTED, RideStatus.ARRIVED, RideStatus.STARTED])
    ).first()
    
    if not ride:
        return None
    
    return RideSchema.from_orm(ride)

@app.get("/rides/history", response_model=RideHistory)
async def get_ride_history(
    page: int = 1,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    rides = db.query(Ride).filter(
        Ride.passenger_id == current_user.id
    ).offset((page - 1) * limit).limit(limit).all()
    
    total = db.query(Ride).filter(Ride.passenger_id == current_user.id).count()
    
    return RideHistory(
        rides=[RideSchema.from_orm(ride) for ride in rides],
        total=total,
        page=page,
        limit=limit
    )

@app.post("/rides/estimate", response_model=RideEstimate)
async def get_ride_estimate(ride_data: dict):
    # Mock estimate - in real implementation, use Google Maps API
    return RideEstimate(
        distance=5.2,
        duration=15,
        fare=120.0,
        breakdown={
            "baseFare": 50.0,
            "distanceFare": 60.0,
            "timeFare": 10.0,
            "surgeMultiplier": 1.0
        }
    )

# Payment endpoints
@app.post("/payments/process", response_model=PaymentResponse)
async def process_payment(
    payment_data: PaymentRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    payment = Payment(
        id=str(uuid.uuid4()),
        amount=payment_data.amount,
        method=payment_data.method,
        status=PaymentStatus.COMPLETED,  # Mock successful payment
        transaction_id=str(uuid.uuid4()),
        description=payment_data.description,
        user_id=current_user.id,
        ride_id=payment_data.ride_id,
        completed_at=datetime.utcnow()
    )
    
    db.add(payment)
    db.commit()
    db.refresh(payment)
    
    return PaymentResponse.from_orm(payment)

@app.get("/payments/methods", response_model=List[PaymentMethodResponse])
async def get_payment_methods(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    methods = db.query(PaymentMethod).filter(PaymentMethod.user_id == current_user.id).all()
    return [PaymentMethodResponse.from_orm(method) for method in methods]

@app.post("/payments/methods", response_model=PaymentMethodResponse)
async def add_payment_method(
    method_data: PaymentMethodCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    payment_method = PaymentMethod(
        id=str(uuid.uuid4()),
        type=method_data.type,
        name=method_data.name,
        phone_number=method_data.phone_number,
        user_id=current_user.id
    )
    
    db.add(payment_method)
    db.commit()
    db.refresh(payment_method)
    
    return PaymentMethodResponse.from_orm(payment_method)

@app.get("/payments/history", response_model=PaymentHistory)
async def get_payment_history(
    page: int = 1,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    payments = db.query(Payment).filter(
        Payment.user_id == current_user.id
    ).offset((page - 1) * limit).limit(limit).all()
    
    total = db.query(Payment).filter(Payment.user_id == current_user.id).count()
    
    return PaymentHistory(
        payments=[PaymentResponse.from_orm(payment) for payment in payments],
        total=total,
        page=page,
        limit=limit
    )

# Notification endpoints
@app.get("/users/notifications", response_model=NotificationHistory)
async def get_notifications(
    page: int = 1,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).offset((page - 1) * limit).limit(limit).all()
    
    total = db.query(Notification).filter(Notification.user_id == current_user.id).count()
    
    return NotificationHistory(
        notifications=[NotificationResponse.from_orm(notif) for notif in notifications],
        total=total,
        page=page,
        limit=limit
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
