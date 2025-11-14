from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from resentry.api.deps import get_db_session
from resentry.database.models.user import User as UserModel
from resentry.database.schemas.user import User as UserSchema, UserCreate, UserUpdate

users_router = APIRouter()


@users_router.get("/", response_model=List[UserSchema])
def get_users(db: Session = Depends(get_db_session)):
    users = db.exec(select(UserModel)).all()
    return users


@users_router.post("/", response_model=UserSchema)
def create_user(user: UserCreate, db: Session = Depends(get_db_session)):
    db_user = UserModel(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@users_router.get("/{user_id}", response_model=UserSchema)
def get_user(user_id: int, db: Session = Depends(get_db_session)):
    user = db.exec(select(UserModel).where(UserModel.id == user_id)).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@users_router.put("/{user_id}", response_model=UserSchema)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db_session)):
    db_user = db.exec(select(UserModel).where(UserModel.id == user_id)).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    for key, value in user.model_dump().items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user


@users_router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db_session)):
    db_user = db.exec(select(UserModel).where(UserModel.id == user_id)).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}
