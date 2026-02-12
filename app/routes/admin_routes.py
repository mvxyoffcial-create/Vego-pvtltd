from fastapi import APIRouter, HTTPException, Depends, status
from app.models import (AdminLogin, ProductCreate, ProductUpdate, DeliverySettings, 
                        AgentAssign, OrderStatusUpdate, Token)
from app.auth import hash_password, verify_password, create_access_token, get_current_admin
from app.database import (get_admins_collection, get_users_collection, get_agents_collection,
                          get_products_collection, get_orders_collection, get_delivery_settings_collection)
from app.email_service import email_service
from datetime import datetime
from bson import ObjectId
from app.config import settings

router = APIRouter()

@router.post("/login", response_model=Token)
async def admin_login(admin_data: AdminLogin):
    admins_collection = get_admins_collection()
    
    admin = await admins_collection.find_one({"email": admin_data.email})
    if not admin:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not verify_password(admin_data.password, admin["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    access_token = create_access_token(data={"sub": admin_data.email, "type": "admin"})
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/dashboard")
async def get_dashboard(current_admin: dict = Depends(get_current_admin)):
    """Get admin dashboard statistics"""
    users_collection = get_users_collection()
    agents_collection = get_agents_collection()
    products_collection = get_products_collection()
    orders_collection = get_orders_collection()
    
    total_users = await users_collection.count_documents({})
    total_agents = await agents_collection.count_documents({"approved": True})
    pending_agents = await agents_collection.count_documents({"approved": False})
    total_products = await products_collection.count_documents({})
    total_orders = await orders_collection.count_documents({})
    pending_orders = await orders_collection.count_documents({"status": "pending"})
    
    return {
        "total_users": total_users,
        "total_agents": total_agents,
        "pending_agents": pending_agents,
        "total_products": total_products,
        "total_orders": total_orders,
        "pending_orders": pending_orders
    }

@router.get("/users")
async def get_all_users(current_admin: dict = Depends(get_current_admin)):
    """Get all users"""
    users_collection = get_users_collection()
    
    users = await users_collection.find({}).to_list(1000)
    
    for user in users:
        user["id"] = str(user["_id"])
        user.pop("_id")
        user.pop("password", None)
    
    return users

@router.get("/agents")
async def get_all_agents(current_admin: dict = Depends(get_current_admin)):
    """Get all agents"""
    agents_collection = get_agents_collection()
    
    agents = await agents_collection.find({}).to_list(1000)
    
    for agent in agents:
        agent["id"] = str(agent["_id"])
        agent.pop("_id")
        agent.pop("password", None)
    
    return agents

@router.put("/agent/approve/{agent_id}")
async def approve_agent(
    agent_id: str,
    approve: bool,
    current_admin: dict = Depends(get_current_admin)
):
    """Approve or reject agent"""
    agents_collection = get_agents_collection()
    
    agent = await agents_collection.find_one({"_id": ObjectId(agent_id)})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    await agents_collection.update_one(
        {"_id": ObjectId(agent_id)},
        {"$set": {"approved": approve, "updated_at": datetime.utcnow()}}
    )
    
    # Send email notification
    await email_service.send_agent_approval_email(
        agent["email"],
        agent["name"],
        approve
    )
    
    return {"message": f"Agent {'approved' if approve else 'rejected'} successfully"}

@router.post("/product/add")
async def add_product(
    product_data: ProductCreate,
    current_admin: dict = Depends(get_current_admin)
):
    """Add new product"""
    products_collection = get_products_collection()
    
    product_dict = {
        "name": product_data.name,
        "imageUrl": product_data.imageUrl,
        "unitType": product_data.unitType,
        "pricePerKg": product_data.pricePerKg,
        "pricePerPiece": product_data.pricePerPiece,
        "stockKg": product_data.stockKg,
        "stockPieces": product_data.stockPieces,
        "category": product_data.category,
        "isAvailable": product_data.isAvailable,
        "created_at": datetime.utcnow()
    }
    
    result = await products_collection.insert_one(product_dict)
    
    return {"message": "Product added successfully", "product_id": str(result.inserted_id)}

@router.put("/product/update/{product_id}")
async def update_product(
    product_id: str,
    product_data: ProductUpdate,
    current_admin: dict = Depends(get_current_admin)
):
    """Update product"""
    products_collection = get_products_collection()
    
    product = await products_collection.find_one({"_id": ObjectId(product_id)})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = {}
    if product_data.name is not None:
        update_data["name"] = product_data.name
    if product_data.imageUrl is not None:
        update_data["imageUrl"] = product_data.imageUrl
    if product_data.unitType is not None:
        update_data["unitType"] = product_data.unitType
    if product_data.pricePerKg is not None:
        update_data["pricePerKg"] = product_data.pricePerKg
    if product_data.pricePerPiece is not None:
        update_data["pricePerPiece"] = product_data.pricePerPiece
    if product_data.stockKg is not None:
        update_data["stockKg"] = product_data.stockKg
    if product_data.stockPieces is not None:
        update_data["stockPieces"] = product_data.stockPieces
    if product_data.category is not None:
        update_data["category"] = product_data.category
    if product_data.isAvailable is not None:
        update_data["isAvailable"] = product_data.isAvailable
    
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        await products_collection.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": update_data}
        )
    
    return {"message": "Product updated successfully"}

@router.delete("/product/delete/{product_id}")
async def delete_product(
    product_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """Delete product"""
    products_collection = get_products_collection()
    
    result = await products_collection.delete_one({"_id": ObjectId(product_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {"message": "Product deleted successfully"}

@router.get("/orders")
async def get_all_orders(current_admin: dict = Depends(get_current_admin)):
    """Get all orders"""
    orders_collection = get_orders_collection()
    
    orders = await orders_collection.find({}).sort("created_at", -1).to_list(1000)
    
    for order in orders:
        order["id"] = str(order["_id"])
        order.pop("_id")
    
    return orders

@router.put("/order/status/{order_id}")
async def update_order_status(
    order_id: str,
    status_data: OrderStatusUpdate,
    current_admin: dict = Depends(get_current_admin)
):
    """Update order status"""
    orders_collection = get_orders_collection()
    users_collection = get_users_collection()
    
    order = await orders_collection.find_one({"_id": ObjectId(order_id)})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    await orders_collection.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": {
            "status": status_data.status,
            "updated_at": datetime.utcnow()
        }}
    )
    
    # Send email notification
    user = await users_collection.find_one({"_id": ObjectId(order["user_id"])})
    if user:
        await email_service.send_order_status_email(
            user["email"],
            user["username"],
            order["order_number"],
            status_data.status
        )
    
    return {"message": "Order status updated successfully"}

@router.put("/order/assign-agent/{order_id}")
async def assign_agent_to_order(
    order_id: str,
    agent_data: AgentAssign,
    current_admin: dict = Depends(get_current_admin)
):
    """Assign agent to order"""
    orders_collection = get_orders_collection()
    agents_collection = get_agents_collection()
    users_collection = get_users_collection()
    
    # Verify order exists
    order = await orders_collection.find_one({"_id": ObjectId(order_id)})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Verify agent exists and is approved
    agent = await agents_collection.find_one({"_id": ObjectId(agent_data.agent_id)})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    if not agent.get("approved", False):
        raise HTTPException(status_code=400, detail="Agent is not approved")
    
    # Assign agent
    await orders_collection.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": {
            "agent_id": agent_data.agent_id,
            "status": "assigned",
            "updated_at": datetime.utcnow()
        }}
    )
    
    # Send email notification to user
    user = await users_collection.find_one({"_id": ObjectId(order["user_id"])})
    if user:
        await email_service.send_order_assigned_email(
            user["email"],
            user["username"],
            order["order_number"],
            agent["name"]
        )
    
    return {"message": "Agent assigned successfully"}

