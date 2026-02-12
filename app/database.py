from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

client: AsyncIOMotorClient = None
database = None

async def connect_db():
    global client, database
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    database = client[settings.DATABASE_NAME]
    print(f"✅ Connected to MongoDB: {settings.DATABASE_NAME}")

async def close_db():
    global client
    if client:
        client.close()
        print("❌ Disconnected from MongoDB")

def get_database():
    return database

# Collections
def get_users_collection():
    return database.users

def get_admins_collection():
    return database.admins

def get_agents_collection():
    return database.agents

def get_products_collection():
    return database.products

def get_orders_collection():
    return database.orders

def get_delivery_settings_collection():
    return database.delivery_settings
