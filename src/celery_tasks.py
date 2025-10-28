from celery import Celery
from asgiref.sync import async_to_sync
from src.mail import create_message, mail
from src.config import Config
import json
import re

# Configuration Celery
app = Celery(
    'tasks',
    broker=getattr(Config, 'REDIS_URL', None) or f"redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}/{Config.REDIS_DB}",
    backend=getattr(Config, 'REDIS_URL', None) or f"redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}/{Config.REDIS_DB}"
)

# Configuration supplémentaire
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@app.task
def send_email(recipients, subject, body):
    """Tâche d'envoi d'email asynchrone"""
    try:
        message = create_message(recipients, subject, body)
        async_to_sync(mail.send_message)(message)
        print(f"sent email to: {recipients}")
        return {"status": "success", "message": f"Email envoyé à {recipients}"}
    except Exception as e:
        print(e)
        return {"status": "failed", "error": str(e)}


def _fallback_question(user: dict) -> str:
    """Fallback déterministe si LLM indisponible."""
    status = str(user.get('status', '') or '')
    if status == 'Etudiant':
        parts = []
        competences = user.get('competences') or []
        if competences:
            parts.append(f"Tu connais déjà {', '.join(competences)}.")
        objectifs = user.get('objectifs_apprentissage')
        if objectifs:
            parts.append(f"Ton objectif est: {objectifs}.")
        base = "Quelle est la prochaine compétence que tu aimerais développer dans les 2 semaines à venir ?"
        return (" ".join(parts) + " " + base).strip()
    if status == 'Professeur':
        parts = []
        specialites = user.get('specialites') or []
        if specialites:
            parts.append(f"Tes spécialités: {', '.join(specialites)}.")
        motiv = user.get('motivation_principale')
        if motiv:
            parts.append(f"Ta motivation principale: {motiv}.")
        base = "Quel est le principal défi pédagogique que tu souhaites adresser avec tes apprenants ?"
        return (" ".join(parts) + " " + base).strip()
    return "Quel est ton principal objectif d'apprentissage cette semaine ?"


def _clean_json_like(text: str):
    """Nettoie une sortie type Markdown ```json ... ``` et tente de parser en JSON."""
    if not isinstance(text, str):
        return None, None

    # 1. Enlever les fences ```json ... ``` ou ```...```
    cleaned = re.sub(r"^```(?:json)?\s*\n?|\n?```\s*$", "", text.strip())

    # 2. Enlever les espaces en début de lignes (indentation)
    lines = cleaned.split('\n')
    cleaned = '\n'.join(line.strip() for line in lines)

    # 3. Tenter de charger directement en JSON
    try:
        parsed = json.loads(cleaned)
        return cleaned, parsed
    except Exception as e1:
        pass

    # 4. Tenter de trouver un objet JSON ou array dans le texte
    # Chercher entre { } ou [ ]
    try:
        # Trouver le premier { ou [
        start_brace = cleaned.find('{')
        start_bracket = cleaned.find('[')

        if start_brace != -1 and (start_bracket == -1 or start_brace < start_bracket):
            # Commencer par {
            depth = 0
            for i in range(start_brace, len(cleaned)):
                if cleaned[i] == '{':
                    depth += 1
                elif cleaned[i] == '}':
                    depth -= 1
                    if depth == 0:
                        json_str = cleaned[start_brace:i+1]
                        parsed = json.loads(json_str)
                        return json_str, parsed
        elif start_bracket != -1:
            # Commencer par [
            depth = 0
            for i in range(start_bracket, len(cleaned)):
                if cleaned[i] == '[':
                    depth += 1
                elif cleaned[i] == ']':
                    depth -= 1
                    if depth == 0:
                        json_str = cleaned[start_bracket:i+1]
                        parsed = json.loads(json_str)
                        return json_str, parsed
    except Exception as e2:
        pass

    # 5. Tenter avec unescaping des caractères Unicode
    try:
        unescaped = cleaned.encode('utf-8').decode('unicode_escape')
        parsed = json.loads(unescaped)
        return unescaped, parsed
    except Exception:
        pass

    # 6. Remplacer les guillemets simples par doubles (cas courant)
    try:
        # Attention: ceci est un hack et peut causer des problèmes
        fixed = cleaned.replace("'", '"')
        parsed = json.loads(fixed)
        return fixed, parsed
    except Exception:
        pass

    # 7. Nettoyer les caractères de contrôle
    try:
        # Enlever les caractères de contrôle sauf \n, \r, \t
        import string
        printable = set(string.printable)
        cleaned_chars = ''.join(c for c in cleaned if c in printable)
        parsed = json.loads(cleaned_chars)
        return cleaned_chars, parsed
    except Exception:
        pass

    return cleaned, None


