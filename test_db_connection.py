import sys
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

def test_connection():
    db_url = os.environ.get('DATABASE_URL')
    
    if not db_url:
        print("ERREUR : DATABASE_URL n'est pas définie dans le fichier .env")
        return False
    
    print(f"Tentative de connexion à : {db_url.split('@')[-1]} (masqué)")
    
    try:
        # Create engine
        engine = create_engine(db_url)
        
        # Attempt to connect and execute a simple query
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            version = result.fetchone()
            print("\n✅ CONNEXION RÉUSSIE !")
            print(f"Version PostgreSQL : {version[0]}")
            
            # Check if database dbaescttresoreire is the one we are connected to
            result = connection.execute(text("SELECT current_database();"))
            db_name = result.fetchone()
            print(f"Base de données actuelle : {db_name[0]}")
            
            if db_name[0] == 'dbaescttresoreire':
                print("✅ Le nom de la base de données est correct.")
            else:
                print(f"⚠️ Attention : Connecté à '{db_name[0]}' au lieu de 'dbaescttresoreire'.")
                
        return True
    except Exception as e:
        print("\n❌ ÉCHEC DE LA CONNEXION")
        print(f"Erreur : {str(e)}")
        print("\nVérifiez :")
        print("1. Que PostgreSQL est lancé.")
        print("2. Que l'utilisateur et le mot de passe dans .env sont corrects.")
        print("3. Que la base de données 'dbaescttresoreire' existe.")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
