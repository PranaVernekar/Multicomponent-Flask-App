import shelve

devices = {
    "001": {
        "id": "001",
        "name": "Light bulb",
        "location": "hall",
        "status": "off"
    },
    "002": {
        "id": "002",
        "name": "Humidity_sensor",
        "location": "bedroom",
        "status": "on"
    },
    "003": {
        "id": "003",
        "name": "Humidifier",
        "location": "bedroom",
        "status": "off"
    }
}

# Initialize db with some data already in it
with shelve.open('storage') as db:
    # Iterate over the dictionary and save each entry into the shelf
    for device_id, device_data in devices.items():
        db[device_id] = device_data

if __name__ == '__main__':
    # Verification: Re-opening the shelf to ensure data persisted
    with shelve.open('storage') as db:
        print("Current items in the shelf database:")
        for item in db.items():
            print(item)