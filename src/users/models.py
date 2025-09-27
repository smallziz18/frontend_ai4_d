from typing import List, Optional
from enum import Enum
from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, ForeignKey
import sqlalchemy.dialects.postgresql as pg


class StatutUtilisateur(str, Enum):
    ETUDIANT = "Etudiant"
    PROFESSEUR = "Professeur"


class UtilisateurBase(SQLModel):
    nom: str = Field(nullable=False)
    prenom: str = Field(nullable=False)
    username:  str= Field(
            unique=True,
            nullable=False,
    )

    email: str = Field(unique=True, nullable=False)
    motDePasseHash: str
    statut: StatutUtilisateur
    created_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP,
            default=datetime.now
        )
    )
    updated_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP,
            default=datetime.now
        )
    )
    is_verified: bool = Field(
        sa_column=Column(
            pg.BOOLEAN,
            default=False
        )
    )




class Utilisateur(UtilisateurBase, table=True):
    __tablename__ = "utilisateur"
    id: UUID = Field(
        sa_column=Column(
            pg.UUID,
            primary_key=True,
            default=uuid4
        )
    )

    # Relations vers les tables enfants
    professeur: Optional["Professeur"] = Relationship(back_populates="utilisateur")
    etudiant: Optional["Etudiant"] = Relationship(back_populates="utilisateur")


class Professeur(SQLModel, table=True):
    __tablename__ = "professeur"
    id: UUID = Field(
        sa_column=Column(
            pg.UUID, ForeignKey("utilisateur.id"),
            primary_key=True,
            default=uuid4
        )
    )


    utilisateur: Utilisateur = Relationship(back_populates="professeur")

    niveau_experience: int = Field(ge=0, le=30, description="Années d'expérience pédagogique")
    specialites: List[str] = Field(
        sa_column=Column(pg.ARRAY(pg.TEXT)), default_factory=list, description="Domaines d'expertise"
    )
    motivation_principale: Optional[str] = None
    niveau_technologique: int = Field(ge=1, le=10)
    def __repr__(self) -> str:
        return f"Professeur(id={self.id})"


class Etudiant(SQLModel, table=True):
    __tablename__ = "etudiant"
    id: UUID = Field(
        sa_column=Column(
            pg.UUID, ForeignKey("utilisateur.id"),
            primary_key=True,
            default=uuid4
        )
    )

    utilisateur: Utilisateur = Relationship(back_populates="etudiant")

    niveau_technique: int = Field(ge=1, le=10)
    competences: List[str] = Field(
        sa_column=Column(pg.ARRAY(pg.TEXT)), default_factory=list
    )
    objectifs_apprentissage: Optional[str] = None
    motivation: Optional[str] = None
    niveau_energie: int = Field(ge=1, le=10)
    def __repr__(self) -> str:
        return f"Etudiant(id={self.id})"
