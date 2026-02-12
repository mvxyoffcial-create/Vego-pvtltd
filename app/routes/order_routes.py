from fastapi import APIRouter, HTTPException, Depends
from app.models import OrderCreate, OrderItem
from app.auth import get_current_user
from app.database import (get_orders_collection, get_products_collection, 
                          get_users_collection, get_delivery_settings_collection)
from app.maps_service import maps_service
from app.email_service import email_service
from datetime import datetime, timedelta
from bson import ObjectId
import random
import string
from app.config import settings

router = APIRouter()

def generate_order_number():
    """Generate unique order number"""
    timestamp = datetime.utcnow().strftime("%Y%m%d")
    random_part = ''.join(random.choices(string.digits, k=6))
    return f"VG{timestamp}{random_part}"

async def get_delivery_fee_settings():
    """Get current delivery fee settings from database or config"""
    settings_collection = get_delivery_settings_collection()
    settings_doc = await settings_collection.find_one({}, sort=[("updated_at", -1)])
    
    if settings_doc:
        return {
            "base_fee": settings_doc["base_delivery_fee"],
            "per_km": settings_doc["price_per_km"],
            "per_meter": settings_doc["price_per_meter"]
        }
    
    return {
        "base_fee": settings.BASE_DELIVERY_FEE,
        "per_km": settings.PRICE_PER_KM,
        "per_meter": settings.PRICE_PER_METER
    }

