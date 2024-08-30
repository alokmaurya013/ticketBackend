from pydantic import BaseModel,EmailStr
from typing import Optional

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    
class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
class UserInDB(BaseModel):
    name: str
    email: EmailStr
    hashed_password: str
    class Config:
        from_orm:True
        
class Ticket(BaseModel):
    title: str
    description: str
    category: str
    class Config:
        from_orm:True
        
class TicketStatusUpdate(BaseModel):
    status: str

class UpdateProfileModel(BaseModel):
    name: Optional[str]
    email:Optional[str]
    
class UpdateUserModel(BaseModel):
    name: str = None
    email: str = None

