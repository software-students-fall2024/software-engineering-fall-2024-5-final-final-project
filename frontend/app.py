"""
Defines routes for the frontend and gives entry point of the Flask application.
"""

import os
from flask import Flask, render_template, request, Response
import requests

app = Flask(__name__, template_folder="templates", static_folder="static")

app.secret_key = os.environ.get("SECRET_KEY", "your-secret-key-here")
BACKEND_URL = os.environ.get("BACKEND_URL", "http://backend:5001")

@app.route("/")
def index():
    """
    Render the home page of the application.
    """
    return render_template("index.html")


@app.route("/api/signup", methods=["POST"])
def signup():
    """
    Proxy the signup request to the backend.
    """
    try:
        data = request.get_json()
        resp = requests.post(
            f"{BACKEND_URL}/api/signup",
            json=data,
            cookies=request.cookies,
            timeout=5,
        )
        response = Response(
            resp.content,
            status=resp.status_code,
            content_type=resp.headers.get("content-type", "application/json")
        )

        if "set-cookie" in resp.headers:
            response.headers["set-cookie"] = resp.headers["set-cookie"]

        return response
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}, 500


@app.route("/api/<path:path>", methods=["GET", "POST"])
def proxy_to_backend(path):
    """
    Proxy API requests to the backend server for other routes.
    """
    try:
        if request.method == "GET":
            resp = requests.get(f"{BACKEND_URL}/api/{path}", cookies=request.cookies, timeout=5)
        else:
            resp = requests.post(
                f"{BACKEND_URL}/api/{path}",
                json=request.get_json(),
                cookies=request.cookies,
                timeout=5,
            )
        response = Response(
            resp.content,
            status=resp.status_code,
            content_type=resp.headers.get("content-type", "application/octet-stream"),
        )

        if "set-cookie" in resp.headers:
            response.headers["set-cookie"] = resp.headers["set-cookie"]

        return response
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}, 500
    
@app.route("/api/logout", methods=["POST"])
def logout():
    """
    Proxy the logout request to the backend without sending a JSON body.
    """
    try:
        resp = requests.post(
            f"{BACKEND_URL}/api/logout",
            cookies=request.cookies,
            timeout=5,
        )
        response = Response(
            resp.content,
            status=resp.status_code,
            content_type=resp.headers.get("content-type", "application/json")
        )

        if "set-cookie" in resp.headers:
            response.headers["set-cookie"] = resp.headers["set-cookie"]

        return response
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}, 500



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
