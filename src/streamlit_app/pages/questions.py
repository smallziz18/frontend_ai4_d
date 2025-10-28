import streamlit as st
import json
import time
import requests
from datetime import datetime
import re


# Utilitaires de parsing pour extraire des listes JSON depuis du texte LLM
def _clean_json_like_text(text: str) -> tuple[str, object | None]:
    if not isinstance(text, str):
        return "", None
    cleaned = re.sub(r"^```(?:json)?\n|\n```$", "", text.strip())
    try:
        return cleaned, json.loads(cleaned)
    except Exception:
        try:
            unescaped = cleaned.encode('utf-8').decode('unicode_escape')
            return unescaped, json.loads(unescaped)
        except Exception:
            return cleaned, None


def parse_questions_payload(result_data: dict) -> list | None:
    """Parse le payload de réponse pour extraire les questions JSON"""
    try:
        if not isinstance(result_data, dict):
            return None

        # Priorité 1: Si 'json' existe et est déjà une liste
        if 'json' in result_data and isinstance(result_data['json'], list):
            return result_data['json']

        # Priorité 2: Si 'json' est une string, tenter de parser
        if 'json' in result_data and isinstance(result_data['json'], str):
            try:
                _, parsed = _clean_json_like_text(result_data['json'])
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                pass

        # Priorité 3: Si 'question' contient le JSON en string
        if 'question' in result_data and isinstance(result_data['question'], str):
            try:
                cleaned, parsed = _clean_json_like_text(result_data['question'])
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                pass

        # Priorité 4: Chercher toute clé contenant une liste de dicts avec 'question'
        for key, value in result_data.items():
            if isinstance(value, list) and len(value) > 0:
                # Vérifier que c'est bien une liste de questions
                if all(isinstance(item, dict) and 'question' in item for item in value):
                    return value

        return None
    except Exception as e:
        print(f"Erreur de parsing: {e}")
        return None


# Import client HTTP
try:
    from src.streamlit_app.client import make_request, PROFILE_PREFIX, AUTH_PREFIX, is_logged_in
except Exception:
    API_BASE_URL = "http://127.0.0.1:8000"
    AUTH_PREFIX = "/api/auth/v1"
    PROFILE_PREFIX = "/api/profile/v1"


    def make_request(method: str, endpoint: str, data: dict | None = None, auth: bool = False) -> tuple[bool, dict]:
        url = f"{API_BASE_URL}{endpoint}"
        headers = {"Content-Type": "application/json"}
        if auth and st.session_state.get('access_token'):
            headers["Authorization"] = f"Bearer {st.session_state.access_token}"
        try:
            method_u = method.upper()
            if method_u == "GET":
                resp = requests.get(url, headers=headers)
            elif method_u == "POST":
                resp = requests.post(url, json=data, headers=headers)
            elif method_u == "PUT":
                resp = requests.put(url, json=data, headers=headers)
            else:
                return False, {"error": "Method not supported"}
            try:
                body = resp.json()
            except Exception:
                body = {"content": resp.text}
            if isinstance(body, dict):
                body["status_code"] = resp.status_code
            return resp.status_code < 400, body
        except requests.RequestException as e:
            return False, {"error": str(e)}


    def is_logged_in() -> bool:
        return st.session_state.get('access_token') is not None


st.title("❓ Questionnaire Personnalisé")

# Initialisation des variables de session
if 'access_token' not in st.session_state:
    st.session_state.access_token = None
if 'user_info' not in st.session_state:
    st.session_state.user_info = {}
if 'questions' not in st.session_state:
    st.session_state.questions = None
if 'current_question_index' not in st.session_state:
    st.session_state.current_question_index = 0
if 'answers' not in st.session_state:
    st.session_state.answers = {}
if 'quiz_completed' not in st.session_state:
    st.session_state.quiz_completed = False
if 'evaluation_result' not in st.session_state:
    st.session_state.evaluation_result = None
if 'question_task_id' not in st.session_state:
    st.session_state.question_task_id = None
if 'task_check_attempts' not in st.session_state:
    st.session_state.task_check_attempts = 0
if 'profile_task_id' not in st.session_state:
    st.session_state.profile_task_id = None
if 'profile_result' not in st.session_state:
    st.session_state.profile_result = None


