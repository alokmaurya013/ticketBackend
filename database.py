import motor.motor_asyncio

from ticket.backend.config import Config

client =motor.motor_asyncio.AsyncIOMotorClient(Config.MONGODB_URI)
db= client.ticket_system
users_collection = db.get_collection("users")
tickets_collection = db.get_collection("tickets")

def get_db():
    return db