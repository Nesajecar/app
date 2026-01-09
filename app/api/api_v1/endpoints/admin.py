from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import os

from app.db.database import get_db
from app.db.models import Dog, User, DogStatus, DogImage
from app.schemas.dog import Dog as DogSchema
from app.schemas.user import User as UserSchema
from app.api.deps import get_admin_user
from app.api.api_v1.utils import convert_dog_to_schema

router = APIRouter()

@router.get("/dogs/pending", response_model=List[DogSchema])
def get_pending_dogs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Lista pasa koji čekaju potvrdu spašavanja"""
    pending_dogs = db.query(Dog).filter(
        Dog.status == DogStatus.PENDING_ADMIN
    ).order_by(Dog.created_at.desc()).all()
    
    # Konvertuj svaki dog u schema format
    return [convert_dog_to_schema(dog) for dog in pending_dogs]

@router.post("/dogs/{id}/confirm", response_model=DogSchema)
def confirm_dog_rescue(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Admin potvrđuje da je pas zaista spašen → status confirmed"""
    dog = db.query(Dog).filter(Dog.id == id).first()
    if not dog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dog not found"
        )
    
    if dog.status != DogStatus.PENDING_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dog is not in pending confirmation status"
        )
    
    # Update status
    dog.status = DogStatus.CONFIRMED
    dog.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(dog)
    
    # Učitaj relationships
    if dog.reporter_id:
        dog.reporter = db.query(User).filter(User.id == dog.reporter_id).first()
    if dog.picked_up_by_user_id:
        dog.picked_up_by = db.query(User).filter(User.id == dog.picked_up_by_user_id).first()
    
    return convert_dog_to_schema(dog)

@router.post("/dogs/{id}/reject", response_model=DogSchema)
def reject_dog_rescue(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Admin odbija spašavanje → vraća psa u reported"""
    dog = db.query(Dog).filter(Dog.id == id).first()
    if not dog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dog not found"
        )
    
    if dog.status != DogStatus.PENDING_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dog is not in pending confirmation status"
        )
    
    # Reset to reported status
    dog.status = DogStatus.REPORTED
    dog.picked_up_by_user_id = None
    dog.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(dog)
    
    # Učitaj relationships
    if dog.reporter_id:
        dog.reporter = db.query(User).filter(User.id == dog.reporter_id).first()
    if dog.picked_up_by_user_id:
        dog.picked_up_by = db.query(User).filter(User.id == dog.picked_up_by_user_id).first()
    
    return convert_dog_to_schema(dog)

@router.patch("/users/{id}/role")
def update_user_role(
    id: int,
    is_admin: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Dodela admin prava korisniku"""
    if id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own admin status"
        )
    
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_admin = is_admin
    db.commit()
    
    return {"message": f"User {'promoted to' if is_admin else 'removed from'} admin"}

@router.delete("/dog-images/{image_id}")
def delete_dog_image(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Briše određenu sliku (admin)"""
    image = db.query(DogImage).filter(DogImage.id == image_id).first()
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    # Delete file from filesystem
    image_path = os.path.join("uploads", image.filename)
    if os.path.exists(image_path):
        try:
            os.remove(image_path)
        except Exception:
            pass  # Continue even if file deletion fails
    
    db.delete(image)
    db.commit()
    
    return {"message": "Image deleted successfully"}