@app.task(name="generate_profile_question_task")
def generate_profile_question_task(user_data: dict):
    """Génère une question personnalisée (LLM si dispo), sinon fallback.
    Retourne un objet avec question brute et JSON parsé si applicable.
    """
    try:
        try:
            from src.ai_agents.profiler.question_generator import generate_profile_question as llm_generate
        except Exception:
            llm_generate = None

        if llm_generate:
            try:
                question = llm_generate(type('U', (), user_data))  # objet léger ad-hoc
                cleaned, parsed = _clean_json_like(question)
                if parsed and isinstance(parsed, list) and len(parsed) > 0:
                    return {"ok": True, "source": "llm", "question": cleaned or question, "json": parsed}
                else:
                    # Si le parsing échoue, utiliser le fallback
                    print(f"LLM parsing failed, using fallback. Raw: {question[:200] if question else 'None'}")
            except Exception as e:
                print(f"LLM generation failed: {e}, using fallback")
                # fallback si LLM échoue
                pass

        # Fallback: générer des questions de base
        q = _fallback_question(user_data)
        return {"ok": True, "source": "fallback", "question": q, "json": None}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.task(name="profile_analysis_task")
def profile_analysis_task(user_data: dict, evaluation: dict):
    """
    Analyse les résultats du quiz avec gamification complète et met à jour le profil.
    Utilise le LLM pour une analyse approfondie ET le moteur de gamification.
    """
    try:
        from src.ai_agents.profiler.profile_analyzer import analyze_profile_with_llm
        from src.profile.services import profile_service
        from uuid import UUID as _UUID

        print(f"[PROFILE_ANALYSIS] Starting analysis for user: {user_data.get('username', 'unknown')}")

        # 1) Extraire user_id
        user_id_raw = user_data.get('id')
        try:
            user_uuid = _UUID(str(user_id_raw))
        except Exception:
            user_uuid = str(user_id_raw)

        # 2) Extraire le temps pris pour le quiz (si disponible)
        time_taken = evaluation.get("time_taken_seconds")

        # 3) Appeler la méthode de gamification qui fait tout le travail
        print(f"[PROFILE_ANALYSIS] Calling gamification engine...")
        result = async_to_sync(profile_service.analyze_quiz_and_update_profile)(
            user_uuid,
            evaluation,
            time_taken_seconds=time_taken
        )

        print(f"[PROFILE_ANALYSIS] Gamification complete. XP earned: {result['xp_earned']['total_xp']}")
        print(f"[PROFILE_ANALYSIS] Badges earned: {result['badges_earned']}")
        print(f"[PROFILE_ANALYSIS] Level: {result['old_level']} -> {result['new_level']}")

        # 4) Optionnel: Appeler le LLM pour une analyse encore plus approfondie
        # Ceci enrichit l'analyse mais n'est pas obligatoire
        try:
            user_json = json.dumps(user_data, default=str, ensure_ascii=False)
            evaluation_json = json.dumps(evaluation, ensure_ascii=False)

            print(f"[PROFILE_ANALYSIS] Calling LLM for deep analysis...")
            llm_text = analyze_profile_with_llm(user_json, evaluation_json)

            # Parser la réponse LLM
            cleaned, parsed = _clean_json_like(llm_text)

            if isinstance(parsed, dict):
                # Enrichir les recommandations avec celles du LLM
                llm_recommendations = parsed.get("recommandations", [])
                if llm_recommendations:
                    result["recommendations"].extend(llm_recommendations)
                    # Dédupliquer
                    result["recommendations"] = list(dict.fromkeys(result["recommendations"]))

                # Ajouter l'analyse LLM au résultat
                result["llm_analysis"] = parsed

                print(f"[PROFILE_ANALYSIS] LLM analysis added successfully")
            else:
                print(f"[PROFILE_ANALYSIS] LLM parsing failed, continuing with gamification only")

        except Exception as llm_error:
            print(f"[PROFILE_ANALYSIS] LLM analysis failed: {llm_error}, continuing with gamification only")
            # Pas grave, on continue avec la gamification seule

        # 5) Formatter le profil pour la réponse
        prof_dict = result["profile"].model_dump() if hasattr(result["profile"], 'model_dump') else getattr(result["profile"], '__dict__', None)

        print(f"[PROFILE_ANALYSIS] Task completed successfully")

        return {
            "ok": True,
            "profile": prof_dict,
            "xp_earned": result["xp_earned"],
            "badges_earned": result["badges_earned"],
            "level_up": result["level_up"],
            "old_level": result["old_level"],
            "new_level": result["new_level"],
            "streak_info": result["streak_info"],
            "quiz_summary": result["quiz_summary"],
            "performance_analysis": result["performance_analysis"],
            "recommendations": result["recommendations"][:10],  # Limiter à 10 recommandations
        }

    except Exception as e:
        print(f"[PROFILE_ANALYSIS] Task failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"ok": False, "error": str(e)}
