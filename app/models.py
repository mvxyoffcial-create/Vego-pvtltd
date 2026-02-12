from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Enums
class UnitType(str, Enum):
    KG = "Kg"
    PIECE = "Piece"
    BOTH = "Both"

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    ASSIGNED = "assigned"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class VehicleType(str, Enum):
    BIKE = "bike"
    CAR = "car"

# User Models
class UserSignup(BaseModel):
    username: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    address: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class GoogleLogin(BaseModel):
    google_token: str

class UserProfileUpdate(BaseModel):
    username: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

# Agent Models
class AgentSignup(BaseModel):
    name: str
    phone: str
    email: EmailStr
    password: str
    vehicle_type: VehicleType
    license_number: Optional[str] = None

class AgentLogin(BaseModel):
    email: EmailStr
    password: str

class LocationUpdate(BaseModel):
    lat: float
    lng: float

class OrderStatusUpdate(BaseModel):
    status: OrderStatus

# Admin Models
class AdminLogin(BaseModel):
    email: EmailStr
    password: str

class ProductCreate(BaseModel):
    name: str
    imageUrl: str
    unitType: UnitType
    pricePerKg: Optional[float] = None
    pricePerPiece: Optional[float] = None
    stockKg: Optional[float] = None
    stockPieces: Optional[int] = None
    category: str
    isAvailable: bool = True

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    imageUrl: Optional[str] = None
    unitType: Optional[UnitType] = None
    pricePerKg: Optional[float] = None
    pricePerPiece: Optional[float] = None
    stockKg: Optional[float] = None
    stockPieces: Optional[int] = None
    category: Optional[str] = None
    isAvailable: Optional[bool] = None

class DeliverySettings(BaseModel):
    base_delivery_fee: float
    price_per_km: float
    price_per_meter: float
    updated_by: str
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Order Models
class OrderItem(BaseModel):
    product_id: str
    product_name: str
    quantity: float
    unit: str  # "Kg" or "Piece"
    price_per_unit: float
    total_price: float

class OrderCreate(BaseModel):
    items: List[OrderItem]
    delivery_address: str
    lat: float
    lng: float
    phone: str
    notes: Optional[str] = None

class AgentAssign(BaseModel):
    agent_id: str

# Response Models
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    verified: bool
    phone: Optional[str] = None
    address: Optional[str] = None
    created_at: datetime

class AgentResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: str
    approved: bool
    vehicle_type: str
    current_location: Optional[dict] = None

class ProductResponse(BaseModel):
    id: str
    name: str
    imageUrl: str
    unitType: str
    pricePerKg: Optional[float] = None
    pricePerPiece: Optional[float] = None
    stockKg: Optional[float] = None
    stockPieces: Optional[int] = None
    category: str
    isAvailable: bool

class OrderResponse(BaseModel):
    id: str
    order_number: str
    user_id: str
    items: List[OrderItem]
    total_price: float
    delivery_fee: float
    final_price: float
    status: str
    delivery_address: str
    lat: float
    lng: float
    phone: str
    agent_id: Optional[str] = None
    agent_location: Optional[dict] = None
    created_at: datetime
    can_cancel: bool = False
