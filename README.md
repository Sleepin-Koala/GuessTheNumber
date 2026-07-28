# Readme Generé par IA


# 🎯 Plus-Minus — Guess the Number Game Suite

> Un jeu de devinette complet, cross‑platform (Web + Android), avec une esthétique cartoon dynamique, un système de progression, une boutique et des statistiques.

---

## 🧩 Description

**Plus-Minus** est un jeu où vous devez trouver un nombre mystère en un minimum d’essais. Il se décline en plusieurs modes (Découverte, Classique par niveaux, Duel à venir) et propose une expérience de jeu complète :

- **Système de progression** : niveaux, XP, pièces et gemmes.
- **Boutique** : achetez des power‑ups et des cosmétiques.
- **Statistiques** : suivez vos performances (taux de victoire, temps moyen, répartition des erreurs).
- **Interface cartoon** : couleurs vives, ombres épaisses, animations fluides — inspirée de jeux comme Subway Surfers, mais adaptée au PC (React) et au mobile (Flutter).

Ce projet est une démonstration d’architecture **full‑stack** modulaire, où la logique métier (backend) est isolée pour faciliter le portage entre plateformes.

---

## 🚀 Fonctionnalités principales

| Mode | Description |
|------|-------------|
| **Découverte** | Apprenez les règles pas à pas avec des indices. Essais illimités, pas de chrono. |
| **Classique** | Devinez le nombre dans un temps et un nombre d’essais limités. Progression à travers 100+ niveaux. |
| **Duel** *(à venir)* | Affrontez un autre joueur au tour par tour. |
| **Boutique** | Achetez des bonus (indice, +3 essais, multiplicateur) et des skins. |
| **Statistiques** | Visualisez votre taux de victoire, votre progression par niveau, la répartition de vos erreurs (trop haut / trop bas), et l’historique de vos parties. |

---

## 🛠️ Stack technique

### Backend (API REST)
- **Langage** : Python 3.10+
- **Framework** : FastAPI (ou Flask – adaptez selon votre choix)
- **Base de données** : SQLite / PostgreSQL (via SQLAlchemy)
- **Moteur de progression** : calcul de la difficulté, des récompenses (XP/pièces/gemmes) et des étoiles.
- **Authentification** : simple, basée sur un `player_id` stocké en local.

### Web (React)
- **Framework** : React 18 avec Vite
- **UI** : Tailwind CSS + Framer Motion (animations)
- **État** : useState / useEffect + Context API
- **Icônes** : react-icons (SVG)
- **Graphiques** : Recharts (pour les stats)

### Mobile (Flutter)
- **Framework** : Flutter 3.16+
- **État** : flutter_bloc (Cubit)
- **UI** : widgets personnalisés, dégradés, ombres cartoon
- **Icônes** : lucide_icons
- **Persistance** : SharedPreferences

---

## 🏗️ Architecture

```
plus-minus/
├── backend/                  # API Python
│   ├── app/
│   │   ├── models/           # SQLAlchemy / Peewee models
│   │   ├── routes/           # Endpoints REST
│   │   ├── services/         # Moteur de progression (SoloMode)
│   │   └── database.py       # Connexion DB
│   └── requirements.txt
│
├── web/                      # App React
│   ├── src/
│   │   ├── assets/           # Images, SVG, composants génériques
│   │   ├── components/       # UI réutilisables (cartes, overlays, etc.)
│   │   ├── pages/            # Menu, jeu, boutique, stats
│   │   ├── api/              # Appels HTTP vers le backend
│   │   └── hooks/            # Logique métier (useGame, useSound, etc.)
│   └── package.json
│
└── mobile/                   # App Flutter
    ├── lib/
    │   ├── core/             # Thèmes, widgets partagés
    │   ├── features/         # Pages organisées par domaine (menu, jeu, stats)
    │   ├── bloc/             # Gestion d'état (GameCubit)
    │   ├── data/             # DTOs, API client
    │   └── main.dart
    └── pubspec.yaml
```

---

## 💾 Modèle de données (Backend)

