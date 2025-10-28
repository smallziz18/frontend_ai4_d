import streamlit as st
import requests
import json

# Configuration de la page
st.set_page_config(
    page_title="AI4D Test App",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration de l'API
API_BASE_URL = "http://127.0.0.1:8000"
AUTH_PREFIX = "/api/auth/v1"
PROFILE_PREFIX = "/api/profile/v1"

# Session state initialization
if 'access_token' not in st.session_state:
    st.session_state.access_token = None
if 'user_info' not in st.session_state:
    st.session_state.user_info = {}

def make_request(method: str, endpoint: str, data: dict = None, auth: bool = False) -> tuple:
    """Effectue une requête HTTP vers l'API"""
    url = f"{API_BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}

    if auth and st.session_state.access_token:
        headers["Authorization"] = f"Bearer {st.session_state.access_token}"

    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, headers=headers)
        else:
            return False, {"error": "Method not supported"}

        # Tenter de parser la réponse JSON
        try:
            json_response = response.json()
        except json.JSONDecodeError:
            # Si la réponse n'est pas du JSON valide, utiliser le texte brut
            json_response = {"content": response.text, "status_code": response.status_code}

        # Ajouter le code de statut à la réponse pour faciliter le débogage
        if isinstance(json_response, dict):
            json_response["status_code"] = response.status_code

        return response.status_code < 400, json_response

    except requests.exceptions.RequestException as e:
        # Ajouter plus de détails sur l'erreur de requête
        error_details = {
            "error": str(e),
            "error_type": type(e).__name__,
            "url": url,
            "method": method,
            "headers": {k: v for k, v in headers.items() if k != "Authorization"}  # Ne pas inclure le token dans les logs
        }
        if headers.get("Authorization"):
            error_details["auth"] = "Token présent"

        return False, error_details


def is_logged_in() -> bool:
    """Vérifie si l'utilisateur est connecté"""
    return st.session_state.access_token is not None

def logout():
    """Déconnecte l'utilisateur"""
    st.session_state.access_token = None
    st.session_state.user_info = {}
    st.rerun()

# Page principale
st.title("🤖 AI4D Test App")

# Test de connexion à l'API
with st.expander("🔌 Tester la connexion à l'API"):
    if st.button("Test API"):
        try:
            response = requests.get(f"{API_BASE_URL}/api/health")
            if response.status_code == 200:
                st.success(f"✅ API accessible! Réponse: {response.json()}")
            else:
                st.error(f"❌ API inaccessible. Code: {response.status_code}")
        except Exception as e:
            st.error(f"❌ Erreur de connexion: {str(e)}")

# Formulaire de connexion simple
if not is_logged_in():
    st.subheader("🔐 Connexion")

    with st.form("login_form"):
        email = st.text_input("Email", "utilisateur@example.com")
        password = st.text_input("Mot de passe", type="password", value="password")
        submit = st.form_submit_button("Se connecter")

        if submit:
            login_data = {"email": email, "password": password}
            success, response = make_request("POST", f"{AUTH_PREFIX}/login", login_data)

            if success and "access_token" in response:
                st.session_state.access_token = response["access_token"]
                # Récupérer les infos utilisateur
                success, user_info = make_request("GET", f"{AUTH_PREFIX}/me", auth=True)
                if success and user_info:
                    st.session_state.user_info = user_info
                else:
                    st.session_state.user_info = {"username": "Utilisateur"}
                st.success("✅ Connexion réussie!")
                st.rerun()
            else:
                st.error(f"❌ Erreur de connexion: {response.get('detail', 'Identifiants invalides')}")
else:
    # Afficher les infos de l'utilisateur connecté
    username = st.session_state.user_info.get('username', 'Utilisateur')
    st.success(f"🙋 Connecté en tant que: {username}")

    if st.button("Se déconnecter", type="secondary"):
        logout()

    st.write("Allez à la page 'Questions' dans la barre latérale pour accéder au questionnaire.")
