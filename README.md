# 🎓 AI-Edu Frontend

Application web de plateforme d'apprentissage personnalisée avec intelligence artificielle.

## 🚀 Stack Technologique

- **Framework** : Nuxt 4.1.2
- **UI Framework** : DaisyUI + Tailwind CSS
- **Langage** : TypeScript
- **Icons** : Nuxt Icon (Tabler Icons)
- **Backend API** : FastAPI (Python)
- **Base de données** : MongoDB

## 📋 Prérequis

- Node.js 18+
- npm ou yarn
- Backend FastAPI en cours d'exécution (http://127.0.0.1:8000)

## 🔧 Installation

### 1. Cloner le projet

```bash
git clone <repository-url>
cd ai4d_frontend
```

### 2. Installer les dépendances

```bash
npm install
```

### 3. Configurer les variables d'environnement

Copier le fichier `.env.example` en `.env` :

```bash
cp .env.example .env
```

Modifier `.env` avec vos valeurs :

```env
FAST_API_URL=http://127.0.0.1:8000
NODE_ENV=development
```

### 4. Démarrer le serveur de développement

```bash
npm run dev
```

L'application sera accessible sur [http://localhost:3000](http://localhost:3000)

## 📁 Structure du Projet

```
ai4d_frontend/
├── app/
│   ├── components/          # Composants réutilisables
│   │   ├── footer.vue
│   │   ├── landing-content.vue
│   │   └── nav-bar.vue
│   ├── data/                # Composables de données
│   │   └── use-auth.ts
│   ├── layouts/             # Layouts de pages
│   │   └── default.vue
│   └── pages/               # Pages de l'application
│       ├── index.vue        # Page d'accueil
│       ├── login.vue        # Connexion
│       ├── dashboard.vue    # Dashboard personnalisé
│       ├── questionnaire.vue # Questionnaire IA
│       ├── sign-up/         # Inscription
│       │   ├── index.vue
│       │   ├── etudiants.vue
│       │   └── professors.vue
│       └── verify/          # Vérification email
│           └── [token].vue
├── composables/             # Composables Nuxt
│   ├── use-auth.ts         # Authentification
│   ├── use-profile.ts      # Profil utilisateur
│   ├── use-questionnaire.ts # Questionnaire
│   └── use-signup.ts       # Inscription
├── middleware/              # Middleware de routes
│   └── auth.ts             # Protection des routes
├── lib/                     # Utilitaires
│   ├── env.ts
│   └── try-parse-env.ts
├── public/                  # Fichiers statiques
├── types/                   # Types TypeScript
│   └── user-type.ts
├── nuxt.config.ts          # Configuration Nuxt
├── tailwind.config.js      # Configuration Tailwind
└── FLUX_UTILISATEUR.md     # Documentation du flux utilisateur
```

## 🔐 Flux Utilisateur

Consultez [FLUX_UTILISATEUR.md](./FLUX_UTILISATEUR.md) pour une documentation complète du parcours utilisateur.

### Résumé Rapide

#### Pour un **nouvel utilisateur** :

1. **Inscription** (`/sign-up`) - Formulaire en 2 étapes (données de base uniquement)
   - Step 1 : Nom, prénom, username, email, mot de passe, type (Étudiant/Professeur)
   - Step 2 : Préférences (stockées localement, pas envoyées au backend)
2. **Vérification Email** - Clic sur le lien reçu par email
3. **Connexion** (`/login`) - Authentification
   - ✅ Frontend vérifie `hasProfile()` → retourne `false`
   - ➡️ Redirection automatique vers `/questionnaire`
