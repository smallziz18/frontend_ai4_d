import logging
import uuid
from typing import Optional, Dict, Any

from fastapi import HTTPException,status
from passlib.context import CryptContext
from datetime import timedelta, datetime, timezone
import jwt
from sqlalchemy.exc import NoResultFound
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from sqlmodel.ext.asyncio.session import AsyncSession

from src.config import Config
from src.error import InvalidToken, ExpiredToken, UserNotFound
from src.users.models import Utilisateur

# Configuration des tokens
ACCESS_TOKEN_EXPIRE = 3600  # en secondes (1 heure)
REFRESH_TOKEN_EXPIRE = 7 * 24 * 3600  # 7 jours en secondes

# Configuration du contexte de mot de passe
password_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)


def generate_password_hash(password: str) -> str:
    """Génère un hash sécurisé du mot de passe"""
    if not password:
        raise ValueError("Le mot de passe ne peut pas être vide")
    return password_context.hash(password)


def verify_password_hash(password: str, password_hash: str) -> bool:
    """Vérifie un mot de passe contre son hash"""
    if not password or not password_hash:
        return False
    return password_context.verify(password, password_hash)


def create_access_token(
        data: dict,
        expires_delta: Optional[timedelta] = None,
        refresh: bool = False
) -> str:
    """Crée un token d'accès ou de rafraîchissement"""
    if not data:
        raise ValueError("Les données utilisateur sont requises")

    # Éviter la double imbrication
    payload_data = data if "user" in data else {"user": data}

    # Calculer l'expiration
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        default_expire = REFRESH_TOKEN_EXPIRE if refresh else ACCESS_TOKEN_EXPIRE
        expire = datetime.now(timezone.utc) + timedelta(seconds=default_expire)

    # Créer le payload
    payload = {
        **payload_data,  # Utiliser directement les données sans réencapsuler
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "jti": str(uuid.uuid4()),
        "type": "refresh" if refresh else "access",
        "refresh": refresh
    }

    try:
        token = jwt.encode(
            payload,
            key=Config.JWT_SECRET,
            algorithm=Config.JWT_ALGORITHM
        )
        return token
    except Exception as e:
        raise ValueError(f"Erreur lors de la création du token: {str(e)}")


def decode_token(token: str) -> Dict[str, Any]:
    """
    Décode et valide un token JWT

    Args:
        token: Token JWT à décoder

    Returns:
        dict: Payload du token décodé

    Raises:
        ExpiredToken: Si le token a expiré
        InvalidToken: Si le token est invalide
    """
    if not token:
        raise InvalidToken()

    try:
        # Décoder le token
        payload = jwt.decode(
            token,
            key=Config.JWT_SECRET,
            algorithms=[Config.JWT_ALGORITHM]
        )

        # Vérifications supplémentaires
        if not payload.get("user"):
            raise InvalidToken()

        if not payload.get("jti"):
            raise InvalidToken()

        # Vérifier que le token n'est pas expiré (double vérification)
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
            raise ExpiredToken()

        return payload

    except jwt.ExpiredSignatureError:
        raise ExpiredToken()
    except jwt.InvalidTokenError :
        raise InvalidToken()
    except Exception :
        raise InvalidToken()


def validate_token_type(token_data: Dict[str, Any], expected_type: str) -> bool:
    """
    Valide que le token est du bon type (access ou refresh)

    Args:
        token_data: Données du token décodé
        expected_type: Type attendu ("access" ou "refresh")

    Returns:
        bool: True si le type correspond
    """
    token_type = token_data.get("type", "access")  # Par défaut access pour compatibilité
    return token_type == expected_type


def extract_user_from_token(token_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extrait les données utilisateur du token

    Args:
        token_data: Données du token décodé

    Returns:
        dict: Données utilisateur

    Raises:
        InvalidToken: Si les données utilisateur sont absentes
    """
    user_data = token_data.get("user")
    if not user_data:
        raise InvalidToken()
    return user_data


def get_token_expiry(token_data: Dict[str, Any]) -> datetime:
    """
    Récupère la date d'expiration du token

    Args:
        token_data: Données du token décodé

    Returns:
        datetime: Date d'expiration du token
    """
    exp_timestamp = token_data.get("exp")
    if not exp_timestamp:
        raise InvalidToken()

    return datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)


def is_token_expired(token_data: Dict[str, Any]) -> bool:
    """
    Vérifie si un token est expiré

    Args:
        token_data: Données du token décodé

    Returns:
        bool: True si le token est expiré
    """
    try:
        expiry = get_token_expiry(token_data)
        return expiry < datetime.now(timezone.utc)
    except NoResultFound:
        return True


def get_token_jti(token_data: Dict[str, Any]) -> str:
    """
    Récupère le JTI (JWT ID) du token

    Args:
        token_data: Données du token décodé

    Returns:
        str: JTI du token

    Raises:
        InvalidToken: Si le JTI est absent
    """
    jti = token_data.get("jti")
    if not jti:
        raise InvalidToken()
    return jti

serializer = URLSafeTimedSerializer(
        Config.JWT_SECRET,
        salt=" email-configuration"
    )
def create_url_safe_token(data : dict):

    token = serializer.dumps(data)
    return token

def decode_url_safe_token(token: str):
    try:
        token_data = serializer.loads(token)
        return token_data
    except Exception as e:
        logging.error(e)


# Ajouter cette fonction dans src/users/utils.py
async def validate_email_token_and_get_user(
        token: str,
        session: AsyncSession
) -> Utilisateur:
    """
    Valide un token d'email et retourne l'utilisateur correspondant

    Args:
        token: Token à valider
        session: Session de base de données

    Returns:
        Utilisateur: L'utilisateur trouvé

    Raises:
        HTTPException: Si le token est invalide ou l'utilisateur introuvable
    """
    # Décoder le token
    token_data = decode_url_safe_token(token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token format"
        )

    # Extraire l'email
    user_email = str(token_data.get("email", "")).strip().lower()
    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not found in token"
        )

    # Récupérer l'utilisateur
    from src.users.services import UserService
    user_service = UserService()
    user = await user_service.get_user_by_email(user_email, session)

    if not user:
        raise UserNotFound()

    return user


