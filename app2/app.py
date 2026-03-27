from flask import Flask, jsonify
from prometheus_flask_exporter import PrometheusMetrics
import redis

app = Flask(__name__)

# Ajouter les métriques Prometheus
metrics = PrometheusMetrics(app)

# Informations statiques sur l'application
metrics.info('app_info', 'Application info', version='1.0.0')

# Connexion à Redis
redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)

@app.route('/')
def home():
    return "Bienvenue sur App2 !"

@app.route('/visits', methods=['GET'])
def visits():
    count = redis_client.incr('visits_app2')
    return jsonify({"service": "app2", "visits": count})

@app.route('/info', methods=['GET'])
def info():
    return jsonify({
        "service": "app2",
        "version": "1.0",
        "description": "Deuxième microservice"
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "app2"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)