4. **Questionnaire** (`/questionnaire`) - Diagnostic personnalisé (10 questions générées par IA)
   - Génération des questions (temps d'attente ~1-3 minutes)
   - Réponse aux questions
   - Soumission → Lance l'analyse IA
5. **Analyse IA** - Le backend crée le profil MongoDB + profil Étudiant/Professeur
6. **Dashboard** (`/dashboard`) - Interface personnalisée avec recommandations IA
   - Les recommandations peuvent prendre du temps (analyse en cours)
   - Bouton "Rafraîchir" disponible pour vérifier si l'analyse est terminée

#### Pour un **utilisateur existant** :

1. **Connexion** (`/login`) - Authentification
   - ✅ Frontend vérifie `hasProfile()` → retourne `true`
   - ➡️ Redirection automatique vers `/dashboard`
2. **Dashboard** (`/dashboard`) - Accès direct au profil et recommandations

## 🛠️ Scripts Disponibles

```bash
# Développement
npm run dev

# Build pour production
npm run build

# Prévisualiser la build de production
npm run preview

# Générer une version statique
npm run generate

# Analyse du code
npm run lint
```

## 🎨 Composables Principaux

### `useApi()`

Composable centralisé pour tous les appels API (respecte l'OpenAPI spec du backend) :

**Authentification :**

- `api.auth.signup(data)` - Inscription (données de base uniquement)
- `api.auth.login(email, password)` - Connexion
- `api.auth.logout()` - Déconnexion
- `api.auth.getCurrentUser()` - Informations utilisateur
- `api.auth.verifyEmail(token)` - Vérification email

**Profil :**

- `api.profile.getMyProfile()` - Récupérer profil (404 si n'existe pas)
- `api.profile.getRecommendations()` - Récupérer recommandations
- `api.profile.updateProfile(data)` - Mettre à jour profil

**Questionnaire :**

- `api.questionnaire.generateQuestions()` - Générer questions
- `api.questionnaire.getQuestionResult(taskId)` - Vérifier statut
- `api.questionnaire.analyzeQuiz(evaluation)` - Analyser + créer profil
- `api.questionnaire.getAnalysisResult(taskId)` - Vérifier statut analyse

**Gamification :**

- `api.gamification.getDashboard()` - Dashboard gamification
- `api.gamification.getMyBadges()` - Mes badges
- `api.gamification.getStreak()` - Série de jours

### `useAuth()`

Gestion de l'authentification :

- `login(email, password)` - Connexion + redirection intelligente
- `logout()` - Déconnexion
- `loadUserFromCookie()` - Charger utilisateur depuis cookie
- `isAuthenticated()` - Vérifier si connecté

### `useProfile()`

Gestion du profil utilisateur :

- `hasProfile()` - **Vérifier si l'utilisateur a un profil** (retourne `false` pour nouveaux utilisateurs)
- `fetchProfile()` - Récupérer profil
- `fetchRecommendations()` - Récupérer recommandations
- `analyzeQuiz(quizResult)` - Analyser résultats avec IA
- `checkProfileStatus(taskId)` - Vérifier statut analyse

### `useQuestionnaire()`

Gestion du questionnaire :

- `generateQuestionnaire()` - Générer questions avec IA
- `checkTaskStatus(taskId)` - Vérifier statut génération
- `submitQuestionnaire()` - Soumettre réponses + lancer analyse
- `resetQuestionnaire()` - Réinitialiser

### `useSignup()`

Gestion de l'inscription :

- `setBaseData(data, status)` - Enregistrer données de base
- `signupEtudiant(preferences)` - Inscription étudiant
- `signupProfesseur(preferences)` - Inscription professeur
- `clearSignupData()` - Nettoyer données temporaires

**Note :** Les préférences (compétences, spécialités, etc.) sont stockées localement et peuvent être utilisées pour enrichir l'expérience, mais ne sont PAS envoyées lors du signup.

## 🔌 API Endpoints

### Authentification

- `POST /api/auth/v1/signup` - Inscription (schéma `UtilisateurCreateBase` - données de base uniquement)
- `POST /api/auth/v1/login` - Connexion
- `GET /api/auth/v1/logout` - Déconnexion
- `GET /api/auth/v1/verify/{token}` - Vérification email
- `GET /api/auth/v1/me` - Informations utilisateur
- `GET /api/auth/v1/refresh_token` - Rafraîchir le token
- `POST /api/auth/v1/password_reset_request` - Demande reset mot de passe
- `POST /api/auth/v1/resend_verification` - Renvoyer email de vérification

### Profil & Questionnaire

- `GET /api/profile/v1/me` - Récupérer profil (404 si n'existe pas encore)
- `PUT /api/profile/v1/` - Mettre à jour profil
- `DELETE /api/profile/v1/` - Supprimer profil
- `GET /api/profile/v1/question` - Générer questionnaire (tâche asynchrone)
- `GET /api/profile/v1/question_result/{task_id}` - Statut génération questions
- `POST /api/profile/v1/analyze_quiz` - Analyser questionnaire + **créer profil si premier questionnaire**
- `GET /api/profile/v1/analysis_result/{task_id}` - Statut analyse
- `GET /api/profile/v1/recommendations` - Récupérer recommandations IA
- `GET /api/profile/v1/stats` - Statistiques du profil
- `POST /api/profile/v1/xp` - Ajouter de l'XP

### Gamification

- `GET /api/profile/v1/gamification/dashboard` - Dashboard complet
- `GET /api/profile/v1/gamification/my-badges` - Mes badges
- `GET /api/profile/v1/gamification/badges` - Badges disponibles
- `GET /api/profile/v1/gamification/streak` - Série de jours consécutifs
- `GET /api/profile/v1/gamification/progression` - Progression détaillée
- `GET /api/profile/v1/gamification/leaderboard-enriched` - Classement enrichi

### Activités

- `GET /api/profile/v1/activities` - Historique des activités
- `POST /api/profile/v1/activities` - Enregistrer une activité
- `GET /api/profile/v1/leaderboard` - Classement par XP

## 🍪 Cookies Utilisés

| Cookie             | Description                            | Durée     |
| ------------------ | -------------------------------------- | --------- |
| `access_token`     | Token JWT d'authentification           | 7 jours   |
| `refresh_token`    | Token de rafraîchissement              | 30 jours  |
| `user_data`        | Données utilisateur (nom, email, etc.) | 7 jours   |
| `analysis_task_id` | ID de la tâche d'analyse IA en cours   | 24 heures |

**Note :** Le cookie `questionnaire_completed` a été supprimé. La vérification se fait maintenant via l'existence du profil dans la base de données (`hasProfile()`).

## 🛡️ Middleware

### `auth.ts`

Protège les routes nécessitant une authentification :

- Vérifie la présence du token
- Redirige vers `/login` si non connecté

**La vérification du profil se fait dans les pages elles-mêmes** pour optimiser les performances :

- `/dashboard` → Vérifie `hasProfile()`, redirige vers `/questionnaire` si `false`
- `/questionnaire` → Accessible même si le profil existe (pour refaire le questionnaire)

**Usage** :

```typescript
definePageMeta({
  middleware: ["auth"]
});
```

## 🎨 Thème & Design

L'application utilise DaisyUI avec les thèmes :

- **Light** : Thème clair par défaut
- **Dark** : Thème sombre (auto-détection système)

Couleurs principales :

- **Primary** : Bleu (#3B82F6)
- **Secondary** : Violet (#8B5CF6)
- **Success** : Vert (#10B981)
- **Warning** : Orange (#F59E0B)
- **Error** : Rouge (#EF4444)

## 📦 Dépendances Principales

```json
{
  "nuxt": "^4.1.2",
  "@nuxtjs/tailwindcss": "^6.12.2",
  "daisyui": "^5.1.27",
  "@nuxt/icon": "^1.9.3",
  "zod": "^3.24.1"
}
```

## 🚧 Développement

### Ajouter une nouvelle page

1. Créer le fichier dans `app/pages/`
2. Ajouter le middleware si nécessaire
3. Utiliser les composables pour les données

```vue
<script setup lang="ts">
definePageMeta({
  middleware: ["auth"] // Si authentification requise
});

const { user } = useAuth();
</script>

<template>
  <div>
    <!-- Votre contenu -->
  </div>
</template>
```

### Ajouter un composable

1. Créer le fichier dans `composables/`
2. Exporter une fonction commençant par `use`

```typescript
export function useMyFeature() {
  const data = useState("myData", () => null);

  const fetchData = async () => {
    // Logique
  };

  return {
    data,
    fetchData
  };
}
```

## 🐛 Debugging

### Activer les DevTools Nuxt

Appuyez sur `Shift + Option + D` dans le navigateur

### Logs Serveur

Les logs du serveur s'affichent dans le terminal où `npm run dev` est lancé

### Vérifier les erreurs de compilation

```bash
npm run build
```

## 🧪 Test

Pour tester le flux complet utilisateur, consultez le [Guide de Test](./testing.md) qui détaille :

- Comment tester un nouvel utilisateur (profil créé après questionnaire)
- Comment tester un utilisateur existant (accès direct au dashboard)
- Points de vérification clés
- Résolution de problèmes

**Test rapide :**

```bash
# 1. Créer un nouveau compte
# 2. Vérifier email
# 3. Se connecter → Devrait rediriger vers /questionnaire
# 4. Compléter le questionnaire
# 5. Aller au dashboard → Profil créé et recommandations affichées
# 6. Se déconnecter et reconnecter → Devrait rediriger vers /dashboard
```

## 🐛 Débogage

Si vous rencontrez des problèmes avec la création du profil après le questionnaire, consultez le [Guide de Débogage](./debug-profil.md).

## 📝 TODO

- [ ] Intégration complète avec MongoDB
- [ ] Amélioration du dashboard (graphiques, statistiques)
- [ ] Système de cours et exercices
- [ ] Suivi des progrès dans le temps
- [ ] Badges et achievements
- [ ] Communauté et interactions
- [ ] Mode hors-ligne (PWA)
- [ ] Notifications push
- [ ] Export de données utilisateur

## 🤝 Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT.

## 📞 Support

Pour toute question ou problème, consultez la [documentation du flux utilisateur](./FLUX_UTILISATEUR.md) ou ouvrez une issue.

---

**Développé avec ❤️ pour l'éducation personnalisée par IA**
