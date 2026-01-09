from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.db.models import DogStatus

class DogImageBase(BaseModel):
    filename: str

class DogImageCreate(DogImageBase):
    pass

class DogImage(DogImageBase):
    id: int
    dog_id: int
    uploaded_by: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

class DogBase(BaseModel):
    title: str
    description: Optional[str] = None
    latitude: float = Field(..., ge=-90, le=90, description="Latitude must be between -90 and 90")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude must be between -180 and 180")

class DogCreate(DogBase):
    pass

class DogUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)

class DogInDB(DogBase):
    id: int
    reporter_id: Optional[int] = None
    status: DogStatus
    picked_up_by_user_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Dog(DogInDB):
    images: List[DogImage] = []
    reporter: Optional[dict] = None
    picked_up_by: Optional[dict] = None

class DogList(BaseModel):
    id: int
    title: str
    latitude: float
    longitude: float
    status: DogStatus
    created_at: datetime
    images: List[DogImage] = []

    class Config:
        from_attributes = True
