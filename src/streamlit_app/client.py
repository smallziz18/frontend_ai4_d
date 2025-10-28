import json
import requests
import streamlit as st

API_BASE_URL = "http://127.0.0.1:8000"
AUTH_PREFIX = "/api/auth/v1"
PROFILE_PREFIX = "/api/profile/v1"


def make_request(method: str, endpoint: str, data: dict | None = None, auth: bool = False) -> tuple[bool, dict]:
    url = f"{API_BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}

    token = st.session_state.get('access_token')
    if auth and token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        method_u = method.upper()
        if method_u == "GET":
            response = requests.get(url, headers=headers)
        elif method_u == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method_u == "PUT":
            response = requests.put(url, json=data, headers=headers)
        else:
            return False, {"error": "Method not supported"}

        try:
            json_response = response.json()
        except json.JSONDecodeError:
            json_response = {"content": response.text, "status_code": response.status_code}

        if isinstance(json_response, dict):
            json_response["status_code"] = response.status_code

        return response.status_code < 400, json_response

    except requests.exceptions.RequestException as e:
        error_details = {
            "error": str(e),
            "error_type": type(e).__name__,
            "url": url,
            "method": method,
            "headers": {k: v for k, v in headers.items() if k != "Authorization"},
        }
        if headers.get("Authorization"):
            error_details["auth"] = "Token présent"
        return False, error_details


def is_logged_in() -> bool:
    return st.session_state.get('access_token') is not None

