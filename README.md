# 🥬 VegGo - Complete Vegetable Delivery Platform

A comprehensive vegetable delivery platform built with **FastAPI**, **MongoDB**, and **Google Maps API**.

## 🌟 Features

### 👥 User System
- Normal signup/login with email verification
- Google OAuth login (ready to implement)
- Password reset via email
- Profile management with location
- View past deliveries and order history
- Real-time order tracking with agent location
- Cancel orders within 5 minutes

### 🚴 Delivery Agent System
- Separate agent signup area
- Admin approval required
- Real-time location updates
- View and manage assigned orders
- Update order status

### 👨‍💼 Admin Panel
- Manage users, agents, products, orders
- Approve/block delivery agents
- Add/edit/delete products
- Set products as in-stock or out-of-stock
- Assign orders to agents
- Track all agents on map
- **Edit delivery fee settings** (base fee, price per km, price per meter)
- View dashboard statistics

### 📦 Product Management
- Multiple unit types: Kg, Piece, or Both
- Stock management for each unit type
- Product categories
- Image URLs
- Availability status

### 📝 Order System
- Place orders with multiple products
- Automatic delivery fee calculation based on distance
- Real-time order status updates
- Order cancellation within 5 minutes
- Email notifications for all order events

### 📧 Email Notifications
- Signup verification
- Order confirmation
- Order status updates
- Agent assignment notification
- Order cancellation
- Agent approval/rejection
- Password reset

### 🗺️ Google Maps Integration
- Distance calculation using Google Maps API
- Real-time agent tracking
- Delivery fee based on distance
- Fallback to Haversine formula

## 🚀 Installation

### Prerequisites
- Python 3.9+
- MongoDB Atlas account (or local MongoDB)
- Google Maps API key
- SMTP email account (Gmail recommended)

### 1. Clone or Extract

```bash
cd veggo-platform
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Create a `.env` file in the root directory:

```env
# MongoDB Configuration
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
DATABASE_NAME=veggo_db

# JWT Configuration
SECRET_KEY=your-super-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Email Configuration (Gmail example)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password
FROM_EMAIL=noreply@veggo.com
FROM_NAME=VegGo Platform

# Google Maps API
GOOGLE_MAPS_API_KEY=your-google-maps-api-key

# Delivery Fee Configuration (Can be changed by admin)
BASE_DELIVERY_FEE=50
PRICE_PER_KM=10
PRICE_PER_METER=0.01

