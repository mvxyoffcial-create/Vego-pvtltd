# VegGo API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
Most endpoints require a Bearer token:
```
Authorization: Bearer <your_token>
```

---

## 👥 USER ENDPOINTS

### 1. User Signup
**POST** `/api/user/signup`

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123",
  "phone": "1234567890",
  "address": "123 Main St",
  "lat": 28.6139,
  "lng": 77.2090
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### 2. User Login
**POST** `/api/user/login`

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

### 3. Verify Email
**GET** `/api/user/verify-email?token=<verification_token>`

### 4. Reset Password Request
**POST** `/api/user/reset-password`

**Request Body:**
```json
{
  "email": "john@example.com"
}
```

### 5. Get Profile
**GET** `/api/user/profile`

**Headers:** `Authorization: Bearer <token>`

### 6. Update Profile
**PUT** `/api/user/profile/update`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "username": "john_updated",
  "phone": "9876543210",
  "address": "456 New St",
  "lat": 28.7041,
  "lng": 77.1025
}
```

### 7. Get User Orders (Past Deliveries)
**GET** `/api/user/orders`

**Headers:** `Authorization: Bearer <token>`

---

## 🚴 AGENT ENDPOINTS

### 1. Agent Signup
**POST** `/api/agent/signup`

**Request Body:**
```json
{
  "name": "Mike Wilson",
  "phone": "1234567890",
  "email": "mike@example.com",
  "password": "AgentPass123",
  "vehicle_type": "bike",
  "license_number": "DL123456"
}
```

### 2. Agent Login
**POST** `/api/agent/login`

**Request Body:**
```json
{
  "email": "mike@example.com",
  "password": "AgentPass123"
}
```

### 3. Get Agent Profile
**GET** `/api/agent/profile`

**Headers:** `Authorization: Bearer <token>`

### 4. Get Assigned Orders
**GET** `/api/agent/orders`

**Headers:** `Authorization: Bearer <token>`

### 5. Update Location
**PUT** `/api/agent/update-location`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "lat": 28.6139,
  "lng": 77.2090
}
```

### 6. Update Order Status
**PUT** `/api/agent/order-status/{order_id}`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "status": "picked_up"
}
```

**Status Options:**
- `pending`
- `confirmed`
- `assigned`
- `picked_up`
- `in_transit`
- `delivered`
- `cancelled`

---

## 👨‍💼 ADMIN ENDPOINTS

### 1. Admin Login
**POST** `/api/admin/login`

**Request Body:**
```json
{
  "email": "admin@veggo.com",
  "password": "admin123"
}
```

### 2. Get Dashboard Stats
**GET** `/api/admin/dashboard`

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "total_users": 150,
  "total_agents": 25,
  "pending_agents": 5,
  "total_products": 50,
  "total_orders": 500,
  "pending_orders": 10
}
```

### 3. Get All Users
**GET** `/api/admin/users`

**Headers:** `Authorization: Bearer <token>`

### 4. Get All Agents
**GET** `/api/admin/agents`

**Headers:** `Authorization: Bearer <token>`

### 5. Approve/Reject Agent
**PUT** `/api/admin/agent/approve/{agent_id}?approve=true`

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `approve`: `true` or `false`

### 6. Add Product
**POST** `/api/admin/product/add`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "Tomato",
  "imageUrl": "https://example.com/tomato.jpg",
  "unitType": "Kg",
  "pricePerKg": 40.0,
  "pricePerPiece": null,
  "stockKg": 100.0,
  "stockPieces": null,
  "category": "Vegetables",
  "isAvailable": true
}
```

**Unit Types:**
- `Kg` - Sold by kilogram
- `Piece` - Sold by piece
- `Both` - Sold by both kg and piece

### 7. Update Product
**PUT** `/api/admin/product/update/{product_id}`

**Headers:** `Authorization: Bearer <token>`

**Request Body:** (All fields optional)
```json
{
  "name": "Fresh Tomato",
  "pricePerKg": 45.0,
  "stockKg": 150.0,
  "isAvailable": false
}
```

**Note:** Set `isAvailable: false` to mark product as out of stock

### 8. Delete Product
**DELETE** `/api/admin/product/delete/{product_id}`

**Headers:** `Authorization: Bearer <token>`

### 9. Get All Orders
**GET** `/api/admin/orders`

**Headers:** `Authorization: Bearer <token>`

### 10. Update Order Status
**PUT** `/api/admin/order/status/{order_id}`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "status": "confirmed"
}
```

### 11. Assign Agent to Order
**PUT** `/api/admin/order/assign-agent/{order_id}`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "agent_id": "64abc123def456789"
}
```

### 12. Get Delivery Settings
**GET** `/api/admin/delivery-settings`

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "base_delivery_fee": 50.0,
  "price_per_km": 10.0,
  "price_per_meter": 0.01,
  "updated_at": "2024-01-15T10:30:00",
  "updated_by": "admin@veggo.com"
}
```