# Fonction pour générer les résultats d'évaluation
def generate_evaluation_result():
    """Génère le JSON de résultats avec les réponses de l'utilisateur"""
    questions_list = st.session_state.questions
    evaluation_data = []

    for i, q in enumerate(questions_list):
        q_key = f"q_{i}"
        user_answer = st.session_state.answers.get(q_key, "")

        # Déterminer si la réponse est correcte
        is_correct = False
        if q.get('type') in ["QuestionOuverte", "ListeOuverte"]:
            is_correct = "Non évalué (requiert une analyse humaine)"
        else:
            correct_answer = q.get('correction', '')
            if isinstance(correct_answer, list):
                is_correct = user_answer in correct_answer
            else:
                # Vérifier si la réponse commence par la lettre de la correction (A, B, C, D)
                is_correct = user_answer and user_answer.strip().startswith(correct_answer.split()[0])

        evaluation_data.append({
            "numero": q.get('numero', i + 1),
            "question": q.get('question', ''),
            "type": q.get('type', ''),
            "options": q.get('options', []),
            "user_answer": user_answer,
            "correct_answer": q.get('correction', ''),
            "is_correct": is_correct
        })

    # Calculer le score
    score = sum(1 for item in evaluation_data if item["is_correct"] is True)
    total = len([item for item in evaluation_data if item["is_correct"] != "Non évalué (requiert une analyse humaine)"])

    return {
        "score": f"{score}/{total}",
        "score_percentage": round(score / total * 100 if total > 0 else 0, 2),
        "completed_at": str(datetime.now()),
        "questions_data": evaluation_data
    }


# Fonction pour vérifier le statut d'une tâche asynchrone
def check_task_status(task_id):
    """Vérifie le statut d'une tâche de génération de questions"""
    if not task_id:
        return None
    success, response = make_request("GET", f"{PROFILE_PREFIX}/question_result/{task_id}", auth=True)
    if success:
        return response
    return None


def check_profile_status(task_id):
    """Vérifie le statut d'une tâche de génération de profil"""
    if not task_id:
        return None
    success, response = make_request("GET", f"{PROFILE_PREFIX}/analysis_result/{task_id}", auth=True)
    if success:
        return response
    return None


# ============================================================================
# SECTION AUTHENTIFICATION
# ============================================================================

if not is_logged_in():
    st.warning("⚠️ Vous devez être connecté pour générer un questionnaire.")

    st.subheader("🔐 Connexion")
    with st.form("login_form_questions"):
        email = st.text_input("Email", "utilisateur@example.com")
        password = st.text_input("Mot de passe", type="password", value="password")
        submit = st.form_submit_button("Se connecter")

        if submit:
            login_data = {"email": email, "password": password}
            success, response = make_request("POST", f"{AUTH_PREFIX}/login", login_data)

            if success and "access_token" in response:
                st.session_state.access_token = response["access_token"]
                success, user_info = make_request("GET", f"{AUTH_PREFIX}/me", auth=True)
                if success and user_info:
                    st.session_state.user_info = user_info
                st.success("✅ Connexion réussie!")
                st.rerun()
            else:
                st.error(f"❌ Erreur de connexion: {response.get('detail', 'Identifiants invalides')}")

    st.info("💡 Vous pouvez également vous connecter via la [page d'accueil](/).")
    st.stop()

# ============================================================================
# UTILISATEUR CONNECTÉ
# ============================================================================

username = st.session_state.user_info.get('username', 'Utilisateur')
st.success(f"🙋 Connecté en tant que: **{username}**")

# ============================================================================
# SECTION GÉNÉRATION DE PROFIL (si quiz complété)
# ============================================================================

