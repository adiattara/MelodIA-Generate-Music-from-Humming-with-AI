# MelodIA : Générateur de musique assisté par IA

## Description

Ce projet contient deux services Dockerized :

- **Backend** : service FastAPI qui enrichit les fichiers MIDI via un modèle IA et stocke un log dans une base PostgreSQL
- **Frontend** : application Streamlit qui permet d'enregistrer ou importer des audios, convertir en MIDI, et appeler le backend pour enrichissement

Les deux services partagent un volume de données commun (`./data`). Une base PostgreSQL est déployée pour stocker les logs.

---

## Prérequis

- Docker et Docker Compose installés sur ta machine
- Fichier `.env` à la racine du projet (un exemple est fourni)


---

## Structure des dossiers

```
.
├── backend/                # Code backend FastAPI et Dockerfile
├── frontend/               # Code frontend Streamlit et Dockerfile
├── data/                   # Volume partagé pour fichiers audio et MIDI
├── .env                    # Variables d'environnement pour la configuration
├── docker-compose.yml
└── README.md
```

---

## Lancer le projet

1. **Configurer les variables d'environnement** :
   Assurez-vous que le fichier `.env` existe à la racine du projet et contient les variables nécessaires (voir section Configuration).

2. **Construire et lancer les services** :
   ```bash
   docker-compose up --build
   ```

3. **Accéder à l'application Streamlit (frontend)** :
   Ouvre un navigateur sur :
   ```
   http://localhost:8501
   ```

## Nettoyer le projet

Pour arrêter et supprimer les containers et volumes (attention, supprime aussi la base de données) :

```bash
docker-compose down -v
```

## Notes importantes

- Les variables d'environnement pour la base de données sont définies dans le fichier `.env` à la racine du projet.
- Le backend utilise la variable d'environnement `DATABASE_URL` pour se connecter à PostgreSQL.
- Le volume `data/` est partagé pour stocker les fichiers audio et MIDI entre frontend et backend.
- Le volume Docker nommé `pgdata` stocke les données persistantes de la base PostgreSQL.

## Configuration (.env)

Le fichier `.env` contient les variables d'environnement suivantes :
```
# Configuration de la base de données
POSTGRES_USER=postgres         # Utilisateur PostgreSQL
POSTGRES_PASSWORD=password     # Mot de passe PostgreSQL
POSTGRES_DB=melodia_db         # Nom de la base de données
DATABASE_URL=...               # URL de connexion à la base de données

# Configuration de l'API
API_URL=http://backend:8000/enrich_midi/  # URL du service API backend

# Configuration du modèle IA
MODEL_NAME=skytnt/midi-model-tv2o-medium  # Nom du modèle Hugging Face
MODEL_MAX_LEN=512                         # Longueur maximale de génération
MODEL_TEMP=0.90                           # Température pour la génération
MODEL_TOP_P=0.98                          # Paramètre top_p pour la génération
MODEL_TOP_K=20                            # Paramètre top_k pour la génération
```
Vous pouvez modifier ces valeurs selon vos besoins avant de lancer le projet. Les valeurs par défaut sont configurées pour fonctionner avec l'installation standard.
