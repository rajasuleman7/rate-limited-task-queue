
import uuid
from fastapi import APIRouter, HTTPException
from ..auth import (UserCreate, UserLogin, TokenResponse,
                    hash_pw, create_token, _users)

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(body: UserCreate):
    if body.username in _users:
        raise HTTPException(409, "Username already taken")
    if len(body.password) < 6:
        raise HTTPException(400, "Password must be at least 6 characters")
    if body.role not in ("user", "premium", "admin"):
        raise HTTPException(400, "Role must be user, premium, or admin")

    user_id = str(uuid.uuid4())
    _users[body.username] = {
        "id":       user_id,
        "username": body.username,
        "password": hash_pw(body.password),
        "role":     body.role,
    }
    token = create_token(user_id, body.username, body.role)
    return TokenResponse(access_token=token, role=body.role)


@router.post("/login", response_model=TokenResponse)
def login(body: UserLogin):
    user = _users.get(body.username)
    if not user or user["password"] != hash_pw(body.password):
        raise HTTPException(401, "Invalid credentials")
    token = create_token(user["id"], user["username"], user["role"])
    return TokenResponse(access_token=token, role=user["role"])
