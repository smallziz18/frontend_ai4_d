#!/bin/bash

# Script de lancement pour l'application Streamlit AI4D Test

echo "🚀 Lancement de l'application de test AI4D"
echo "=========================================="

# Vérifier si Streamlit est installé
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit n'est pas installé"
    echo "💡 Installation des dépendances..."
    pip install -r requirements.txt
fi

# Vérifier si l'API FastAPI est accessible
echo "🔍 Vérification de l'API FastAPI..."
if curl -s http://127.0.0.1:8000 &> /dev/null; then
    echo "✅ API FastAPI accessible"
else
    echo "⚠️  API FastAPI non accessible sur http://127.0.0.1:8000"
    echo "💡 Assurez-vous que votre serveur FastAPI est démarré"
    echo "   Commande: fastapi dev src"
fi

echo ""
echo "🌐 Lancement de Streamlit sur http://localhost:8501"
echo "📱 L'application s'ouvrira automatiquement dans votre navigateur"
echo ""

# Lancer Streamlit
streamlit run main.py
