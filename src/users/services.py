from datetime import datetime
from uuid import UUID
from typing import  Union
from .utils import generate_password_hash,verify_password_hash

from sqlmodel import select,desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.models import Utilisateur, Professeur, Etudiant
from src.users.schema import UtilisateurRead, EtudiantRead, ProfesseurCreate, ProfesseurRead, EtudiantCreate, \
    UtilisateurBase, StatutUtilisateur


class UserService:

    @staticmethod
    async def get_all_users(session: AsyncSession) :
        stmt = select(Utilisateur).order_by(desc(Utilisateur.created_at))
        result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_user(user_id: UUID, session: AsyncSession):
        stmt = select(Utilisateur).where(Utilisateur.id == user_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    @staticmethod
    async def user_exists(user_id: UUID, session: AsyncSession) -> bool:
        stmt = select(Utilisateur).where(Utilisateur.id == user_id)
        result = await session.execute(stmt)
        if result:
            return True
        return False

    @staticmethod
    async def create_user(
            session: AsyncSession,
            data: Union[EtudiantCreate, ProfesseurCreate]
    ):
        utilisateur = Utilisateur(
            nom=data.nom,
            prenom=data.prenom,
            username=data.username,
            email=data.email,
            motDePasseHash=generate_password_hash(data.motDePasseHash),
            statut=data.statut,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.add(utilisateur)

        # Flush envoie INSERT en DB et récupère utilisateur.id
        await session.flush()

        if data.statut == StatutUtilisateur.PROFESSEUR:
            professeur = Professeur(
                id=utilisateur.id,  # clé étrangère qui pointe vers Utilisateur
                niveau_experience=data.niveau_experience,
                specialites=data.specialites,
                motivation_principale=data.motivation_principale,
                niveau_technologique=data.niveau_technologique,
            )
            session.add(professeur)

        elif data.statut == StatutUtilisateur.ETUDIANT:
            etudiant = Etudiant(
                id=utilisateur.id,  # clé étrangère qui pointe vers Utilisateur
                niveau_technique=data.niveau_technique,
                competences=data.competences,
                objectifs_apprentissage=data.objectifs_apprentissage,
                motivation=data.motivation,
                niveau_energie=data.niveau_energie,
            )
            session.add(etudiant)

        else:
            raise ValueError("Statut inconnu")

        # Validation finale
        await session.commit()
        await session.refresh(utilisateur)

        return utilisateur

    @staticmethod
    async def get_user_by_email(email: str, session: AsyncSession):
        stmt = select(Utilisateur).where(Utilisateur.email == email)
        result = await session.scalars(stmt)
        user = result.first()  # user est maintenant un objet Utilisateur
        return user






