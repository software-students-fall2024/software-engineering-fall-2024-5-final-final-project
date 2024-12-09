import os
from flask import Flask, render_template, request, Response
import requests

app = Flask(__name__)
app.secret_key = "your-secret-key-here"


app.config['SESSION_COOKIE_NAME'] = 'frontend_session'

BACKEND_URL = os.environ.get("BACKEND_URL", "http://backend:5001")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/<path:path>", methods=["GET", "POST"])
def proxy_to_backend(path):
    try:
        backend_cookies = {}
        if 'session' in request.cookies:
            backend_cookies['session'] = request.cookies['session']

        # Forward the request method and data
        if request.method == "GET":
            resp = requests.get(
                f"{BACKEND_URL}/api/{path}",
                cookies=backend_cookies,
                allow_redirects=False
            )
        else:
            resp = requests.post(
                f"{BACKEND_URL}/api/{path}",
                json=request.get_json(),
                cookies=backend_cookies,
                allow_redirects=False
            )

        # Create a Flask response object with backend's response content and status
        response = Response(
            resp.content,
            status=resp.status_code,
            content_type=resp.headers.get("content-type", "application/json")
        )

        # Correctly forward all Set-Cookie headers
        for key, value in resp.headers.items():
            if key.lower() == 'set-cookie':
                response.headers.add('Set-Cookie', value)

        return response
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
