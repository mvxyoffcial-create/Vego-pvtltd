"""
Database Initialization Script
Run this once to create the default admin account and set up indexes
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from app.auth import hash_password
from datetime import datetime

async def init_database():
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.DATABASE_NAME]
    
    print("🚀 Initializing VegGo Database...")
    
    # Create default admin
    admins_collection = db.admins
    existing_admin = await admins_collection.find_one({"email": "admin@veggo.com"})
    
    if not existing_admin:
        admin_data = {
            "name": "Admin",
            "email": "admin@veggo.com",
            "password": hash_password("admin123"),  # Change this password!
            "role": "super_admin",
            "created_at": datetime.utcnow()
        }
        await admins_collection.insert_one(admin_data)
        print("✅ Default admin created: admin@veggo.com / admin123")
    else:
        print("ℹ️  Admin already exists")
    
    # Create indexes
    print("📑 Creating indexes...")
    
    # Users
    await db.users.create_index("email", unique=True)
    await db.users.create_index("username")
    
    # Agents
    await db.agents.create_index("email", unique=True)
    await db.agents.create_index("approved")
    
    # Products
    await db.products.create_index("category")
    await db.products.create_index("isAvailable")
    
    # Orders
    await db.orders.create_index("user_id")
    await db.orders.create_index("agent_id")
    await db.orders.create_index("status")
    await db.orders.create_index("order_number", unique=True)
    await db.orders.create_index("created_at")
    
    print("✅ Indexes created")
    
    # Insert sample products (optional)
    products_collection = db.products
    existing_products = await products_collection.count_documents({})
    
    if existing_products == 0:
        sample_products = [
            {
                "name": "Tomato",
                "imageUrl": "https://example.com/tomato.jpg",
                "unitType": "Kg",
                "pricePerKg": 40.0,
                "pricePerPiece": None,
                "stockKg": 100.0,
                "stockPieces": None,
                "category": "Vegetables",
                "isAvailable": True,
                "created_at": datetime.utcnow()
            },
            {
                "name": "Onion",
                "imageUrl": "https://example.com/onion.jpg",
                "unitType": "Kg",
                "pricePerKg": 30.0,
                "pricePerPiece": None,
                "stockKg": 150.0,
                "stockPieces": None,
                "category": "Vegetables",
                "isAvailable": True,
                "created_at": datetime.utcnow()
            },
            {
                "name": "Potato",
                "imageUrl": "https://example.com/potato.jpg",
                "unitType": "Kg",
                "pricePerKg": 25.0,
                "pricePerPiece": None,
                "stockKg": 200.0,
                "stockPieces": None,
                "category": "Vegetables",
                "isAvailable": True,
                "created_at": datetime.utcnow()
            },
            {
                "name": "Carrot",
                "imageUrl": "https://example.com/carrot.jpg",
                "unitType": "Both",
                "pricePerKg": 50.0,
                "pricePerPiece": 5.0,
                "stockKg": 80.0,
                "stockPieces": 500,
                "category": "Vegetables",
                "isAvailable": True,
                "created_at": datetime.utcnow()
            },
            {
                "name": "Cabbage",
                "imageUrl": "https://example.com/cabbage.jpg",
                "unitType": "Piece",
                "pricePerKg": None,
                "pricePerPiece": 30.0,
                "stockKg": None,
                "stockPieces": 50,
                "category": "Vegetables",
                "isAvailable": True,
                "created_at": datetime.utcnow()
            }
        ]
        
        await products_collection.insert_many(sample_products)
        print("✅ Sample products added")
    else:
        print("ℹ️  Products already exist")
    
    # Initialize delivery settings
    settings_collection = db.delivery_settings
    existing_settings = await settings_collection.find_one({})
    
    if not existing_settings:
        default_settings = {
            "base_delivery_fee": 50.0,
            "price_per_km": 10.0,
            "price_per_meter": 0.01,
            "updated_by": "system",
            "updated_at": datetime.utcnow()
        }
        await settings_collection.insert_one(default_settings)
        print("✅ Default delivery settings initialized")
    else:
        print("ℹ️  Delivery settings already exist")
    
    client.close()
    print("\n✨ Database initialization complete!")
    print("\n📋 Default Credentials:")
    print("   Admin Email: admin@veggo.com")
    print("   Admin Password: admin123")
    print("\n⚠️  Please change the admin password after first login!\n")

if __name__ == "__main__":
    asyncio.run(init_database())
