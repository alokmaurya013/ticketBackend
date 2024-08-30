import logging
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.responses import JSONResponse
from models import UpdateProfileModel, UserLogin,UserRegister,UserInDB
from database import users_collection,get_db
from auth import create_jwt_token, verify_jwt_token,verify_password,get_password_hash

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.post("/login")
async def login_user(user: UserLogin):
    db_user = await users_collection.find_one({"email": user.email})
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid email or password")
    if not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    token = create_jwt_token(user.email)
    return {"token": token, "email": user.email}

@router.post("/register")
async def register_user(user: UserRegister):
    existing_user = await users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered please login")
    hashed_password = get_password_hash(user.password)
    user_in_db = UserInDB(
        name=user.name,
        email=user.email,
        hashed_password=hashed_password
    )
    await users_collection.insert_one(user_in_db.dict())
    return JSONResponse(status_code=201, content={"message": "User created successfully"})

@router.get("/user/profile")
async def get_user_profile(authorization: str =Header(...)):
    token = authorization.split(" ")[1] 
    logger.info("user token: %s", token)
    user_email = verify_jwt_token(token)  
    user = await users_collection.find_one({"email":user_email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "name": user["name"],
        "email": user["email"],
    }

@router.put("/user/profile/update")
async def update_user_profile(profile_data: UpdateProfileModel,authorization: str = Header(...)):
    token = authorization.split(" ")[1] 
    logger.info("user token: %s", token)
    user_email = verify_jwt_token(token)  
    user = await users_collection.find_one({"email":user_email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    update_result = await users_collection.update_one(
        {"_id": ObjectId(user["_id"])},
        {"$set": {"name": profile_data.name, "email": profile_data.email}}
    )
    if update_result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Profile updated successfully"}
