# TeaRide Backend API

A robust, scalable backend API for the TeaRide mobile application built with FastAPI.

## 🚀 Features

- **Authentication & Authorization**: JWT-based auth with role-based access control
- **Ride Management**: Complete ride lifecycle management
- **Payment Processing**: Multiple payment methods support
- **Real-time Notifications**: User notification system
- **Scalable Architecture**: Clean separation of concerns
- **Comprehensive Testing**: Unit and integration tests
- **API Documentation**: Auto-generated OpenAPI docs

## 📁 Project Structure

```
tearide-backend/
├── app/
│   ├── api/                    # API routes
│   │   └── v1/                # API version 1
│   │       ├── auth.py        # Authentication endpoints
│   │       ├── users.py       # User management
│   │       ├── rides.py       # Ride management
│   │       ├── payments.py    # Payment processing
│   │       └── notifications.py # Notifications
│   ├── core/                  # Core functionality
│   │   ├── config.py         # Configuration
│   │   ├── database.py       # Database setup
│   │   └── security.py       # Security utilities
│   ├── models/               # Database models
│   │   ├── user.py
│   │   ├── ride.py
│   │   ├── payment.py
│   │   ├── rating.py
│   │   └── notification.py
│   ├── schemas/              # Pydantic schemas
│   │   ├── user.py
│   │   ├── ride.py
│   │   ├── payment.py
│   │   ├── notification.py
│   │   ├── auth.py
│   │   └── common.py
│   ├── services/             # Business logic
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── ride_service.py
│   │   ├── payment_service.py
│   │   └── notification_service.py
│   ├── middleware/           # Custom middleware
│   │   └── auth.py
│   └── main.py              # Application entry point
├── tests/                   # Test files
├── alembic/                 # Database migrations
├── requirements.txt         # Dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd tearide-backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start the development server**
   ```bash
   python -m uvicorn app.main:app --reload
   ```

## 🔧 Configuration

The application uses environment variables for configuration. Copy `.env.example` to `.env` and update the values:

### Required Variables
- `SECRET_KEY`: JWT secret key
- `DATABASE_URL`: Database connection string
- `REDIS_URL`: Redis connection string

### Optional Variables
- `DEBUG`: Enable debug mode (default: true)
- `ENVIRONMENT`: Environment name (development/production)
- `ALLOWED_ORIGINS`: CORS allowed origins

## 📚 API Documentation

Once the server is running, you can access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🧪 Testing

Run tests with pytest:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py
```

## 🚀 Deployment

### Production Setup

1. **Set production environment variables**
   ```bash
   export ENVIRONMENT=production
   export DEBUG=false
   export SECRET_KEY=your-production-secret-key
   ```

2. **Use production database**
   ```bash
   export DATABASE_URL=postgresql://user:password@localhost/tearide
   ```

3. **Run with production server**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🔐 Security Features

- JWT-based authentication
- Password hashing with bcrypt
- CORS protection
- Request validation
- Rate limiting (configurable)
- Input sanitization

## 📊 Database Schema

The application uses SQLAlchemy ORM with the following main entities:

- **Users**: Passenger, driver, and admin accounts
- **Rides**: Ride requests and tracking
- **Payments**: Payment processing and history
- **Notifications**: User notifications
- **Ratings**: Driver and passenger ratings

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions, please contact the development team or create an issue in the repository.

