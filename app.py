import time
import requests
from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('hello.html')

# Déposez votre code à partir d'ici :
@app.route("/contact")
def contact():
    return render_template("contact.html")  
@app.get("/paris")
def api_paris():
    
    url = "https://api.open-meteo.com/v1/forecast?latitude=48.8566&longitude=2.3522&hourly=temperature_2m"
    response = requests.get(url)
    data = response.json()

    times = data.get("hourly", {}).get("time", [])
    temps = data.get("hourly", {}).get("temperature_2m", [])

    n = min(len(times), len(temps))
    result = [
        {"datetime": times[i], "temperature_c": temps[i]}
        for i in range(n)
    ]

    return jsonify(result)

@app.route("/rapport")
def mongraphique():
    return render_template("graphique.html")

@app.route("/histogramme")
def monhistogramme():
    return render_template("histogramme.html")

cache_telemetrie = {
    "donnees": None,
    "derniere_maj": 0
}

@app.get("/api/atelier")
def api_atelier():
    global cache_telemetrie
    
    # Temps actuel en secondes
    maintenant = time.time()
    
    # Si le cache contient des données et qu'elles ont moins de 60 secondes, on les renvoie directement
    if cache_telemetrie["donnees"] and (maintenant - cache_telemetrie["derniere_maj"] < 60):
        return jsonify(cache_telemetrie["donnees"])
        
    # Sinon, on effectue la requête vers l'API externe avec un timeout de 5 secondes
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=48.67&longitude=2.38&current=temperature_2m,relative_humidity_2m,wind_speed_10m"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        current = data.get("current", {})

        result = [
            ["Indicateur", "Valeur"],
            ["Temp (°C)", current.get("temperature_2m", 0)],
            ["Humidité (%)", current.get("relative_humidity_2m", 0)],
            ["Vent (km/h)", current.get("wind_speed_10m", 0)]
        ]

        # Enregistrement des nouvelles données en mémoire
        cache_telemetrie["donnees"] = result
        cache_telemetrie["derniere_maj"] = maintenant

        return jsonify(result)
        
    except requests.exceptions.RequestException as e:
        # En cas de problème de connexion à Open-Meteo, on renvoie une erreur HTTP 500
        return jsonify({"erreur": "Erreur de connexion a l'API metrologique", "details": str(e)}), 500

@app.route("/atelier")
def monatelier():
    return render_template("atelier.html")
# Ne rien mettre après ce commentaire
    
if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000, debug=True)
