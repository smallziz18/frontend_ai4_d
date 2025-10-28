"""
Gestion des tokens de vérification et reset de mot de passe
"""
from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4
import secrets

from sqlmodel import SQLModel, Field, select
from sqlalchemy import Column
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy.dialects.postgresql as pg


class VerificationToken(SQLModel, table=True):
    """Token de vérification d'email"""
    __tablename__ = "verification_token"

    id: int = Field(primary_key=True)
    user_id: str = Field(foreign_key="utilisateur.id", index=True)
    token: str = Field(unique=True, index=True)
    token_type: str = Field(default="email_verification")  # ou "password_reset"

    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, default=datetime.now)
    )
    expires_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP)
    )
    used_at: Optional[datetime] = Field(
        sa_column=Column(pg.TIMESTAMP, nullable=True),
        default=None
    )

    is_used: bool = Field(default=False)


class TokenService:
    """Service pour gérer les tokens de vérification"""

    @staticmethod
    def generate_token() -> str:
        """Génère un token sécurisé"""
        return secrets.token_urlsafe(32)

    @staticmethod
    async def create_verification_token(
        user_id: str,
        session: AsyncSession,
        token_type: str = "email_verification",
        expiry_hours: int = 24
    ) -> VerificationToken:
        """
        Crée un token de vérification

        Args:
            user_id: ID de l'utilisateur
            session: Session de base de données
            token_type: Type de token (email_verification ou password_reset)
            expiry_hours: Durée de validité en heures (défaut 24h)
        """
        # Invalider les tokens précédents non utilisés
        await TokenService.invalidate_user_tokens(user_id, token_type, session)

        token = TokenService.generate_token()
        expires_at = datetime.now() + timedelta(hours=expiry_hours)

        verification_token = VerificationToken(
            user_id=user_id,
            token=token,
            token_type=token_type,
            created_at=datetime.now(),
            expires_at=expires_at,
            is_used=False
        )

        session.add(verification_token)
        await session.commit()
        await session.refresh(verification_token)

        return verification_token

    @staticmethod
    async def verify_token(
        token: str,
        token_type: str,
        session: AsyncSession
    ) -> Optional[VerificationToken]:
        """
        Vérifie un token et le marque comme utilisé

        Returns:
            VerificationToken si valide, None sinon
        """
        stmt = select(VerificationToken).where(
            VerificationToken.token == token,
            VerificationToken.token_type == token_type,
            VerificationToken.is_used == False
        )
        result = await session.execute(stmt)
        token_obj = result.scalar_one_or_none()

        if not token_obj:
            return None

        # Vérifier si le token n'a pas expiré
        if datetime.now() > token_obj.expires_at:
            return None

        # Marquer comme utilisé
        token_obj.is_used = True
        token_obj.used_at = datetime.now()
        await session.commit()

        return token_obj

    @staticmethod
    async def invalidate_user_tokens(
        user_id: str,
        token_type: str,
        session: AsyncSession
    ):
        """Invalide tous les tokens non utilisés d'un utilisateur"""
        stmt = select(VerificationToken).where(
            VerificationToken.user_id == user_id,
            VerificationToken.token_type == token_type,
            VerificationToken.is_used == False
        )
        result = await session.execute(stmt)
        tokens = result.scalars().all()

        for token in tokens:
            token.is_used = True
            token.used_at = datetime.now()

        await session.commit()

    @staticmethod
    async def cleanup_expired_tokens(session: AsyncSession):
        """Nettoie les tokens expirés (à exécuter périodiquement)"""
        stmt = select(VerificationToken).where(
            VerificationToken.expires_at < datetime.now()
        )
        result = await session.execute(stmt)
        expired_tokens = result.scalars().all()

        for token in expired_tokens:
            await session.delete(token)

        await session.commit()
        return len(expired_tokens)