@router.post("/order/create")
async def create_order(
    order_data: OrderCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create new order with automatic delivery fee calculation"""
    orders_collection = get_orders_collection()
    products_collection = get_products_collection()
    user = current_user["user"]
    
    # Validate and calculate order total
    total_price = 0
    validated_items = []
    
    for item in order_data.items:
        product = await products_collection.find_one({"_id": ObjectId(item.product_id)})
        
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        
        if not product.get("isAvailable", False):
            raise HTTPException(status_code=400, detail=f"Product {product['name']} is not available")
        
        # Check stock
        if item.unit == "Kg":
            if product.get("stockKg", 0) < item.quantity:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Insufficient stock for {product['name']}. Available: {product.get('stockKg', 0)} Kg"
                )
            price_per_unit = product.get("pricePerKg")
            if price_per_unit is None:
                raise HTTPException(status_code=400, detail=f"Product {product['name']} not available in Kg")
        elif item.unit == "Piece":
            if product.get("stockPieces", 0) < item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock for {product['name']}. Available: {product.get('stockPieces', 0)} Pieces"
                )
            price_per_unit = product.get("pricePerPiece")
            if price_per_unit is None:
                raise HTTPException(status_code=400, detail=f"Product {product['name']} not available in Pieces")
        else:
            raise HTTPException(status_code=400, detail="Unit must be 'Kg' or 'Piece'")
        
        item_total = price_per_unit * item.quantity
        total_price += item_total
        
        validated_items.append({
            "product_id": item.product_id,
            "product_name": product["name"],
            "quantity": item.quantity,
            "unit": item.unit,
            "price_per_unit": price_per_unit,
            "total_price": item_total
        })
    
    # Calculate delivery fee based on distance
    # Assume store location (you should set this in your database or config)
    store_lat = 28.6139  # Example: Delhi
    store_lng = 77.2090
    
    distance_km, distance_meters = maps_service.calculate_distance(
        store_lat, store_lng,
        order_data.lat, order_data.lng
    )
    
    # Get delivery fee settings
    fee_settings = await get_delivery_fee_settings()
    
    # Calculate delivery fee
    delivery_fee = fee_settings["base_fee"] + (distance_km * fee_settings["per_km"])
    final_price = total_price + delivery_fee
    
    # Generate order number
    order_number = generate_order_number()
    
    # Create order
    order_dict = {
        "order_number": order_number,
        "user_id": str(user["_id"]),
        "items": validated_items,
        "total_price": round(total_price, 2),
        "delivery_fee": round(delivery_fee, 2),
        "distance_km": round(distance_km, 2),
        "final_price": round(final_price, 2),
        "status": "pending",
        "delivery_address": order_data.delivery_address,
        "lat": order_data.lat,
        "lng": order_data.lng,
        "phone": order_data.phone,
        "notes": order_data.notes,
        "agent_id": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await orders_collection.insert_one(order_dict)
    
    # Update product stock
    for item in order_data.items:
        if item.unit == "Kg":
            await products_collection.update_one(
                {"_id": ObjectId(item.product_id)},
                {"$inc": {"stockKg": -item.quantity}}
            )
        else:  # Piece
            await products_collection.update_one(
                {"_id": ObjectId(item.product_id)},
                {"$inc": {"stockPieces": -item.quantity}}
            )
    
    # Send confirmation email
    await email_service.send_order_confirmation_email(
        user["email"],
        user["username"],
        order_number,
        final_price
    )
    
    return {
        "message": "Order created successfully",
        "order_id": str(result.inserted_id),
        "order_number": order_number,
        "total_price": total_price,
        "delivery_fee": delivery_fee,
        "final_price": final_price,
        "distance_km": distance_km
    }

@router.get("/order/{order_id}")
async def get_order(
    order_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get order details with real-time agent location"""
    orders_collection = get_orders_collection()
    user = current_user["user"]
    
    order = await orders_collection.find_one({"_id": ObjectId(order_id)})
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Verify order belongs to user
    if order["user_id"] != str(user["_id"]):
        raise HTTPException(status_code=403, detail="Not authorized to view this order")
    
    order["id"] = str(order["_id"])
    order.pop("_id")
    
    # Get agent location if assigned
    if order.get("agent_id"):
        from app.database import get_agents_collection
        agents_collection = get_agents_collection()
        agent = await agents_collection.find_one({"_id": ObjectId(order["agent_id"])})
        if agent and agent.get("current_location"):
            order["agent_location"] = agent["current_location"]
            order["agent_name"] = agent.get("name")
            order["agent_phone"] = agent.get("phone")
    
    # Check if order can be cancelled
    can_cancel = False
    if order["status"] in ["pending", "confirmed"]:
        time_diff = datetime.utcnow() - order["created_at"]
        if time_diff.total_seconds() <= (settings.ORDER_CANCEL_TIME_MINUTES * 60):
            can_cancel = True
    order["can_cancel"] = can_cancel
    
    return order

@router.put("/order/cancel/{order_id}")
async def cancel_order(
    order_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Cancel order within 5 minutes of placement"""
    orders_collection = get_orders_collection()
    products_collection = get_products_collection()
    user = current_user["user"]
    
    order = await orders_collection.find_one({"_id": ObjectId(order_id)})
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Verify order belongs to user
    if order["user_id"] != str(user["_id"]):
        raise HTTPException(status_code=403, detail="Not authorized to cancel this order")
    
    # Check if order can be cancelled
    if order["status"] not in ["pending", "confirmed"]:
        raise HTTPException(
            status_code=400,
            detail="Order cannot be cancelled at this stage"
        )
    
    # Check time limit (5 minutes)
    time_diff = datetime.utcnow() - order["created_at"]
    if time_diff.total_seconds() > (settings.ORDER_CANCEL_TIME_MINUTES * 60):
        raise HTTPException(
            status_code=400,
            detail=f"Orders can only be cancelled within {settings.ORDER_CANCEL_TIME_MINUTES} minutes of placement"
        )
    
    # Update order status
    await orders_collection.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": {
            "status": "cancelled",
            "cancelled_at": datetime.utcnow(),
            "cancelled_by": "user"
        }}
    )
    
    # Restore product stock
    for item in order["items"]:
        if item["unit"] == "Kg":
            await products_collection.update_one(
                {"_id": ObjectId(item["product_id"])},
                {"$inc": {"stockKg": item["quantity"]}}
            )
        else:  # Piece
            await products_collection.update_one(
                {"_id": ObjectId(item["product_id"])},
                {"$inc": {"stockPieces": item["quantity"]}}
            )
    
    # Send cancellation email
    await email_service.send_order_cancelled_email(
        user["email"],
        user["username"],
        order["order_number"],
        "Cancelled by user"
    )
    
    return {"message": "Order cancelled successfully"}

@router.get("/user/orders")
async def get_user_orders_list(current_user: dict = Depends(get_current_user)):
    """Get all user orders (duplicate of user_routes endpoint for convenience)"""
    orders_collection = get_orders_collection()
    user = current_user["user"]
    
    orders = await orders_collection.find(
        {"user_id": str(user["_id"])}
    ).sort("created_at", -1).to_list(100)
    
    for order in orders:
        order["id"] = str(order["_id"])
        order.pop("_id")
        
        # Check if order can be cancelled
        can_cancel = False
        if order["status"] in ["pending", "confirmed"]:
            time_diff = datetime.utcnow() - order["created_at"]
            if time_diff.total_seconds() <= (settings.ORDER_CANCEL_TIME_MINUTES * 60):
                can_cancel = True
        order["can_cancel"] = can_cancel
    
    return orders
