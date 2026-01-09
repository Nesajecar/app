from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.schemas.user import User as UserSchema, UserUpdate
from app.api.deps import get_current_user, get_current_active_user

router = APIRouter()

@router.get("/me", response_model=UserSchema)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Dobavlja informacije o trenutnom korisniku"""
    return current_user

@router.patch("/users/me", response_model=UserSchema)
def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Ažuriranje profila trenutnog korisnika"""
    update_data = user_update.dict(exclude_unset=True)
    
    # Check if email is being changed and if it's already taken
    if "email" in update_data:
        existing_user = db.query(User).filter(
            User.email == update_data["email"],
            User.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user

@router.delete("/users/me")
def delete_current_user(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Brisanje ličnog naloga"""
    # Soft delete - deactivate account
    current_user.is_active = False
    db.commit()
    
    return {"message": "Account deleted successfully"}
