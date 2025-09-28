from pymongo import MongoClient
from src.config import Config
import os

# Détecter l'environnement
DOCKER_ENV = os.getenv('DOCKER_ENV', 'false').lower() == 'true'

# Choisir le bon hôte selon l'environnement
mongo_host = Config.MONGO_HOST if DOCKER_ENV else 'localhost'

# Créer la chaîne de connexion
mongo_client = MongoClient(
    host=mongo_host,
    port=Config.MONGO_PORT,
    username=Config.MONGO_APP_USERNAME,
    password=Config.MONGO_APP_PASSWORD,
    authSource=Config.MONGO_DATABASE,
    serverSelectionTimeoutMS=5000
)

mongo_db = mongo_client[Config.MONGO_DATABASE]
