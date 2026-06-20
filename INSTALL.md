# Guide d'installation - Association Trésorerie

## Prérequis
- Python 3.8+
- PostgreSQL
- pip, virtualenv

## Installation locale

1. Cloner le projet
2. Créer un environnement virtuel :
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```
3. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
4. Configurer la base de données :
   - Créer une base nommée `dbaescttresoreire` dans PostgreSQL.
   - Copier `.env.example` vers `.env` et ajuster les valeurs.
5. Initialiser la base de données et les données par défaut :
   ```bash
   python seed.py
   ```
6. Lancer l'application :
   ```bash
   python manage.py
   ```

## Accès par défaut
- URL : `http://localhost:5000`
- Utilisateur : `admin`
- Mot de passe : `admin123`
