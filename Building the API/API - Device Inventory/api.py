from flask import Flask, request, jsonify
from marshmallow import Schema, fields, validates_schema, ValidationError

app = Flask(__name__)

# Dictionary to mimic the database
devices = {
    "001": {"id": "001", "name": "Light bulb", "location": "hall", "status": "off"},
    "002": {"id": "002", "name": "Humidity sensor", "location": "bedroom", "status": "on"},
    "003": {"id": "003", "name": "Humidifier", "location": "bedroom", "status": "off"}
}

# ---------------- Schema ----------------
class DeviceSchema(Schema):
    id = fields.Str(required=True)
    name = fields.Str(required=True)
    location = fields.Str(required=True)
    status = fields.Str(required=True)

    @validates_schema
    def validate_required_fields(self, data, **kwargs):
        required_fields = ["id", "name", "location", "status"]
        errors = {}

        for field in required_fields:
            if field not in data:
                errors[field] = [f"{field} is required"]

        if errors:
            raise ValidationError(errors)

device_schema = DeviceSchema()
devices_schema = DeviceSchema(many=True)

# ---------------- Single Device Endpoint ----------------
@app.route('/items/<string:identifier>', methods=['GET', 'PUT', 'DELETE'])
def device(identifier):
    if request.method == 'GET':
        device = devices.get(identifier)
        if not device:
            return jsonify({'message': 'Device not found'}), 404
        return jsonify(device), 200

    elif request.method == 'PUT':
        try:
            args = device_schema.load(request.json, partial=True)
        except ValidationError as err:
            return jsonify(err.messages), 400

        if identifier not in devices:
            return jsonify({'message': 'Device not found'}), 404

        devices[identifier].update(args)
        return jsonify({"updated device": identifier}), 200

    elif request.method == 'DELETE':
        if identifier not in devices:
            return jsonify({'message': 'Device not found'}), 404

        del devices[identifier]
        return jsonify({'message': 'Device deleted'}), 200

# ---------------- Device Inventory Endpoint ----------------
@app.route('/items', methods=['GET', 'POST'])
def device_inventory():

    if request.method == 'GET':
        return jsonify({"items": devices}), 200

    elif request.method == 'POST':
        json_data = request.get_json()

        if not json_data:
            return jsonify({"message": "No input data provided"}), 400

        try:
            new_device = device_schema.load(json_data)
        except ValidationError as err:
            return jsonify(err.messages), 400

        # Check if ID already exists
        if new_device["id"] in devices:
            return jsonify({"message": "Device with this ID already exists"}), 400

        # Add new device
        devices[new_device["id"]] = new_device

        return jsonify({
            "Posted a device": new_device
        }), 201


if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)