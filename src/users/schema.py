from typing import List, Optional
from uuid import UUID
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


# -------- ENUM --------

class StatutUtilisateur(str, Enum):
    ETUDIANT = "Etudiant"
    PROFESSEUR = "Professeur"


# -------- BASE COMMUNE --------

class UtilisateurBase(BaseModel):
    nom: str
    prenom: str
    email: EmailStr
    motDePasseHash: str
    statut: StatutUtilisateur


# -------- SCHÉMAS DE CRÉATION --------

class ProfesseurCreate(UtilisateurBase):
    statut: StatutUtilisateur = StatutUtilisateur.PROFESSEUR
    niveau_experience: int = Field(ge=0, le=20)
    specialites: List[str]
    motivation_principale: Optional[str]
    niveau_technologique: int = Field(ge=1, le=10)


class EtudiantCreate(UtilisateurBase):
    statut: StatutUtilisateur = StatutUtilisateur.ETUDIANT
    niveau_technique: int = Field(ge=1, le=10)
    competences: List[str]
    objectifs_apprentissage: Optional[str]
    motivation: Optional[str]
    niveau_energie: int = Field(ge=1, le=10)


# -------- SCHÉMAS DE LECTURE (GET) --------

class UtilisateurRead(BaseModel):
    id: UUID
    nom: str
    prenom: str
    email: EmailStr
    statut: StatutUtilisateur
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProfesseurRead(UtilisateurRead):
    niveau_experience: int
    specialites: List[str]
    motivation_principale: Optional[str]
    niveau_technologique: int


class EtudiantRead(UtilisateurRead):
    niveau_technique: int
    competences: List[str]
    objectifs_apprentissage: Optional[str]
    motivation: Optional[str]
    niveau_energie: int
