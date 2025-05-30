# MelodIA : Générateur de musique assisté par IA

## Description

Ce projet contient deux services :

- **Backend** : service FastAPI qui enrichit les fichiers MIDI via un modèle IA et stocke un log dans une base PostgreSQL
- **Frontend** : application Streamlit qui permet d'enregistrer ou importer des audios, convertir en MIDI, et appeler le backend pour enrichissement

Les deux services partagent un volume de données commun. Une base PostgreSQL est déployée pour stocker les logs.

---

## Prérequis

### Pour Docker Compose
- Docker et Docker Compose installés sur ta machine

### Pour Kubernetes
- kubectl installé
- Un cluster Kubernetes fonctionnel
- kustomize installé (inclus dans kubectl récent)

---

## Structure des dossiers

```
.
├── backend/                # Code backend FastAPI et Dockerfile
├── frontend/               # Code frontend Streamlit et Dockerfile
├── data/                   # Volume partagé pour fichiers audio et MIDI
├── docker-compose.yml      # Configuration Docker Compose
├── *.yaml                  # Manifestes Kubernetes
└── README.md
```

---

## Lancer le projet avec Docker Compose

1. **Construire et lancer les services** :
   ```bash
   docker-compose up --build
   ```

2. **Accéder à l'application Streamlit (frontend)** :
   Ouvre un navigateur sur :
   ```
   http://localhost:8501
   ```

## Nettoyer le projet Docker Compose

Pour arrêter et supprimer les containers et volumes (attention, supprime aussi la base de données) :

```bash
docker-compose down -v
```

## Déployer sur Kubernetes

1. **Construire et pousser les images Docker vers un registre** :
   ```bash
   # Construire les images
   docker build -t "adiattara"/melodia-backend:latest ./backend
   docker build -t "adiattara"/melodia-frontend:latest ./frontend

   # Pousser les images vers le registre
   docker push "adiattara"/melodia-backend:latest
   docker push "adiattara"/melodia-frontend:latest
   ```

2. **Déployer l'application avec kustomize** :
   ```bash
   # Définir le registre d'images
   export REGISTRY="adiattara"

   # Appliquer les manifestes Kubernetes
   kubectl apply -k .
   ```

3. **Accéder à l'application** :
   ```bash
   # Obtenir l'adresse IP externe du service frontend
   kubectl get svc melodia-frontend -n melodia
   ```
   Ouvre un navigateur sur l'adresse IP externe sur le port 8501.

## Nettoyer le déploiement Kubernetes

Pour supprimer tous les ressources Kubernetes créées :

```bash
kubectl delete -k .
```

## Notes importantes

- Le backend utilise la variable d'environnement `DATABASE_URL` pour se connecter à PostgreSQL.
- Le frontend utilise la variable d'environnement `BACKEND_URL` pour se connecter au backend.
- Un volume persistant est utilisé pour stocker les fichiers audio et MIDI entre frontend et backend.
- Un volume persistant est utilisé pour stocker les données de la base PostgreSQL.
- Les secrets pour les mots de passe de la base de données sont stockés dans un Secret Kubernetes.
- Toutes les configurations sont stockées dans des ConfigMaps et Secrets pour faciliter la maintenance.
