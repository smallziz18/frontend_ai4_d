from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query


from src.profile.schema import ProfilResponse, ProfilCreate, ProfilUpdate, XPRequest, BadgeRequest, CompetenceRequest, \
    PreferencesRequest, ActivityRequest, AchievementRequest
from src.profile.services import profile_service
from src.users.dependencies import get_current_user
from src.users.models import Utilisateur


router = APIRouter()





@router.post("/", response_model=ProfilResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
        profile_data: ProfilCreate,
        current_user: Utilisateur = Depends(get_current_user)
):
    """Créer le profil de l'utilisateur connecté"""

    # Assigner automatiquement l'ID de l'utilisateur connecté
    profile_data.utilisateur_id = current_user.id

    try:
        profile = await profile_service.create_profile(profile_data)
        return profile
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create profile"
        )


@router.get("/", response_model=ProfilResponse)
async def get_my_profile(
        current_user: Utilisateur = Depends(get_current_user)
):
    """Récupérer le profil de l'utilisateur connecté ou le créer s'il n'existe pas"""
    profile = await profile_service.get_profile_by_user_id(current_user.id)

    if not profile:
        # Créer un nouveau profil avec les valeurs par défaut
        profile_data = ProfilCreate(
            utilisateur_id=current_user.id,
            niveau=1,
            xp=0,
            badges=[],
            competences=[],
            energie=5
        )
        try:
            profile = await profile_service.create_profile(profile_data)
        except ValueError as e:
            # En cas de création simultanée, on réessaie de récupérer
            profile = await profile_service.get_profile_by_user_id(current_user.id)
            if not profile:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create or retrieve profile"
                )

    return profile


@router.put("/", response_model=ProfilResponse)
async def update_profile(
        update_data: ProfilUpdate,
        current_user: Utilisateur = Depends(get_current_user)
):
    """Mettre à jour le profil de l'utilisateur connecté"""

    profile = await profile_service.update_profile(current_user.id, update_data)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    return profile


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
        current_user: Utilisateur = Depends(get_current_user)
):
    """Supprimer le profil de l'utilisateur connecté"""

    success = await profile_service.delete_profile(current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )


@router.post("/xp")
async def add_xp(
        xp_request: XPRequest,
        current_user: Utilisateur = Depends(get_current_user)
):
    """Ajouter de l'XP au profil de l'utilisateur connecté"""

    if xp_request.xp_points <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="XP points must be positive"
        )

    profile = await profile_service.add_xp(current_user.id, xp_request.xp_points)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    return {
        "message": f"Added {xp_request.xp_points} XP",
        "new_xp": profile.xp,
        "level": profile.niveau
    }


@router.post("/badges")
async def add_badge(
        badge_request: BadgeRequest,
        current_user: Utilisateur = Depends(get_current_user)
):
    """Ajouter un badge au profil de l'utilisateur connecté"""

    profile = await profile_service.add_badge(current_user.id, badge_request.badge)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    return {
        "message": f"Badge '{badge_request.badge}' added",
        "total_badges": len(profile.badges),
        "badges": profile.badges
    }


@router.post("/competences")
async def add_competence(
        competence_request: CompetenceRequest,
        current_user: Utilisateur = Depends(get_current_user)
):
    """Ajouter une compétence au profil de l'utilisateur connecté"""

    profile = await profile_service.add_competence(current_user.id, competence_request.competence)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    return {
        "message": f"Competence '{competence_request.competence}' added",
        "total_competences": len(profile.competences),
        "competences": profile.competences
    }


@router.put("/preferences")
async def update_preferences(
        preferences_request: PreferencesRequest,
        current_user: Utilisateur = Depends(get_current_user)
):
    """Mettre à jour les préférences de l'utilisateur connecté"""

    profile = await profile_service.update_preferences(current_user.id, preferences_request.preferences)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    return {
        "message": "Preferences updated successfully",
        "preferences": profile.preferences
    }


@router.post("/activities")
async def complete_activity(
        activity_request: ActivityRequest,
        current_user: Utilisateur = Depends(get_current_user)
):
    """Enregistrer une activité terminée et optionnellement ajouter de l'XP"""

    profile = await profile_service.complete_activity(
        user_id=current_user.id,
        activity_type=activity_request.activity_type,
        xp_reward=activity_request.xp_reward
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    return {
        "message": f"Activity '{activity_request.activity_type}' completed",
        "xp_earned": activity_request.xp_reward,
        "total_xp": profile.xp,
        "level": profile.niveau
    }


@router.post("/achievements")
async def unlock_achievement(
        achievement_request: AchievementRequest,
        current_user: Utilisateur = Depends(get_current_user)
):
    """Débloquer un succès et optionnellement un badge"""

    profile = await profile_service.unlock_achievement(
        user_id=current_user.id,
        achievement=achievement_request.achievement,
        badge=achievement_request.badge
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    response = {
        "message": f"Achievement '{achievement_request.achievement}' unlocked"
    }

    if achievement_request.badge:
        response["badge_earned"] = achievement_request.badge
        response["total_badges"] = len(profile.badges)

    return response


@router.get("/stats")
async def get_profile_stats(
        current_user: Utilisateur = Depends(get_current_user)
):
    """Obtenir les statistiques du profil de l'utilisateur connecté"""

    stats = await profile_service.get_profile_stats(current_user.id)
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    return stats


@router.get("/leaderboard")
async def get_leaderboard(
        limit: int = Query(10, ge=1, le=100, description="Nombre de profils à retourner")
):
    """Obtenir le classement des utilisateurs par XP"""

    try:
        leaderboard = await profile_service.get_leaderboard(limit)
        return {
            "leaderboard": leaderboard,
            "total_results": len(leaderboard)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get leaderboard"
        )


@router.get("/activities")
async def get_activity_history(
        current_user: Utilisateur = Depends(get_current_user),
        limit: int = Query(50, ge=1, le=200, description="Nombre d'activités à retourner")
):
    """Obtenir l'historique des activités de l'utilisateur connecté"""

    profile = await profile_service.get_profile_by_user_id(current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    # Retourner les dernières activités triées par timestamp
    activities = sorted(
        profile.historique_activites,
        key=lambda x: x.get("timestamp", datetime.min),
        reverse=True
    )[:limit]

    return {
        "activities": activities,
        "total_activities": len(profile.historique_activites)
    }