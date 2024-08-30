import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException,Header
from models import Ticket, TicketStatusUpdate
from database import get_db,tickets_collection,users_collection
from auth import verify_jwt_token

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.post("/tickets")
async def submit_ticket(ticket: Ticket,  authorization: str = Header(...)):
    token = authorization.split(" ")[1]  # Expecting 'Bearer <token>'
    user_email = verify_jwt_token(token)  # Decode the token to get the user's email

    logger.info("Verifying user email from token: %s", user_email)
    user = await users_collection.find_one({"email": user_email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    new_ticket = {
        "title": ticket.title,
        "description": ticket.description,
        "category": ticket.category,
        "created_by":str(user["_id"]), 
        "status": "open",
        "created_at":datetime.now(timezone.utc)
    }
    result = await tickets_collection.insert_one(new_ticket)
    if result.inserted_id:
        return {"message": "Ticket submitted successfully", "ticket_id": str(result.inserted_id)}
    else:
        raise HTTPException(status_code=500, detail="Ticket submission failed")
    

@router.get("/usertickets")
async def get_tickets(authorization: str = Header(...)):
    logger.info("authorization token: %s",authorization)
    token = authorization.split(" ")[1] 
    logger.info("user token: %s", token)
    user_email = verify_jwt_token(token)  
    logger.info("Verifying user email from token: %s", user_email)
    user = await users_collection.find_one({"email": user_email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db = get_db()
    tickets = []
    async for ticket in db.tickets.find({"created_by": str(user["_id"])}):
        ticket["_id"] = str(ticket["_id"]) 
        tickets.append(ticket) 
    return {"tickets": tickets}

@router.put("/tickets/{ticket_id}")
def update_ticket(ticket_id: str, status_update: TicketStatusUpdate, token: str = Depends(verify_jwt_token)):
    db = get_db()
    result = db.tickets.update_one({"_id": ticket_id, "user": token}, {"$set": status_update.dict()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Ticket not found or unauthorized")
    return {"msg": "Ticket updated successfully"}
