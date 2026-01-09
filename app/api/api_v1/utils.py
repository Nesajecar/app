from app.db.models import Dog
from app.schemas.dog import Dog as DogSchema, DogInDB

def convert_dog_to_schema(dog: Dog) -> DogSchema:
    """Konvertuje Dog SQLAlchemy objekat u DogSchema sa konvertovanim reporter i picked_up_by"""
    # Prvo kreiramo DogInDB bez reporter i picked_up_by
    dog_in_db = DogInDB.from_orm(dog)
    
    # Konvertujemo u dictionary
    dog_dict = dog_in_db.model_dump()
    
    # Dodajemo images
    dog_dict["images"] = [{"id": img.id, "dog_id": img.dog_id, "filename": img.filename, 
                          "uploaded_by": img.uploaded_by, "created_at": img.created_at} 
                         for img in dog.images]
    
    # Konvertujemo reporter i picked_up_by u dictionary ako postoje
    if dog.reporter:
        dog_dict["reporter"] = {
            "id": dog.reporter.id,
            "full_name": dog.reporter.full_name,
            "email": dog.reporter.email
        }
    else:
        dog_dict["reporter"] = None
        
    if dog.picked_up_by:
        dog_dict["picked_up_by"] = {
            "id": dog.picked_up_by.id,
            "full_name": dog.picked_up_by.full_name,
            "email": dog.picked_up_by.email
        }
    else:
        dog_dict["picked_up_by"] = None
    
    # Kreiramo DogSchema iz dictionary-a
    return DogSchema(**dog_dict)
