from fastapi import APIRouter, HTTPException, Depends, status
from app.models import UserSignup, UserLogin, GoogleLogin, UserProfileUpdate, PasswordReset, Token, UserResponse
from app.auth import hash_password, verify_password, create_access_token, get_current_user
from app.database import get_users_collection, get_orders_collection
from app.email_service import email_service
from datetime import datetime
from bson import ObjectId
import secrets

router = APIRouter()

@router.post("/signup", response_model=Token)
async def signup(user_data: UserSignup):
    users_collection = get_users_collection()
    
    # Check if user exists
    existing_user = await users_collection.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    hashed_password = hash_password(user_data.password)
    
    # Generate verification token
    verification_token = secrets.token_urlsafe(32)
    
    # Create user
    user_dict = {
        "username": user_data.username,
        "email": user_data.email,
        "password": hashed_password,
        "phone": user_data.phone,
        "address": user_data.address,
        "lat": user_data.lat,
        "lng": user_data.lng,
        "verified": False,
        "verification_token": verification_token,
        "google_id": None,
        "created_at": datetime.utcnow()
    }
    
    result = await users_collection.insert_one(user_dict)
    
    # Send verification email
    await email_service.send_verification_email(
        user_data.email, 
        verification_token,
        user_data.username
    )
    
    # Create access token
    access_token = create_access_token(data={"sub": user_data.email, "type": "user"})
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    users_collection = get_users_collection()
    
    user = await users_collection.find_one({"email": user_data.email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not verify_password(user_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    access_token = create_access_token(data={"sub": user_data.email, "type": "user"})
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/verify-email")
async def verify_email(token: str):
    users_collection = get_users_collection()
    
    user = await users_collection.find_one({"verification_token": token})
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")
    
    await users_collection.update_one(
        {"_id": user["_id"]},
        {
            "$set": {"verified": True},
            "$unset": {"verification_token": ""}
        }
    )
    
    return {"message": "Email verified successfully"}

@router.post("/reset-password")
async def reset_password(data: PasswordReset):
    users_collection = get_users_collection()
    
    user = await users_collection.find_one({"email": data.email})
    if not user:
        # Don't reveal if email exists
        return {"message": "If the email exists, a reset link has been sent"}
    
    # Generate reset token
    reset_token = secrets.token_urlsafe(32)
    
    await users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {
            "reset_token": reset_token,
            "reset_token_expires": datetime.utcnow()
        }}
    )
    
    # Send reset email
    await email_service.send_password_reset_email(
        data.email,
        reset_token,
        user["username"]
    )
    
    return {"message": "If the email exists, a reset link has been sent"}

@router.get("/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    user = current_user["user"]
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "email": user["email"],
        "verified": user.get("verified", False),
        "phone": user.get("phone"),
        "address": user.get("address"),
        "lat": user.get("lat"),
        "lng": user.get("lng"),
        "created_at": user["created_at"]
    }

@router.put("/profile/update")
async def update_profile(
    profile_data: UserProfileUpdate,
    current_user: dict = Depends(get_current_user)
):
    users_collection = get_users_collection()
    user = current_user["user"]
    
    update_data = {}
    if profile_data.username:
        update_data["username"] = profile_data.username
    if profile_data.phone:
        update_data["phone"] = profile_data.phone
    if profile_data.address:
        update_data["address"] = profile_data.address
    if profile_data.lat is not None:
        update_data["lat"] = profile_data.lat
    if profile_data.lng is not None:
        update_data["lng"] = profile_data.lng
    
    if update_data:
        await users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": update_data}
        )
    
    return {"message": "Profile updated successfully"}

@router.get("/orders")
async def get_user_orders(current_user: dict = Depends(get_current_user)):
    """Get all orders including past deliveries"""
    orders_collection = get_orders_collection()
    user = current_user["user"]
    
    orders = await orders_collection.find(
        {"user_id": str(user["_id"])}
    ).sort("created_at", -1).to_list(100)
    
    # Calculate if order can be cancelled
    for order in orders:
        order["id"] = str(order["_id"])
        order.pop("_id")
        
        # Check if order can be cancelled (within 5 minutes and status is pending/confirmed)
        can_cancel = False
        if order["status"] in ["pending", "confirmed"]:
            time_diff = datetime.utcnow() - order["created_at"]
            if time_diff.total_seconds() <= 300:  # 5 minutes
                can_cancel = True
        order["can_cancel"] = can_cancel
        
        # Format agent location if exists
        if order.get("agent_id"):
            from app.database import get_agents_collection
            agents_collection = get_agents_collection()
            agent = await agents_collection.find_one({"_id": ObjectId(order["agent_id"])})
            if agent and agent.get("current_location"):
                order["agent_location"] = agent["current_location"]
                order["agent_name"] = agent.get("name")
    
    return orders

@router.post("/google-login", response_model=Token)
async def google_login(data: GoogleLogin):
    # TODO: Implement Google OAuth verification
    # This is a placeholder - you need to verify the google_token
    raise HTTPException(status_code=501, detail="Google login not implemented yet")
