from fastapi import APIRouter, HTTPException
from app.database import get_products_collection
from bson import ObjectId

router = APIRouter()

@router.get("/products")
async def get_all_products(category: str = None, available_only: bool = True):
    """Get all products (public endpoint)"""
    products_collection = get_products_collection()
    
    query = {}
    if category:
        query["category"] = category
    if available_only:
        query["isAvailable"] = True
    
    products = await products_collection.find(query).to_list(1000)
    
    for product in products:
        product["id"] = str(product["_id"])
        product.pop("_id")
        
        # Add stock status
        if product["unitType"] == "Kg":
            product["in_stock"] = product.get("stockKg", 0) > 0
        elif product["unitType"] == "Piece":
            product["in_stock"] = product.get("stockPieces", 0) > 0
        else:  # Both
            product["in_stock"] = (product.get("stockKg", 0) > 0 or 
                                  product.get("stockPieces", 0) > 0)
    
    return products

@router.get("/product/{product_id}")
async def get_product(product_id: str):
    """Get single product by ID"""
    products_collection = get_products_collection()
    
    product = await products_collection.find_one({"_id": ObjectId(product_id)})
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product["id"] = str(product["_id"])
    product.pop("_id")
    
    # Add stock status
    if product["unitType"] == "Kg":
        product["in_stock"] = product.get("stockKg", 0) > 0
    elif product["unitType"] == "Piece":
        product["in_stock"] = product.get("stockPieces", 0) > 0
    else:  # Both
        product["in_stock"] = (product.get("stockKg", 0) > 0 or 
                              product.get("stockPieces", 0) > 0)
    
    return product

@router.get("/categories")
async def get_categories():
    """Get all product categories"""
    products_collection = get_products_collection()
    
    categories = await products_collection.distinct("category")
    
    return {"categories": categories}
