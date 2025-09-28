from typing import List, Optional, Dict, Any, Annotated
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, BeforeValidator
from bson import ObjectId

class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, handler):  # Ajout du paramètre handler
        if not isinstance(v, (str, ObjectId)):
            raise ValueError("Invalid ObjectId")
        if isinstance(v, str) and not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(ObjectId(v))

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


# Type annoté pour ObjectId
PyObjectIdAnnotated = Annotated[PyObjectId, BeforeValidator(PyObjectId.validate)]


class ProfilMongoDB(BaseModel):
    """Modèle Profil pour MongoDB"""
    id: Optional[PyObjectIdAnnotated] = Field(default_factory=PyObjectId, alias="_id")
    utilisateur_id: UUID
    niveau: int = Field(default=1, ge=1)
    xp: int = Field(default=0, ge=0)
    badges: List[str] = Field(default_factory=list)
    competences: List[str] = Field(default_factory=list)
    objectifs: Optional[str] = None
    motivation: Optional[str] = None
    energie: int = Field(default=5, ge=1, le=10)
    preferences: Dict[str, Any] = Field(default_factory=dict)
    historique_activites: List[Dict[str, Any]] = Field(default_factory=list)
    statistiques: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }
