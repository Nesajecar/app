from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.database import Base

class DogStatus(str, enum.Enum):
    REPORTED = "reported"
    PENDING_ADMIN = "pending_admin"
    CONFIRMED = "confirmed"
    REMOVED = "removed"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    dogs_reported = relationship("Dog", foreign_keys="Dog.reporter_id", back_populates="reporter")
    dogs_picked_up = relationship("Dog", foreign_keys="Dog.picked_up_by_user_id", back_populates="picked_up_by")
    images_uploaded = relationship("DogImage", back_populates="uploader")

class Dog(Base):
    __tablename__ = "dogs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    status = Column(Enum(DogStatus), default=DogStatus.REPORTED)
    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    picked_up_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    reporter = relationship("User", foreign_keys=[reporter_id], back_populates="dogs_reported")
    picked_up_by = relationship("User", foreign_keys=[picked_up_by_user_id], back_populates="dogs_picked_up")
    images = relationship("DogImage", back_populates="dog", cascade="all, delete-orphan")

class DogImage(Base):
    __tablename__ = "dog_images"
    
    id = Column(Integer, primary_key=True, index=True)
    dog_id = Column(Integer, ForeignKey("dogs.id"), nullable=False)
    filename = Column(String, nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    dog = relationship("Dog", back_populates="images")
    uploader = relationship("User", back_populates="images_uploaded")
