from flask import Flask, render_template, request
import requests

app = Flask(__name__)

API_KEY = "b74465fa14b2a546e3f99979274c5355"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# Función para calcular escorrentía
def calculate_runoff(precipitation, CN):
    if precipitation <= 0.2 * CN:
        return 0
    else:
        S = (1000 / CN) - 10
        runoff = ((precipitation - 0.2 * S) ** 2) / (precipitation + 0.8 * S)
        return round(runoff, 2)

@app.route("/", methods=["GET", "POST"])
def index():
    data = None
    error_message = None

    if request.method == "POST":
        city = request.form["city"]
        CN = float(request.form["cn"])

        # Obtener el clima
        params = {"q": city, "appid": API_KEY, "units": "metric"}
        response = requests.get(BASE_URL, params=params)

        if response.status_code == 200:
            weather_data = response.json()
            precipitation = weather_data.get("rain", {}).get("1h", 0)
            temperature = weather_data["main"]["temp"]
            humidity = weather_data["main"]["humidity"]
            weather_description = weather_data["weather"][0]["description"]
            weather_icon = weather_data["weather"][0]["icon"]  # Código de icono

            # Consultar advertencias meteorológicas
            alerts = weather_data.get("alerts", [])
            weather_alerts = []
            if alerts:
                for alert in alerts:
                    weather_alerts.append({
                        "event": alert["event"],
                        "description": alert["description"],
                        "start": alert["start"],
                        "end": alert["end"]
                    })

            runoff = calculate_runoff(precipitation, CN)
            data = {
                "city": city,
                "precipitation": precipitation,
                "runoff": runoff,
                "CN": CN,
                "temperature": temperature,
                "humidity": humidity,
                "weather_description": weather_description,
                "lat": weather_data["coord"]["lat"],
                "lon": weather_data["coord"]["lon"],
                "weather_alerts": weather_alerts,
                "weather_icon": weather_icon  # Agregamos el icono
            }
        else:
            error_message = "City not found. Please check the city name and try again."

    return render_template("index.html", data=data, error_message=error_message)

if __name__ == "__main__":
    app.run(debug=True)