# App Configuration
FRONTEND_URL=http://localhost:3000
ORDER_CANCEL_TIME_MINUTES=5
```

### 5. Initialize Database

```bash
python init_db.py
```

This will:
- Create default admin account
- Set up database indexes
- Add sample products
- Initialize delivery settings

**Default Admin Credentials:**
- Email: `admin@veggo.com`
- Password: `admin123`

⚠️ **Change the admin password immediately after first login!**

### 6. Run the Application

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

## 📚 API Endpoints

### User Endpoints
- `POST /api/user/signup` - User registration
- `POST /api/user/login` - User login
- `GET /api/user/verify-email?token=xxx` - Verify email
- `POST /api/user/reset-password` - Request password reset
- `GET /api/user/profile` - Get user profile
- `PUT /api/user/profile/update` - Update profile
- `GET /api/user/orders` - Get all user orders (including past)

### Agent Endpoints
- `POST /api/agent/signup` - Agent registration
- `POST /api/agent/login` - Agent login
- `GET /api/agent/profile` - Get agent profile
- `GET /api/agent/orders` - Get assigned orders
- `PUT /api/agent/update-location` - Update location
- `PUT /api/agent/order-status/{orderId}` - Update order status

### Admin Endpoints
- `POST /api/admin/login` - Admin login
- `GET /api/admin/dashboard` - Dashboard statistics
- `GET /api/admin/users` - List all users
- `GET /api/admin/agents` - List all agents
- `PUT /api/admin/agent/approve/{agentId}` - Approve/reject agent
- `POST /api/admin/product/add` - Add product
- `PUT /api/admin/product/update/{id}` - Update product
- `DELETE /api/admin/product/delete/{id}` - Delete product
- `GET /api/admin/orders` - List all orders
- `PUT /api/admin/order/status/{orderId}` - Update order status
- `PUT /api/admin/order/assign-agent/{orderId}` - Assign agent
- `GET /api/admin/delivery-settings` - Get delivery fee settings
- `PUT /api/admin/delivery-settings` - Update delivery fee settings

### Product Endpoints (Public)
- `GET /api/products` - List all products
- `GET /api/product/{id}` - Get single product
- `GET /api/categories` - Get all categories

### Order Endpoints
- `POST /api/order/create` - Create order
- `GET /api/order/{orderId}` - Get order details
- `PUT /api/order/cancel/{orderId}` - Cancel order (within 5 minutes)

## 🔐 Authentication

All authenticated endpoints require a Bearer token in the Authorization header:

```
Authorization: Bearer <your_token>
```

Token is returned after successful login/signup.

## 📱 Email Notifications

Users receive emails for:
1. **Signup** - Email verification link
2. **Order Confirmation** - Order details
3. **Order Assigned** - Agent information
4. **Order Status Updates** - Status changes
5. **Order Cancellation** - Cancellation confirmation
6. **Password Reset** - Reset link

Agents receive emails for:
1. **Account Approval/Rejection**

## 🗺️ Google Maps Setup

1. Get API key from [Google Cloud Console](https://console.cloud.google.com/)
2. Enable these APIs:
   - Distance Matrix API
   - Geocoding API
3. Add the API key to `.env` file

## 💰 Delivery Fee Calculation

Formula:
```
Delivery Fee = Base Fee + (Distance in KM × Price per KM)
```

Admin can update:
- Base Delivery Fee
- Price per KM
- Price per Meter

Settings are stored in database and applied to all new orders.

## 📦 Database Collections

1. **users** - Customer accounts
2. **admins** - Admin accounts
3. **agents** - Delivery agent accounts
4. **products** - Product catalog
5. **orders** - Order records
6. **delivery_settings** - Delivery fee configuration

## 🚀 Deployment to Vercel

### Prerequisites
- Vercel account
- Vercel CLI installed

### Steps

1. **Login to Vercel**
```bash
vercel login
```

2. **Configure Environment Variables**

Go to your Vercel project settings and add these environment variables:
- `MONGODB_URI`
- `DATABASE_NAME`
- `SECRET_KEY`
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USER`
- `SMTP_PASSWORD`
- `FROM_EMAIL`
- `GOOGLE_MAPS_API_KEY`
- `FRONTEND_URL`

3. **Deploy**
```bash
vercel --prod
```

## 🔧 Development

### Run Tests
```bash
pytest
```

### Code Formatting
```bash
black .
```

### Linting
```bash
flake8
```

## 📋 Key Features Implemented

✅ Separate signup areas for Users, Agents, and Admin  
✅ Email verification  
✅ Password reset  
✅ Google Maps distance calculation  
✅ Automatic delivery fee calculation  
✅ Real-time agent tracking  
✅ Order cancellation within 5 minutes  
✅ Email notifications for all events  
✅ Admin can edit delivery fees (base, per km, per meter)  
✅ Product stock management (in-stock/out-of-stock)  
✅ Past delivery history for users  
✅ JWT authentication  
✅ CORS enabled  
✅ Ready for mobile app integration  
✅ Vercel deployment ready  

## 🛡️ Security Features

- Password hashing with bcrypt
- JWT token authentication
- Email verification
- Admin approval for agents
- Time-limited order cancellation
- Secure password reset

## 📞 Support

For issues or questions, please contact support or create an issue.

## 📄 License

MIT License

---

**Built with ❤️ for VegGo Platform**
