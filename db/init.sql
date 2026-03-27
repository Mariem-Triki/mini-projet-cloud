-- Création de la table des tâches
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertion de données de test
INSERT INTO tasks (title) VALUES 
    ('Apprendre Docker'),
    ('Configurer Docker Compose'),
    ('Créer l''API TODO'),
    ('Ajouter PostgreSQL'),
    ('Ajouter Redis'),
    ('Configurer Nginx'),
    ('Tester le load balancing')
ON CONFLICT DO NOTHING;