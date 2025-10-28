"""Script de test pour vérifier la connexion à l'API OpenAI"""
from langchain_openai import ChatOpenAI
from src.config import Config
import sys

print("=" * 60)
print("TEST DE CONNEXION À L'API OPENAI")
print("=" * 60)

# Vérification de la clé
print(f"\n1. Vérification de la clé API:")
print(f"   - Longueur: {len(Config.OPENAI_API_KEY)} caractères")
print(f"   - Début: {Config.OPENAI_API_KEY[:15]}...")
print(f"   - Format attendu: sk-proj-... (164 chars)")

# Test de connexion
print(f"\n2. Test de connexion à OpenAI...")
try:
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=Config.OPENAI_API_KEY,
        temperature=0.3
    )
    print(f"   ✅ Client OpenAI créé avec succès")

    # Test d'appel simple
    print(f"\n3. Test d'appel API...")
    response = llm.invoke("Réponds simplement: OK")
    print(f"   ✅ Réponse reçue: {response.content}")

    print(f"\n" + "=" * 60)
    print("✅ TOUS LES TESTS SONT PASSÉS")
    print("=" * 60)
    sys.exit(0)

except Exception as e:
    print(f"   ❌ ERREUR: {type(e).__name__}")
    print(f"   Message: {str(e)}")
    print(f"\n" + "=" * 60)
    print("❌ ÉCHEC DES TESTS")
    print("=" * 60)
    print("\nSOLUTIONS POSSIBLES:")
    print("1. Vérifiez que votre clé API est valide sur https://platform.openai.com/api-keys")
    print("2. Générez une nouvelle clé si nécessaire")
    print("3. Vérifiez que vous avez des crédits sur votre compte OpenAI")
    print("4. Assurez-vous que la clé commence par 'sk-proj-' ou 'sk-'")
    sys.exit(1)

