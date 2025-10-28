from __future__ import annotations
from langchain_openai import ChatOpenAI
import langchain
from src.config import Config

langchain.verbose = False
langchain.debug = False
langchain.llm_cache = False


ANALYZE_PROMPT = """
Tu es un expert en analyse de compétences IA. Analyse en profondeur les résultats du quiz pour créer un profil d'apprentissage détaillé et personnalisé.

DONNÉES UTILISATEUR:
{user_json}

RÉSULTATS DU QUIZ:
{evaluation_json}

🎯 MISSION:
Analyse chaque réponse pour identifier:
1. Les forces et faiblesses spécifiques en IA
2. Les lacunes de connaissances précises
3. Le style d'apprentissage (conceptuel vs pratique)
4. Les domaines IA à prioriser
5. Le niveau de maturité en IA

📊 ANALYSE DÉTAILLÉE REQUISE:

A. NIVEAU (1-10):
- Calcule le niveau en fonction du score ET de la complexité des questions réussies
- Score 0-30%: niveau 1-3 (débutant)
- Score 30-50%: niveau 4-5 (intermédiaire bas)
- Score 50-70%: niveau 6-7 (intermédiaire)
- Score 70-85%: niveau 8-9 (avancé)
- Score 85-100%: niveau 10 (expert)

B. COMPÉTENCES (liste détaillée):
- Liste UNIQUEMENT les compétences IA démontrées dans les réponses correctes
- Sois spécifique: pas "IA" mais "Deep Learning", "CNN", "NLP", "Reinforcement Learning", etc.
- Identifie les sous-domaines maîtrisés
- Maximum 5-7 compétences spécifiques

C. OBJECTIFS (texte détaillé):
- Identifie les lacunes précises basées sur les erreurs
- Propose un parcours d'apprentissage progressif
- Mentionne les concepts IA à renforcer
- Sois concret et actionnable

D. MOTIVATION (analyse psychologique):
- Déduis la motivation du score et du profil utilisateur
- Est-ce orienté carrière, curiosité intellectuelle, projet spécifique?
- Adapte le ton (encourageant si score faible, challengeant si score élevé)

E. ENERGIE (1-10):
- Base-toi sur le taux de complétion et la qualité des réponses ouvertes
- Questions ouvertes remplies = énergie haute
- Questions ouvertes vides = énergie basse

F. PRÉFÉRENCES (objet détaillé):
- **themes**: Liste 3-5 thèmes IA précis basés sur les réponses correctes/incorrectes
  (ex: ["Réseaux de neurones", "Computer Vision", "Transfer Learning"])
- **type_de_questions**: Analyse quel type de questions a le mieux réussi
  (ChoixMultiple, VraiOuFaux, QuestionOuverte, ListeOuverte)
- **niveau_cible**: Définit le niveau à atteindre dans les 3 mois
  (debutant, intermediaire, avance, expert)
- **style_apprentissage**: Ajoute ce champ (theorique, pratique, mixte)
- **domaines_a_renforcer**: Liste 2-3 domaines IA où l'utilisateur a échoué
- **points_forts**: Liste 2-3 domaines IA où l'utilisateur a excellé

G. RECOMMANDATIONS (nouveau champ):
- Ajoute un champ "recommandations" avec 3-5 actions concrètes
- Exemple: "Approfondir les CNN avec un projet pratique", "Revoir les bases du backpropagation"

🚨 FORMAT JSON STRICT (AUCUN TEXTE AVANT/APRÈS):
{{
  "niveau": 7,
  "competences": ["Deep Learning", "Computer Vision", "Réseaux de neurones convolutifs"],
  "objectifs": "Renforcer la compréhension des architectures de réseaux de neurones récurrents (RNN, LSTM) et approfondir les concepts de NLP. Focus sur la pratique avec des projets concrets de classification de texte.",
  "motivation": "Forte motivation professionnelle avec un intérêt marqué pour les applications pratiques de l'IA. Cherche à acquérir des compétences immédiatement applicables en entreprise.",
  "energie": 7,
  "preferences": {{
    "themes": ["Natural Language Processing", "Transformers", "Sentiment Analysis"],
    "type_de_questions": "ChoixMultiple",
    "niveau_cible": "avance",
    "style_apprentissage": "mixte",
    "domaines_a_renforcer": ["Reinforcement Learning", "GANs"],
    "points_forts": ["Computer Vision", "CNN", "Transfer Learning"]
  }},
  "recommandations": [
    "Suivre un cours sur les Transformers (BERT, GPT) pour renforcer les bases en NLP",
    "Implémenter un projet de classification d'images avec PyTorch",
    "Revoir les concepts mathématiques derrière le gradient descent",
    "Explorer les applications du Reinforcement Learning avec des tutoriels pratiques"
  ],
  "analyse_detaillee": {{
    "taux_reussite_par_type": {{
      "ChoixMultiple": "80%",
      "VraiOuFaux": "100%",
      "QuestionOuverte": "50%",
      "ListeOuverte": "75%"
    }},
    "forces": [
      "Excellente compréhension des concepts fondamentaux de ML",
      "Maîtrise solide des architectures CNN",
      "Bonne connaissance des frameworks PyTorch/TensorFlow"
    ],
    "faiblesses": [
      "Lacunes sur les concepts avancés de NLP",
      "Besoin de renforcer la théorie mathématique",
      "Manque d'expérience en Reinforcement Learning"
    ]
  }}
}}

IMPORTANT:
- Sois PRÉCIS et PERSONNALISÉ basé sur les données réelles
- Ne génère PAS de profil générique
- Utilise les informations du quiz pour justifier chaque champ
- Si une question ouverte est vide, note-le dans l'énergie
- Si l'utilisateur a tout bon dans un domaine, mets-le dans points_forts

GÉNÈRE LE JSON MAINTENANT:
"""


def _niveau_from_score(score_percentage: float) -> int:
    try:
        pct = max(0.0, min(100.0, float(score_percentage)))
        # Map 0..100 -> 1..10
        bucket = int(pct // 10) + 1
        return max(1, min(10, bucket))
    except Exception:
        return 5


def analyze_profile_with_llm(user_json: str, evaluation_json: str, *, model: str = "granite4:latest", base_url: str = "http://192.168.1.2:11434") -> str:
    """Appelle l'LLM pour générer un profil JSON strict.
    Retourne une chaîne JSON (ou texte brut si le modèle ne respecte pas strictement le format)."""
    prompt = ANALYZE_PROMPT.format(user_json=user_json, evaluation_json=evaluation_json)

    # Utilisation correcte de ChatOpenAI avec la clé API
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=Config.OPENAI_API_KEY,
        temperature=0.3
    )
    response = llm.invoke(prompt)
    return response.content if hasattr(response, "content") else str(response)
