import logging
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Header,status
from models import TicketStatusUpdate, UserInDB,Ticket,UpdateUserModel
from database import get_db,users_collection,tickets_collection
from auth import verify_jwt_token,create_jwt_token
from pymongo import ReturnDocument
router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.post("/admin/login")
def admin_login(user: UserInDB):
    if user.name == "admin" and user.password == "admin_password":
        token = create_jwt_token(user.name)
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@router.get("/admin/alltickets")
async def get_all_tickets(authorization: str = Header(...)):
    logger.info("Verifying user email from token: %s", authorization)
    token = authorization.split(" ")[1] 
    user_email = verify_jwt_token(token) 
    logger.info("Verifying user email from token: %s",token)
    user = await users_collection.find_one({"email": user_email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.get("name") != "admin": 
        raise HTTPException(status_code=403, detail="Access denied")
    db = get_db()
    tickets = await db.tickets.find().to_list(length=None)
    for ticket in tickets:
        ticket["_id"] = str(ticket["_id"])
        ticket["created_by"] = str(ticket["created_by"])
    return {"tickets": tickets}

@router.put("/admin/updatestatus/{ticket_id}")
async def update_ticket_status(ticket_id: str, status: TicketStatusUpdate, authorization: str = Header(...)):
    token = authorization.split(" ")[1] 
    user_email = verify_jwt_token(token)
    user = await users_collection.find_one({"email": user_email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    logger.info("Verifying authorization from ticket_it: %s", ticket_id)
    try:
        ticket_object_id = ObjectId(ticket_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid ticket ID format")

    updated_ticket = await tickets_collection.find_one_and_update(
        {"_id": ticket_object_id},
        {"$set": {"status": status.status}},
        return_document=ReturnDocument.AFTER
    )
    if not updated_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    updated_ticket["_id"] = str(updated_ticket["_id"])
    return {"message": "Ticket status updated", "ticket": updated_ticket}

@router.delete("/admin/cancel/{ticket_id}")
async def cancel_ticket(ticket_id: str, authorization: str = Header(...)):
    token = authorization.split(" ")[1] 
    user_email = verify_jwt_token(token)
    user = await users_collection.find_one({"email": user_email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    result = await tickets_collection.delete_one({"_id": ObjectId(ticket_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {"message": "Ticket canceled successfully"}

@router.get("/admin/userlist")
async def get_users(authorization: str = Header(...)):
    logger.info("Verifying authorization from token: %s", authorization)
    token = authorization.split(" ")[1]
    admin_email = verify_jwt_token(token)
    admin = await users_collection.find_one({"email": admin_email})
    if not admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    users = await users_collection.find().to_list(length=None)
    for user in users:
        user["_id"] = str(user["_id"])
    return {"users": users}

@router.put("/admin/updateuser/{user_id}")
async def update_user(user_id: str, user_update: UpdateUserModel, authorization: str = Header(...)):
    token = authorization.split(" ")[1]
    admin_email = verify_jwt_token(token)
    admin = await users_collection.find_one({"email": admin_email})
    if not admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    user_object_id = ObjectId(user_id)
    update_data = user_update.dict(exclude_unset=True)
    result = await users_collection.update_one({"_id": user_object_id}, {"$set": update_data})
    
    if result.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found or no changes made")
    
    return {"msg": "User updated successfully"}

@router.delete("/admin/deleteuser/{user_id}")
async def delete_user(user_id: str, authorization: str = Header(...)):
    token = authorization.split(" ")[1]
    admin_email = verify_jwt_token(token)
    admin = await users_collection.find_one({"email": admin_email})
    if not admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    user_object_id = ObjectId(user_id)
    result = await users_collection.delete_one({"_id": user_object_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")    
    return {"msg": "User deleted successfully"}
