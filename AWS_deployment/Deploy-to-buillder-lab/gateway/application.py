import os

from flask import Flask, request, Response, jsonify
import requests

app = Flask(__name__)
INVSYS_BASE_URL = os.getenv("INVSYS_BASE_URL", "http://invsys:5000").rstrip("/")


@app.route("/")
def index():
    return 'Hello from Gateway!'


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "gateway"}), 200


@app.route('/items', methods=['GET'])
@app.route('/items/<string:item_id>', methods=['GET'])
def get_devices(item_id=None):
    # Forward the request to the relevant endpoint in invsys
    if item_id:
        response = requests.get(f'{INVSYS_BASE_URL}/items/{item_id}', timeout=5)
    else:
        response = requests.get(f'{INVSYS_BASE_URL}/items', timeout=5)

    # Forward the response back to the client
    # We create a Response object by deconstructing our response from above
    return Response(response.content, response.status_code)


@app.route('/items/<string:item_id>', methods=['DELETE'])
def delete_device(item_id):
    # Forward the delete request to the relevant endpoint in invsys
    response = requests.delete(f'{INVSYS_BASE_URL}/items/{item_id}', timeout=5)

    # Forward the response back to the client
    return Response(response.content, response.status_code)


@app.route('/items', methods=['POST'])
def post_device():
    # Get the payload from our incoming request
    payload = request.get_json(force=True)
    response = requests.post(f'{INVSYS_BASE_URL}/items', json=payload, timeout=5)

    # Forward the response back to the client
    return Response(response.content, response.status_code)


@app.route('/items/<string:item_id>', methods=['PUT'])
def put_device(item_id):
    # Get the payload from our incoming request
    payload = request.get_json(force=True)
    response = requests.put(f'{INVSYS_BASE_URL}/items/{item_id}', json=payload, timeout=5)

    # Forward the response back to the client
    return Response(response.content, response.status_code)


if __name__ == "__main__":
    app.run("0.0.0.0", port=5001, debug=False)