if st.session_state.quiz_completed and st.session_state.evaluation_result:
    st.success("✅ Questionnaire terminé!")

    result = st.session_state.evaluation_result
    st.metric("Score", f"{result['score']} ({result['score_percentage']}%)")

    st.divider()

    # Bouton pour générer le profil
    if not st.session_state.profile_task_id and not st.session_state.profile_result:
        st.subheader("🧠 Génération de votre profil personnalisé")
        st.write("Utilisez l'IA pour analyser vos réponses et générer un profil d'apprentissage adapté.")

        if st.button("🚀 Générer mon profil avec l'IA", type="primary", use_container_width=True):
            with st.spinner("Lancement de l'analyse IA..."):
                # Appel à l'API pour analyser le quiz et générer le profil
                success, resp = make_request("POST", f"{PROFILE_PREFIX}/analyze_quiz", data=result, auth=True)

                if success and resp.get('task_id'):
                    st.session_state.profile_task_id = resp['task_id']
                    st.success("✅ Analyse lancée! L'IA analyse vos réponses...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"❌ Échec du lancement de l'analyse: {resp.get('detail', 'Erreur inconnue')}")

    # Vérification du statut de la tâche de génération de profil
    elif st.session_state.profile_task_id and not st.session_state.profile_result:
        st.subheader("⏳ Génération du profil en cours...")

        progress_bar = st.progress(0)
        status_text = st.empty()

        profile_data = check_profile_status(st.session_state.profile_task_id)

        if profile_data:
            status = str(profile_data.get('status', '')).lower()

            if status in ('success', 'succeeded'):
                progress_bar.progress(100)
                status_text.success("✅ Profil généré avec succès!")

                st.session_state.profile_result = profile_data.get('result', {})
                st.session_state.profile_task_id = None
                time.sleep(1)
                st.rerun()

            elif status in ('pending', 'started', 'received', 'retry'):
                progress_bar.progress(50)
                status_text.info(f"🔄 Analyse en cours... ({status})")
                time.sleep(3)
                st.rerun()

            elif status in ('failure', 'failed'):
                progress_bar.progress(0)
                status_text.error("❌ La génération du profil a échoué")

                if 'error' in profile_data:
                    st.error(f"Détail: {profile_data.get('error')}")

                if st.button("🔄 Réessayer"):
                    st.session_state.profile_task_id = None
                    st.rerun()
            else:
                progress_bar.progress(30)
                status_text.warning(f"⏳ Traitement en cours... Statut: {status}")
                time.sleep(3)
                st.rerun()
        else:
            st.warning("⏳ Vérification du statut...")
            time.sleep(3)
            st.rerun()

    # Affichage du profil généré
    elif st.session_state.profile_result:
        st.subheader("🎯 Votre Profil d'Apprentissage")

        profile = st.session_state.profile_result

        # Afficher le profil de manière structurée
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📊 Analyse")
            if 'analysis' in profile:
                analysis = profile['analysis']
                if isinstance(analysis, dict):
                    for key, value in analysis.items():
                        st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")
                else:
                    st.write(analysis)
            elif 'profile' in profile:
                st.json(profile['profile'])
            else:
                st.json(profile)

        with col2:
            st.markdown("### 🎯 Recommandations")
            if 'recommendations' in profile:
                for rec in profile['recommendations']:
                    st.markdown(f"- {rec}")
            elif 'next_steps' in profile:
                for step in profile['next_steps']:
                    st.markdown(f"- {step}")
            else:
                st.info("Aucune recommandation spécifique pour le moment.")

        st.divider()

        # Télécharger le profil
        profile_json = json.dumps(profile, indent=2, ensure_ascii=False)
        st.download_button(
            label="📥 Télécharger mon profil",
            data=profile_json,
            file_name=f"profil_{username}_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True
        )

        if st.button("🔄 Générer un nouveau profil", use_container_width=True):
            st.session_state.profile_result = None
            st.session_state.profile_task_id = None
            st.rerun()

    st.divider()

    # Détails de l'évaluation
    with st.expander("📋 Voir les détails de l'évaluation"):
        for item in result['questions_data']:
            status_icon = "✅" if item['is_correct'] is True else "❌" if item['is_correct'] is False else "⚠️"
            st.markdown(f"**{status_icon} Question {item['numero']}:** {item['question']}")
            st.markdown(f"**Votre réponse:** {item['user_answer'] or '_(Non répondu)_'}")
            st.markdown(f"**Réponse attendue:** {item['correct_answer']}")
            st.markdown("---")

    # Télécharger les résultats
    eval_json = json.dumps(result, indent=2, ensure_ascii=False)
    st.download_button(
        label="📥 Télécharger les résultats du questionnaire",
        data=eval_json,
        file_name=f"resultats_{username}_{datetime.now().strftime('%Y%m%d')}.json",
        mime="application/json"
    )

    if st.button("🔄 Recommencer un nouveau questionnaire", use_container_width=True):
        # Reset complet
        st.session_state.quiz_completed = False
        st.session_state.answers = {}
        st.session_state.current_question_index = 0
        st.session_state.evaluation_result = None
        st.session_state.questions = None
        st.session_state.question_task_id = None
        st.session_state.profile_task_id = None
        st.session_state.profile_result = None
        st.session_state.task_check_attempts = 0
        st.rerun()

    st.stop()

# ============================================================================
# SECTION GÉNÉRATION DU QUESTIONNAIRE
# ============================================================================

if not st.session_state.questions and not st.session_state.question_task_id:
    st.write("### 📋 Générer un questionnaire personnalisé")
    st.write("Cliquez sur le bouton ci-dessous pour que l'IA génère un questionnaire adapté à votre profil.")

    if st.button("✨ Générer mon questionnaire", type="primary", use_container_width=True):
        with st.spinner("🤖 L'IA prépare vos questions..."):
            success, response = make_request("GET", f"{PROFILE_PREFIX}/question", auth=True)

            if success and 'task_id' in response:
                st.session_state.question_task_id = response['task_id']
                st.session_state.task_check_attempts = 0
                st.success("✅ Génération lancée!")
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"❌ Erreur: {response.get('detail', 'Erreur inconnue')}")

    st.stop()

