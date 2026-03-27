from flask import Flask, request, jsonify
from prometheus_flask_exporter import PrometheusMetrics
import psycopg2
import redis
import json

app = Flask(__name__)

# Ajouter les métriques Prometheus
metrics = PrometheusMetrics(app)

# Informations statiques sur l'application
metrics.info('app_info', 'Application info', version='1.0.0')

# Connexion à PostgreSQL
def get_db_connection():
    conn = psycopg2.connect(
        host="db",
        database="tasks",
        user="admin",
        password="admin"
    )
    return conn

# Connexion à Redis
redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)

# Initialiser la base de données
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

init_db()

@app.route('/')
def home():
    return "Bienvenue sur l'API TODO (App1) !"

@app.route('/tasks', methods=['GET'])
def get_tasks():
    # Vérifier le cache Redis
    cached_tasks = redis_client.get('tasks')
    if cached_tasks:
        return jsonify(json.loads(cached_tasks))
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, title FROM tasks ORDER BY id')
    tasks = [{"id": row[0], "title": row[1]} for row in cur.fetchall()]
    cur.close()
    conn.close()
    
    # Mettre en cache pendant 10 secondes
    redis_client.setex('tasks', 10, json.dumps(tasks))
    return jsonify(tasks)

@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    title = data.get('title')
    
    if not title:
        return jsonify({"error": "Title required"}), 400
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO tasks (title) VALUES (%s) RETURNING id', (title,))
    task_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    
    # Invalider le cache
    redis_client.delete('tasks')
    
    return jsonify({"id": task_id, "title": title}), 201

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM tasks WHERE id = %s', (task_id,))
    conn.commit()
    cur.close()
    conn.close()
    
    # Invalider le cache
    redis_client.delete('tasks')
    
    return '', 204

@app.route('/visits', methods=['GET'])
def visits():
    # Compteur de visites avec Redis
    count = redis_client.incr('visits_app1')
    return jsonify({"service": "app1", "visits": count})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "app1"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)