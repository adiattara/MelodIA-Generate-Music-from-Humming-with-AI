# MelodIA : Générateur de musique assisté par IA

## Description

Ce projet contient deux services Dockerized :

- **Backend** : service FastAPI qui enrichit les fichiers MIDI via un modèle IA et stocke un log dans une base PostgreSQL
- **Frontend** : application Streamlit qui permet d'enregistrer ou importer des audios, convertir en MIDI, et appeler le backend pour enrichissement

Les deux services partagent un volume de données commun (`./data`). Une base PostgreSQL est déployée pour stocker les logs.

---

## Prérequis

- Docker et Docker Compose installés sur ta machine


---

## Structure des dossiers

```
.
├── backend/                # Code backend FastAPI et Dockerfile
├── frontend/               # Code frontend Streamlit et Dockerfile
├── data/                   # Volume partagé pour fichiers audio et MIDI
├── docker-compose.yml
└── README.md
```

---

## Lancer le projet

1. **Construire et lancer les services** :
   ```bash
   docker-compose up --build
   ```

2. **Accéder à l'application Streamlit (frontend)** :
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

- Le backend utilise la variable d'environnement `DATABASE_URL` pour se connecter à PostgreSQL avec l'utilisateur `postgres` et mot de passe `password`.
- Le volume `data/` est partagé pour stocker les fichiers audio et MIDI entre frontend et backend.
- Le volume Docker nommé `pgdata` stocke les données persistantes de la base PostgreSQL.


