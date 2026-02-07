from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy import select

from app.core.security import create_access_token, verify_password
from app.db import DBConnection, get_db
from app.models.users import users

router = APIRouter()

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/login/access-token", response_model=Token)
async def login_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[DBConnection, Depends(get_db)],
) -> Token:
    """OAuth2 compatible token login, get an access token for future requests."""
    try:
        # Fetch user by email
        stmt = select(users).where(users.c.email == form_data.username)
        result = await db.execute(stmt)
        user = result.mappings().one_or_none()
        
        if not user:
            raise HTTPException(status_code=400, detail="Incorrect email or password")
            
        if not verify_password(form_data.password, user["hashed_password"]):
            raise HTTPException(status_code=400, detail="Incorrect email or password")
            
        return Token(
            access_token=create_access_token(
                data={"user_id": str(user["id"]), "email": user["email"], "role": user["role"]}
            ),
            token_type="bearer",
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        with open("auth_error.log", "w") as f:
            traceback.print_exc(file=f)
        raise HTTPException(status_code=500, detail=str(e))