- **player** : id, name, level, xp, coins, gems, created_at
- **sessions** : id, player_id, type, max_attempt, attempt_left, number, status, started_time, end_time, time_limit
- **essais** : id, session_id, number, player_id
- **items** : id, name, price
- **hold** : playerId, itemId (inventaire)

---

## ⚙️ Installation et exécution

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sous Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

> Les variables d’environnement (ex: `DATABASE_URL`) sont à définir dans un fichier `.env`.

### 2. Web (React)

```bash
cd web
npm install
npm run dev
```

> L’application tourne sur `http://localhost:5173`. Assurez‑vous que le backend tourne sur `http://localhost:8000`.

### 3. Mobile (Flutter)

```bash
cd mobile
flutter pub get
flutter run
```

> Utilisez un émulateur Android ou un appareil physique connecté. Les appels API doivent cibler l’IP de votre machine (ex: `http://192.168.1.x:8000`). Configurez l’URL de base dans le client HTTP.

---

## 🔐 Variables d’environnement

**Backend (`.env`)** :
```
DATABASE_URL=sqlite:///./game.db
SECRET_KEY=your_secret_key
```

**Web (`.env.local`)** :
```
VITE_API_URL=http://localhost:8000
```

**Flutter** : définissez l’URL de base dans un fichier de configuration ou dans l’initialisation du client HTTP.

---

## 📈 Moteur de progression (SoloMode)

Le backend utilise une classe `SoloMode` qui calcule :

- **Difficulté** : `max_attempts = ceil(log2(level * 10))`
- **Temps max** : `max_time = max_attempts * 5` (secondes)
- **Score** : combinaison pondérée de :
  - Essais restants (poids 0.6)
  - Précision des essais (distance relative, poids 0.3)
  - Temps restant (poids 0.1)
- **Étoiles** : 1 étoile si score ≤ 0.3, 2 si ≤ 0.5, 3 sinon.
- **Récompenses** : pièces, XP et gemmes (1 gemme pour 3 étoiles).

Ces valeurs sont calibrées pour offrir une progression gratifiante sans inflation.

---

## 🎨 Règles de conception (UI/UX)

- **❌ Pas d’émojis natifs** : toutes les icônes sont des SVG (via `react-icons` ou `lucide_icons`).
- **✅ Style cartoon mais pas enfantin** : couleurs vives, ombres épaisses (`shadow-hard`), dégradés, bords arrondis.
- **✅ Animation** : transitions fluides avec Framer Motion (Web) et AnimationController (Flutter).
- **✅ Adaptation mobile** : grille 2 colonnes, gestes tactiles, focus automatique sur l’input.
- **✅ Accessibilité** : navigation au clavier (Web) et retour physique Android (Flutter).

---

## 📸 Captures d’écran

*À venir…*

---

## 🧪 Endpoints API principaux

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/user/new_player` | Crée un nouveau joueur |
| GET | `/user/{id}` | Récupère les infos du joueur |
| POST | `/user/rename` | Modifie le pseudo |
| POST | `/game/discover` | Crée une session mode Découverte |
| POST | `/game/classic` | Crée une session mode Classique (avec niveau) |
| POST | `/game/guess` | Soumet une proposition |
| POST | `/game/endlevel` | Termine une session (calcul des récompenses) |
| GET | `/user/stats/{id}` | Statistiques globales |
| GET | `/shop/items` | Liste des items disponibles |
| POST | `/shop/buy` | Achat d’un item |

---

## 🚧 Améliorations futures

- ✅ Mode Duel (multijoueur local ou en ligne)
- ✅ Système de défis quotidiens
- ✅ Skins et personnalisation avancée
- ✅ Classement mondial (leaderboard)
- ✅ Support iOS (Flutter)

---

## 📝 Licence

Ce projet est distribué sous licence MIT. Vous êtes libre de l’utiliser, de le modifier et de le distribuer.

---

## 🙏 Remerciements

- **Polices** : Bangers, Poppins
- **Icônes** : Lucide, Font Awesome
- **Inspiration graphique** : Subway Surfers, Crossy Road, Jetpack Joyride






---

*Construit avec passion, itération après itération.*  
**Game Designer / UIUX / Full‑stack** : un seul projet, trois plates‑formes.
