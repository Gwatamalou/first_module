import json
from wsgiref.simple_server import make_server

import requests


def app(environ, start_response):
    path = environ.get("PATH_INFO", "/")
    currency = path.strip("/")

    if not currency:
        currency = "USD"

    url = f"https://api.exchangerate-api.com/v4/latest/{currency}"

    try:
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()
        response_body = json.dumps(data).encode("utf-8")
        status = "200 OK"

    except requests.exceptions.HTTPError as e:
        error_data = {"error": str(e)}
        response_body = json.dumps(error_data).encode("utf-8")
        status = "500 Internal Server Error"

    start_response(status, [("Content-Type", "application/json")])
    return [response_body]


if __name__ == "__main__":
    port = 8000
    httpd = make_server("localhost", port, app)
    print(f"http://localhost:{port}")
    httpd.serve_forever()
