from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ...db.session import get_db
from ...db.models import User
from ...utils.password_hashing import hash_password, verify_password
from ...utils.jwt import create_access_token
from ...schemas.auth import RegisterSchema, LoginSchema
from ...db.repository import get_user_by_email
from pydantic import BaseModel
from ...utils.auth_dependency import get_current_user

router = APIRouter()

class ProfileResponse(BaseModel):
    user_id: str
    name: str
    email: str


@router.post("/auth/register")
async def register(user: RegisterSchema, db: AsyncSession = Depends(get_db)):
    existing = await get_user_by_email(db, user.email)
    if existing:
        raise HTTPException(400, "User already exists")

    hashed = hash_password(user.password)

    new_user = User(name=user.name, email=user.email, password_hash=hashed)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    token = create_access_token({"user_id": str(new_user.user_id)})

    return {"access_token": token, "token_type": "bearer"}

@router.post("/auth/login")
async def login(creds: LoginSchema, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, creds.email)

    if not user or not verify_password(creds.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")

    token = create_access_token({"user_id": str(user.user_id)})

    return {"access_token": token, "token_type": "bearer"}

@router.get("/auth/me", response_model=ProfileResponse)
async def get_me(user: User = Depends(get_current_user)):
    return ProfileResponse(
        user_id=str(user.user_id),
        name=user.name,
        email=user.email
    )