# ============================================================================
# VÉRIFICATION DU STATUT DE GÉNÉRATION DES QUESTIONS
# ============================================================================

if st.session_state.question_task_id and not st.session_state.questions:
    st.subheader("⏳ Génération des questions en cours...")

    # Calculer le temps écoulé
    if 'generation_start_time' not in st.session_state:
        st.session_state.generation_start_time = time.time()

    elapsed_time = int(time.time() - st.session_state.generation_start_time)

    progress_bar = st.progress(0)
    status_text = st.empty()
    time_text = st.empty()

    # Afficher le temps écoulé et estimé
    estimated_time = 90  # secondes
    time_text.info(f"⏱️ Temps écoulé: {elapsed_time}s / ~{estimated_time}s estimé")

    task_data = check_task_status(st.session_state.question_task_id)

    if task_data:
        status = str(task_data.get('status', '')).lower()

        if status in ('success', 'succeeded'):
            progress_bar.progress(100)
            status_text.success("✅ Questions générées!")

            result_data = task_data.get('result', {})
            parsed_list = parse_questions_payload(result_data)

            if isinstance(parsed_list, list) and len(parsed_list) > 0:
                st.session_state.questions = parsed_list
                st.session_state.question_task_id = None
                st.session_state.task_check_attempts = 0
                if 'generation_start_time' in st.session_state:
                    del st.session_state.generation_start_time
                st.success(f"✨ {len(parsed_list)} questions générées en {elapsed_time}s!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Impossible de récupérer les questions du serveur")
                st.info("💡 Le format de réponse du LLM n'est pas valide. Nouvelle tentative recommandée.")

                # Afficher les données brutes pour debug
                with st.expander("🔍 Données brutes (debug)"):
                    st.json(result_data)

                if st.button("🔄 Réessayer"):
                    st.session_state.question_task_id = None
                    st.session_state.task_check_attempts = 0
                    if 'generation_start_time' in st.session_state:
                        del st.session_state.generation_start_time
                    st.rerun()

        elif status in ('pending', 'started', 'received', 'retry'):
            # Calculer la progression basée sur le temps écoulé
            progress_value = min(int((elapsed_time / estimated_time) * 90), 90)
            progress_bar.progress(progress_value)

            if elapsed_time < 30:
                status_text.info("🤖 L'IA analyse votre profil et prépare les questions...")
            elif elapsed_time < 60:
                status_text.info("✍️ Génération des questions personnalisées en cours...")
            else:
                status_text.warning(f"⏳ Génération en cours (presque terminé)... ({status})")

            st.session_state.task_check_attempts += 1
            time.sleep(3)
            st.rerun()

        elif status in ('failure', 'failed'):
            progress_bar.progress(0)
            status_text.error("❌ La génération a échoué")

            if 'error' in task_data:
                st.error(f"Détail: {task_data.get('error')}")

            if st.button("🔄 Réessayer"):
                st.session_state.question_task_id = None
                st.session_state.task_check_attempts = 0
                st.rerun()
        else:
            progress_bar.progress(30)
            status_text.warning(f"⏳ Traitement... Statut: {status}")
            time.sleep(3)
            st.rerun()
    else:
        st.warning("⏳ Connexion au serveur...")
        time.sleep(3)
        st.rerun()

    st.stop()

