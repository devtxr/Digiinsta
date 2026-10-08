from datetime import datetime, timezone
from bson import ObjectId
from .db import get_db

def products(active_only=False):
    q = {"active": True} if active_only else {}
    return list(get_db().products.find(q).sort("created_at", -1))

def product(pid):
    try: oid = ObjectId(pid)
    except Exception: return None
    return get_db().products.find_one({"_id": oid})

def add_product(name, description, price, file_url, image_url=""):
    doc = {"name": name, "description": description, "price": float(price), "file_url": file_url,
           "image_url": image_url, "active": True, "created_at": datetime.now(timezone.utc)}
    return str(get_db().products.insert_one(doc).inserted_id)

def toggle_product(pid):
    p = product(pid)
    if not p: return False
    get_db().products.update_one({"_id": p["_id"]}, {"$set": {"active": not p.get("active", True)}})
    return True

def create_order(instagram_user_id, pid):
    p = product(pid)
    if not p or not p.get("active"): return None
    order = {"order_id": "ORD" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f"),
             "instagram_user_id": str(instagram_user_id), "product_id": p["_id"],
             "product_name": p["name"], "amount": p["price"], "payment_status": "pending",
             "delivery_status": "pending", "created_at": datetime.now(timezone.utc)}
    return get_db().orders.insert_one(order).inserted_id
