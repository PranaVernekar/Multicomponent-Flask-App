import shelve
from flask import g

# Open or create database
def pull_db():
    db_ = getattr(g, '_database', None)
    if db_ is None:
        db_ = g._database = shelve.open("storage")
    return db_

# Return all devices
def get():
    with pull_db() as shelf:
        devices_ = {}
        # populate dictionary with data from shelf
        for key in shelf:
            devices_[key] = shelf[key]
    return devices_


# Initial data
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

# Initialize shelve database
with shelve.open('storage') as db:
    for key, value in devices.items():
        db[key] = value