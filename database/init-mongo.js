// Script d'initialisation MongoDB
print('=== Début de l\'initialisation MongoDB ===');

// Variables d'environnement
const dbName = process.env.MONGO_DATABASE || 'ai4db_mongo';
const appUser = process.env.MONGO_APP_USERNAME || 'ai4db_user';
const appPassword = process.env.MONGO_APP_PASSWORD || 'ai4db_password';

print('Base de données cible: ' + dbName);
print('Utilisateur à créer: ' + appUser);

// Passer à la base de données cible
db = db.getSiblingDB(dbName);

try {
    // Créer l'utilisateur application
    db.createUser({
        user: appUser,
        pwd: appPassword,
        roles: [
            {
                role: 'readWrite',
                db: dbName
            },
            {
                role: 'dbAdmin',
                db: dbName
            }
        ]
    });

    print('✓ Utilisateur application créé avec succès: ' + appUser);

    // Créer une collection de test pour confirmer les permissions
    db.createCollection('test_collection');
    db.test_collection.insertOne({message: 'Initialisation réussie', timestamp: new Date()});

    print('✓ Collection de test créée');

    // Vérifier l'utilisateur
    const users = db.getUsers();
    print('✓ Nombre d\'utilisateurs dans la base: ' + users.length);

} catch (error) {
    print('❌ Erreur lors de l\'initialisation: ' + error);
}

print('=== Fin de l\'initialisation MongoDB ===');