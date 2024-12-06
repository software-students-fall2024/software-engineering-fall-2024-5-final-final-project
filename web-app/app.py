from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Function to get weather data
def get_weather(city_name, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        temperature = data['main']['temp']
        weather_description = data['weather'][0]['description']
        return temperature, weather_description
    else:
        return None, None

# API key for OpenWeatherMap
API_KEY = "your_openweathermap_api_key"

# Flask route to fetch weather data
@app.route('/get_weather', methods=['GET'])
def fetch_weather():
    city = request.args.get('city', 'New York')  # Default city is New York
    temperature, description = get_weather(city, API_KEY)
    if temperature is not None:
        return jsonify({
            "city": city,
            "temperature": f"{temperature}°C",
            "description": description
        })
    else:
        return jsonify({"error": "Could not fetch weather data"}), 400

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
