from datetime import datetime
from uuid import UUID
from typing import List, Union, Any, Coroutine, Sequence

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
    async def create_user(
            session: AsyncSession,
            data: Union[EtudiantCreate, ProfesseurCreate]
    ):
        utilisateur = Utilisateur(
            nom=data.nom,
            prenom=data.prenom,
            email=data.email,
            motDePasseHash=data.motDePasseHash,
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