### 13. Update Delivery Settings
**PUT** `/api/admin/delivery-settings`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "base_delivery_fee": 60.0,
  "price_per_km": 12.0,
  "price_per_meter": 0.012,
  "updated_by": "admin@veggo.com",
  "updated_at": "2024-01-15T10:30:00"
}
```

---

## 📦 PRODUCT ENDPOINTS (Public)

### 1. Get All Products
**GET** `/api/products?category=Vegetables&available_only=true`

**Query Parameters:**
- `category`: Filter by category (optional)
- `available_only`: Show only available products (default: true)

**Response:**
```json
[
  {
    "id": "64abc123def456789",
    "name": "Tomato",
    "imageUrl": "https://example.com/tomato.jpg",
    "unitType": "Kg",
    "pricePerKg": 40.0,
    "pricePerPiece": null,
    "stockKg": 100.0,
    "stockPieces": null,
    "category": "Vegetables",
    "isAvailable": true,
    "in_stock": true
  }
]
```

### 2. Get Single Product
**GET** `/api/product/{product_id}`

### 3. Get Categories
**GET** `/api/categories`

**Response:**
```json
{
  "categories": ["Vegetables", "Fruits", "Herbs"]
}
```

---

## 📝 ORDER ENDPOINTS

### 1. Create Order
**POST** `/api/order/create`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "items": [
    {
      "product_id": "64abc123def456789",
      "product_name": "Tomato",
      "quantity": 2.5,
      "unit": "Kg",
      "price_per_unit": 40.0,
      "total_price": 100.0
    }
  ],
  "delivery_address": "123 Main St, City",
  "lat": 28.6139,
  "lng": 77.2090,
  "phone": "1234567890",
  "notes": "Please ring doorbell"
}
```

**Response:**
```json
{
  "message": "Order created successfully",
  "order_id": "64xyz789abc123456",
  "order_number": "VG20240115123456",
  "total_price": 100.0,
  "delivery_fee": 65.0,
  "final_price": 165.0,
  "distance_km": 1.5
}
```

### 2. Get Order Details
**GET** `/api/order/{order_id}`

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "id": "64xyz789abc123456",
  "order_number": "VG20240115123456",
  "user_id": "64abc123def456789",
  "items": [...],
  "total_price": 100.0,
  "delivery_fee": 65.0,
  "final_price": 165.0,
  "status": "assigned",
  "delivery_address": "123 Main St, City",
  "lat": 28.6139,
  "lng": 77.2090,
  "phone": "1234567890",
  "agent_id": "64def456ghi789012",
  "agent_name": "Mike Wilson",
  "agent_phone": "1234567890",
  "agent_location": {
    "lat": 28.6200,
    "lng": 77.2100,
    "updated_at": "2024-01-15T10:35:00"
  },
  "created_at": "2024-01-15T10:30:00",
  "can_cancel": false
}
```

### 3. Cancel Order
**PUT** `/api/order/cancel/{order_id}`

**Headers:** `Authorization: Bearer <token>`

**Note:** Can only cancel within 5 minutes of order placement and if status is `pending` or `confirmed`

---

## 📧 Email Notifications

Users automatically receive emails for:

1. **Signup** - Verification link
2. **Order Placed** - Confirmation with order details
3. **Agent Assigned** - Agent information
4. **Status Updates** - picked_up, in_transit, delivered
5. **Order Cancelled** - Cancellation confirmation
6. **Password Reset** - Reset link

Agents receive:
1. **Account Approved/Rejected** - Approval status

---

## 🗺️ Distance & Delivery Fee

### Calculation
```
Distance calculated using Google Maps Distance Matrix API
Delivery Fee = Base Fee + (Distance in KM × Price per KM)
```

### Example
```
Base Fee: ₹50
Price per KM: ₹10
Distance: 3.5 km

Delivery Fee = 50 + (3.5 × 10) = ₹85
```

Admin can update these values anytime from the admin panel.

---

## ⏱️ Order Cancellation Rules

- Orders can be cancelled within **5 minutes** of placement
- Only orders with status `pending` or `confirmed` can be cancelled
- Stock is automatically restored upon cancellation
- User receives email notification

---

## 🔐 Security

- All passwords are hashed using bcrypt
- JWT tokens expire after 7 days (configurable)
- Email verification required for users
- Admin approval required for agents
- CORS enabled for cross-origin requests

---

## 📊 Status Flow

### Order Status Flow
```
pending → confirmed → assigned → picked_up → in_transit → delivered
                                                        ↘ cancelled
```

---

## 🚀 Integration Guide

### Mobile App Integration
1. Use base URL: `https://your-api.vercel.app`
2. Store JWT token securely
3. Include token in Authorization header
4. Handle token expiration (refresh or re-login)

### Website Integration
1. Same as mobile app
2. Use CORS-enabled endpoints
3. Store token in localStorage or cookies

---

## 🆘 Error Responses

All errors follow this format:
```json
{
  "detail": "Error message here"
}
```

**Common Status Codes:**
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

---

**API Version:** 1.0.0  
**Last Updated:** February 2026