# ============================================================================
# AFFICHAGE DES QUESTIONS ET COLLECTE DES RÉPONSES
# ============================================================================

if st.session_state.questions:
    questions_list = st.session_state.questions

    if not isinstance(questions_list, list) or len(questions_list) == 0:
        st.error("❌ Format de questions incorrect.")
        if st.button("🔄 Réessayer"):
            st.session_state.questions = None
            st.session_state.question_task_id = None
            st.rerun()
        st.stop()

    total_questions = len(questions_list)
    current_index = st.session_state.current_question_index

    # Barre de progression
    st.progress((current_index + 1) / total_questions)
    st.subheader(f"Question {current_index + 1}/{total_questions}")

    current_q = questions_list[current_index]
    question_text = current_q.get('question', 'Question non disponible')
    question_type = current_q.get('type', 'ChoixMultiple')
    question_key = f"q_{current_index}"

    # Afficher la question
    st.markdown(f"### {question_text}")
    st.divider()

    # Afficher le champ de réponse selon le type
    if question_type == "ChoixMultiple":
        options = current_q.get('options', [])
        if options:
            default_index = 0
            if question_key in st.session_state.answers:
                try:
                    default_index = options.index(st.session_state.answers[question_key])
                except (ValueError, IndexError):
                    default_index = 0

            user_answer = st.radio(
                "Sélectionnez votre réponse:",
                options,
                index=default_index,
                key=f"radio_{question_key}"
            )
            st.session_state.answers[question_key] = user_answer
        else:
            st.warning("Aucune option disponible pour cette question.")

    elif question_type == "VraiOuFaux":
        options = current_q.get('options', ["A. Vrai", "B. Faux"])
        default_index = 0
        if question_key in st.session_state.answers:
            try:
                default_index = options.index(st.session_state.answers[question_key])
            except (ValueError, IndexError):
                default_index = 0

        user_answer = st.radio(
            "Sélectionnez votre réponse:",
            options,
            index=default_index,
            key=f"radio_{question_key}"
        )
        st.session_state.answers[question_key] = user_answer

    elif question_type in ["QuestionOuverte", "ListeOuverte"]:
        if question_type == "ListeOuverte":
            st.info("💡 Conseil: Séparez vos réponses par des virgules")

        default_value = st.session_state.answers.get(question_key, "")
        user_answer = st.text_area(
            "Votre réponse:",
            value=default_value,
            height=120,
            key=f"textarea_{question_key}",
            placeholder="Écrivez votre réponse ici..."
        )
        if user_answer:
            st.session_state.answers[question_key] = user_answer

    st.divider()

    # Boutons de navigation
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if current_index > 0:
            if st.button("⬅️ Précédent", use_container_width=True):
                st.session_state.current_question_index -= 1
                st.rerun()

    with col2:
        # Afficher le nombre de réponses
        answered = len(st.session_state.answers)
        st.metric("Réponses", f"{answered}/{total_questions}")

    with col3:
        if current_index < total_questions - 1:
            if st.button("Suivant ➡️", use_container_width=True, type="primary"):
                st.session_state.current_question_index += 1
                st.rerun()
        else:
            if st.button("✅ Terminer", use_container_width=True, type="primary"):
                st.session_state.evaluation_result = generate_evaluation_result()
                st.session_state.quiz_completed = True
                st.rerun()

    # Résumé des réponses
    with st.expander("📊 Voir toutes mes réponses"):
        if len(st.session_state.answers) > 0:
            for i, q in enumerate(questions_list):
                q_key = f"q_{i}"
                if q_key in st.session_state.answers:
                    st.markdown(f"**Q{i + 1}:** {q.get('question', '')}  ")
                    st.markdown(f"**R:** {st.session_state.answers[q_key]}")
                    if i < len(questions_list) - 1:
                        st.markdown("---")
        else:
            st.info("Aucune réponse enregistrée pour le moment.")

