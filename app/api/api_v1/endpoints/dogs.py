from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os
import uuid

from app.db.database import get_db
from app.db.models import Dog, DogImage, User, DogStatus
from app.schemas.dog import DogCreate, DogUpdate, Dog as DogSchema, DogList
from app.api.deps import get_current_user, get_current_active_user
from app.core.config import settings
from app.api.api_v1.utils import convert_dog_to_schema

router = APIRouter()

@router.get("/", response_model=List[DogList])
def get_dogs(
    status: Optional[DogStatus] = Query(None, description="Filter by status"),
    lat: Optional[float] = Query(None, description="Latitude for location filtering"),
    lng: Optional[float] = Query(None, description="Longitude for location filtering"),
    db: Session = Depends(get_db)
):
    """Lista prijavljenih pasa, opcionalno filtriranje po statusu i lokaciji"""
    query = db.query(Dog).filter(Dog.status != DogStatus.REMOVED)
    
    # Filter by status
    if status:
        query = query.filter(Dog.status == status)
    
    # Simple location filtering (basic implementation)
    # In production, use PostGIS or more sophisticated distance calculation
    if lat is not None and lng is not None:
        # This is a placeholder - implement proper distance calculation if needed
        pass
    
    dogs = query.order_by(Dog.created_at.desc()).all()
    
    return dogs

@router.get("/{id}", response_model=DogSchema)
def get_dog(id: int, db: Session = Depends(get_db)):
    """Detalji psa"""
    dog = db.query(Dog).filter(Dog.id == id).first()
    if not dog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dog not found"
        )
    
    # Konvertuj u schema format
    return convert_dog_to_schema(dog)

@router.post("/", response_model=DogSchema, status_code=status.HTTP_201_CREATED)
def create_dog(
    dog: DogCreate,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Unos nove prijave psa"""
    # Create new dog report
    db_dog = Dog(
        title=dog.title,
        description=dog.description,
        latitude=dog.latitude,
        longitude=dog.longitude,
        reporter_id=current_user.id if current_user else None,
        status=DogStatus.REPORTED
    )
    
    db.add(db_dog)
    db.commit()
    db.refresh(db_dog)
    
    # Učitaj relationships
    if db_dog.reporter_id:
        db_dog.reporter = db.query(User).filter(User.id == db_dog.reporter_id).first()
    
    return convert_dog_to_schema(db_dog)

@router.put("/{id}", response_model=DogSchema)
def update_dog(
    id: int,
    dog_update: DogUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Izmena prijave psa (samo autor ili admin)"""
    dog = db.query(Dog).filter(Dog.id == id).first()
    if not dog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dog not found"
        )
    
    # Check if user can update (reporter or admin)
    if dog.reporter_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Update fields
    update_data = dog_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(dog, field, value)
    
    dog.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(dog)
    
    # Učitaj relationships
    if dog.reporter_id:
        dog.reporter = db.query(User).filter(User.id == dog.reporter_id).first()
    if dog.picked_up_by_user_id:
        dog.picked_up_by = db.query(User).filter(User.id == dog.picked_up_by_user_id).first()
    
    return convert_dog_to_schema(dog)

@router.delete("/{id}")
def delete_dog(
    id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Brisanje prijave psa (admin ili autor)"""
    dog = db.query(Dog).filter(Dog.id == id).first()
    if not dog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dog not found"
        )
    
    # Check if user can delete (reporter or admin)
    if dog.reporter_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Delete associated images from filesystem
    for image in dog.images:
        image_path = os.path.join(settings.UPLOAD_DIR, image.filename)
        if os.path.exists(image_path):
            try:
                os.remove(image_path)
            except Exception:
                pass  # Continue even if file deletion fails
    
    db.delete(dog)
    db.commit()
    
    return {"message": "Dog deleted successfully"}

@router.post("/{id}/images")
def upload_dog_image(
    id: int,
    file: UploadFile = File(...),
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload slike za psa (multipart)"""
    # Check if dog exists
    dog = db.query(Dog).filter(Dog.id == id).first()
    if not dog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dog not found"
        )
    
    # Check file type
    file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    if file_extension not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        content = file.file.read()
        buffer.write(content)
    
    # Create database record
    db_image = DogImage(
        dog_id=id,
        filename=unique_filename,
        uploaded_by=current_user.id if current_user else None
    )
    
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    
    return {"message": "Image uploaded successfully", "filename": unique_filename, "url": f"/uploads/{unique_filename}"}

@router.get("/{id}/images", response_model=List[dict])
def get_dog_images(id: int, db: Session = Depends(get_db)):
    """Vraća listu fotografija psa"""
    dog = db.query(Dog).filter(Dog.id == id).first()
    if not dog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dog not found"
        )
    
    images = []
    for image in dog.images:
        images.append({
            "id": image.id,
            "filename": image.filename,
            "url": f"/uploads/{image.filename}",
            "uploaded_by": image.uploaded_by,
            "created_at": image.created_at
        })
    
    return images

@router.post("/{id}/picked-up", response_model=DogSchema)
def mark_dog_picked_up(
    id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Korisnik označava psa kao spašenog → status pending_admin"""
    dog = db.query(Dog).filter(Dog.id == id).first()
    if not dog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dog not found"
        )
    
    if dog.status != DogStatus.REPORTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dog is not in reported status"
        )
    
    # Update dog status
    dog.status = DogStatus.PENDING_ADMIN
    dog.picked_up_by_user_id = current_user.id
    dog.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(dog)
    
    # Učitaj relationships
    if dog.reporter_id:
        dog.reporter = db.query(User).filter(User.id == dog.reporter_id).first()
    if dog.picked_up_by_user_id:
        dog.picked_up_by = db.query(User).filter(User.id == dog.picked_up_by_user_id).first()
    
    return convert_dog_to_schema(dog)
