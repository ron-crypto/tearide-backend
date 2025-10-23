# TeaRide Backend - Project Structure

## 📁 Directory Overview

```
tearide-backend/
├── app/                          # Main application package
│   ├── __init__.py
│   ├── main.py                  # FastAPI application entry point
│   ├── core/                    # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py           # Application configuration
│   │   ├── database.py         # Database connection & session
│   │   └── security.py         # Security utilities (JWT, password hashing)
│   ├── models/                 # SQLAlchemy database models
│   │   ├── __init__.py
│   │   ├── user.py            # User model
│   │   ├── ride.py            # Ride model
│   │   ├── payment.py         # Payment & PaymentMethod models
│   │   ├── rating.py           # Rating model
│   │   └── notification.py     # Notification model
│   ├── schemas/                # Pydantic schemas for API serialization
│   │   ├── __init__.py
│   │   ├── user.py            # User schemas
│   │   ├── ride.py             # Ride schemas
│   │   ├── payment.py          # Payment schemas
│   │   ├── notification.py     # Notification schemas
│   │   ├── auth.py             # Authentication schemas
│   │   └── common.py           # Common schemas (Error, Success)
│   ├── services/               # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py     # Authentication business logic
│   │   ├── user_service.py     # User management business logic
│   │   ├── ride_service.py     # Ride management business logic
│   │   ├── payment_service.py  # Payment processing business logic
│   │   └── notification_service.py # Notification business logic
│   ├── api/                    # API routes
│   │   ├── __init__.py
│   │   └── v1/                 # API version 1
│   │       ├── __init__.py
│   │       ├── auth.py         # Authentication endpoints
│   │       ├── users.py        # User management endpoints
│   │       ├── rides.py        # Ride management endpoints
│   │       ├── payments.py     # Payment endpoints
│   │       └── notifications.py # Notification endpoints
│   └── middleware/             # Custom middleware
│       ├── __init__.py
│       └── auth.py             # Authentication middleware
├── tests/                      # Test files
│   ├── __init__.py
│   ├── conftest.py            # Test configuration
│   └── test_auth.py           # Authentication tests
├── scripts/                    # Utility scripts
│   └── init_db.py             # Database initialization
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── run.py                     # Application startup script
├── README.md                  # Project documentation
└── PROJECT_STRUCTURE.md       # This file
```

## 🏗️ Architecture Principles

### 1. **Separation of Concerns**
- **Models**: Database entities and relationships
- **Schemas**: API request/response validation
- **Services**: Business logic and data processing
- **API Routes**: HTTP endpoint definitions
- **Core**: Configuration and shared utilities

### 2. **Dependency Injection**
- Database sessions injected into services
- Services injected into API routes
- Authentication dependencies for protected routes

### 3. **Error Handling**
- Global exception handlers in main.py
- Service-level error handling
- Consistent error response format

### 4. **Security**
- JWT-based authentication
- Password hashing with bcrypt
- CORS protection
- Input validation with Pydantic

## 🔄 Data Flow

```
Client Request → API Route → Service Layer → Database Model
                     ↓
Client Response ← Schema ← Service Layer ← Database Model
```

## 🚀 Getting Started

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Set up environment**: Copy `.env.example` to `.env`
3. **Initialize database**: `python scripts/init_db.py`
4. **Run application**: `python run.py`

## 📊 Key Features

- **Modular Design**: Easy to extend and maintain
- **Type Safety**: Full type hints throughout
- **Testing Ready**: Comprehensive test structure
- **Documentation**: Auto-generated API docs
- **Scalable**: Clean separation allows for microservices migration

