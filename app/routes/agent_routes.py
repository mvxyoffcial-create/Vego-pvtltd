from fastapi import APIRouter, HTTPException, Depends, status
from app.models import AgentSignup, AgentLogin, LocationUpdate, OrderStatusUpdate, Token
from app.auth import hash_password, verify_password, create_access_token, get_current_agent
from app.database import get_agents_collection, get_orders_collection, get_users_collection
from app.email_service import email_service
from datetime import datetime
from bson import ObjectId

router = APIRouter()

@router.post("/signup", response_model=Token)
async def agent_signup(agent_data: AgentSignup):
    agents_collection = get_agents_collection()
    
    # Check if agent exists
    existing_agent = await agents_collection.find_one({"email": agent_data.email})
    if existing_agent:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    hashed_password = hash_password(agent_data.password)
    
    # Create agent
    agent_dict = {
        "name": agent_data.name,
        "phone": agent_data.phone,
        "email": agent_data.email,
        "password": hashed_password,
        "vehicle_type": agent_data.vehicle_type,
        "license_number": agent_data.license_number,
        "approved": False,  # Needs admin approval
        "current_location": None,
        "created_at": datetime.utcnow()
    }
    
    result = await agents_collection.insert_one(agent_dict)
    
    # Create access token (but agent can't use it until approved)
    access_token = create_access_token(data={"sub": agent_data.email, "type": "agent"})
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def agent_login(agent_data: AgentLogin):
    agents_collection = get_agents_collection()
    
    agent = await agents_collection.find_one({"email": agent_data.email})
    if not agent:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not verify_password(agent_data.password, agent["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not agent.get("approved", False):
        raise HTTPException(
            status_code=403,
            detail="Your account is pending admin approval. Please wait for approval."
        )
    
    access_token = create_access_token(data={"sub": agent_data.email, "type": "agent"})
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/profile")
async def get_agent_profile(current_agent: dict = Depends(get_current_agent)):
    agent = current_agent["agent"]
    return {
        "id": str(agent["_id"]),
        "name": agent["name"],
        "email": agent["email"],
        "phone": agent["phone"],
        "vehicle_type": agent["vehicle_type"],
        "license_number": agent.get("license_number"),
        "approved": agent.get("approved", False),
        "current_location": agent.get("current_location"),
        "created_at": agent["created_at"]
    }

@router.get("/orders")
async def get_agent_orders(current_agent: dict = Depends(get_current_agent)):
    """Get all orders assigned to this agent"""
    orders_collection = get_orders_collection()
    agent = current_agent["agent"]
    
    orders = await orders_collection.find(
        {"agent_id": str(agent["_id"])}
    ).sort("created_at", -1).to_list(100)
    
    for order in orders:
        order["id"] = str(order["_id"])
        order.pop("_id")
    
    return orders

@router.put("/update-location")
async def update_location(
    location_data: LocationUpdate,
    current_agent: dict = Depends(get_current_agent)
):
    """Update agent's current location for real-time tracking"""
    agents_collection = get_agents_collection()
    agent = current_agent["agent"]
    
    await agents_collection.update_one(
        {"_id": agent["_id"]},
        {"$set": {
            "current_location": {
                "lat": location_data.lat,
                "lng": location_data.lng,
                "updated_at": datetime.utcnow()
            }
        }}
    )
    
    return {"message": "Location updated successfully"}

@router.put("/order-status/{order_id}")
async def update_order_status(
    order_id: str,
    status_data: OrderStatusUpdate,
    current_agent: dict = Depends(get_current_agent)
):
    """Update order status by agent"""
    orders_collection = get_orders_collection()
    users_collection = get_users_collection()
    agent = current_agent["agent"]
    
    # Verify order belongs to this agent
    order = await orders_collection.find_one({"_id": ObjectId(order_id)})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.get("agent_id") != str(agent["_id"]):
        raise HTTPException(status_code=403, detail="This order is not assigned to you")
    
    # Update order status
    await orders_collection.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": {
            "status": status_data.status,
            "updated_at": datetime.utcnow()
        }}
    )
    
    # Send email notification to user
    user = await users_collection.find_one({"_id": ObjectId(order["user_id"])})
    if user:
        await email_service.send_order_status_email(
            user["email"],
            user["username"],
            order["order_number"],
            status_data.status
        )
    
    return {"message": "Order status updated successfully"}