@router.get("/delivery-settings")
async def get_delivery_settings(current_admin: dict = Depends(get_current_admin)):
    """Get current delivery fee settings"""
    settings_collection = get_delivery_settings_collection()
    
    settings_doc = await settings_collection.find_one({}, sort=[("updated_at", -1)])
    
    if not settings_doc:
        # Return default settings
        return {
            "base_delivery_fee": settings.BASE_DELIVERY_FEE,
            "price_per_km": settings.PRICE_PER_KM,
            "price_per_meter": settings.PRICE_PER_METER
        }
    
    return {
        "base_delivery_fee": settings_doc["base_delivery_fee"],
        "price_per_km": settings_doc["price_per_km"],
        "price_per_meter": settings_doc["price_per_meter"],
        "updated_at": settings_doc["updated_at"],
        "updated_by": settings_doc["updated_by"]
    }

@router.put("/delivery-settings")
async def update_delivery_settings(
    delivery_settings: DeliverySettings,
    current_admin: dict = Depends(get_current_admin)
):
    """Update delivery fee settings"""
    settings_collection = get_delivery_settings_collection()
    admin = current_admin["admin"]
    
    settings_dict = {
        "base_delivery_fee": delivery_settings.base_delivery_fee,
        "price_per_km": delivery_settings.price_per_km,
        "price_per_meter": delivery_settings.price_per_meter,
        "updated_by": admin["email"],
        "updated_at": datetime.utcnow()
    }
    
    await settings_collection.insert_one(settings_dict)
    
    # Update app settings for current session
    settings.BASE_DELIVERY_FEE = delivery_settings.base_delivery_fee
    settings.PRICE_PER_KM = delivery_settings.price_per_km
    settings.PRICE_PER_METER = delivery_settings.price_per_meter
    
    return {"message": "Delivery settings updated successfully"}
