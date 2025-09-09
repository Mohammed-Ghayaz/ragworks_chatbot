
from auth import ACCESS_TOKEN_EXPIRY, UserRegistration, UserLogin, Token, create_access_token, hash_password, secret_hash_key, verify_password
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from datetime import timedelta
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from database import SessionLocal, User, Conversation, create_db, get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_user_from_db(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def save_user_to_db(db: Session, user: UserRegistration):
    new_user = User(username=user.username, password=hash_password(user.password), email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, secret_hash_key, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    db_user = get_user_from_db(db, username)
    if db_user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    return db_user

def register_user(user: UserRegistration, db: Session = Depends(get_db)):
    db_user = get_user_from_db(db, user.username)

    if db_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    new_user = save_user_to_db(db, user)
    
    access_token = create_access_token(data={"sub": new_user.username}, expiry_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRY))
    return {"access_token": access_token, "token_type": "bearer"}

def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = get_user_from_db(db, user.username)

    if not db_user:
        raise HTTPException(status_code=400, detail="User not found")
    
    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid password")

    access_token = create_access_token(data={"sub": db_user.username}, expiry_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRY))
    return {"access_token": access_token, "token_type": "bearer"}