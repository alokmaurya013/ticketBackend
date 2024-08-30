import logging # type: ignore
from jose import JWTError, jwt 
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from passlib.context import CryptContext

SECRET_KEY = "abcdefg"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_jwt_token(email: str):
    expiration = datetime.utcnow() + timedelta(hours=1)
    return jwt.encode({"sub":email, "exp": expiration}, SECRET_KEY, algorithm=ALGORITHM)

def verify_jwt_token(token: str):
    logger.info("before try user token:%s", token)
    try:
        logger.info("try user token: %s", token)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.info("Verifying user email from token: %s", payload["sub"])
        return payload["sub"]
    except JWTError as e:
        logger.error("JWT Error: %s", str(e))
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)
