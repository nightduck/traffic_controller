# Flask app for web interface and REST api

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import uuid
import json

app = Flask(__name__)

ERROR_NOT_IMPLEMENTED = 501
ERROR_UNKNOWN_ID = 401      # ID not found in database, must request new ID with /getLightID
ERROR_NOT_FOUND = 404
STATUS_OK = 200

class LightState:
    RED = 0x1
    YELLOW = 0x2
    GREEN = 0x4
    DO_NOT_WALK_PERP = 0x10
    WALK_PERP = 0x20
    DO_NOT_WALK = 0x40
    WALK = 0x80
    
class Intersection:
    def __init__(self, id, north, south, east, west):
        self.id = id
        self.north = north
        self.south = south
        self.east = east
        self.west = west

@app.route('/')
def index():
    return 'Hello, World!'
    # TODO: Write main interface page

# # REST call to get unique light ID
# # Returns 500 if error accessing database
# @app.route('/getLightID', methods=['GET'])
# def getLightID():
#     # Generate new ID every time
#     id = uuid.uuid4()
    
#     # TODO: Store ID in database
    
#     return str(id)

# REST call to get list of all IDs
# Returns 500 if error accessing database
@app.route('/getLightIDs', methods=['GET'])
def getLightIDs():
    return 501

# REST call to remove ID from database
@app.route('/removeLightID', methods=['POST'])
def removeLightID():
    return 501

# REST call to get light state for all intersections
# Returns 500 if error accessing database
@app.route('/getLightState', methods=['GET'])
def getLightStateAll():
    # TODO: Get light state from database
    # TODO: Update state given timing information and time passed
    # TODO: Return simplified json with just state information
    
    # TODO: Calculate current state of all uuids and return list of json objects
    
    return 501

# REST call to get light state for specified ID
# Returns 401 if ID not found in database
@app.route('/getLightState/<uuid>', methods=['GET'])
def getLightState(id):
    # TODO: Get light state from database
    # TODO: Update state given timing information and time passed
    # TODO: Return simplified json with just state information, filtered by ID
    
    # Temp:
    # TODO: Calculate current state of uuid and return json object with info
    intersection = None
    traffic = None
    with open("traffic.json", "r") as json_file:
        traffic = json.load(json_file)
        intersection_id = traffic["lights"][id]["intersection_id"]
        intersection = traffic["intersections"][intersection_id]
        
    state_durations = [intersection["ns_green_ms"] - intersection["pedestrian_ms"], intersection["pedestrian_ms"], intersection["ns_yellow_ms"], intersection["all_red_ms"],
                       intersection["ew_green_ms"] - intersection["pedestrian_ms"], intersection["pedestrian_ms"], intersection["ew_yellow_ms"], intersection["all_red_ms"]]
    
    for i in range(1, len(state_durations)):
        state_durations[i] += state_durations[i-1]
        
    time = traffic["time"] % state_durations[-1]
    
    state = 0
    while time < state_durations[i]:
        state += 1
        
    if intersection["north_light"] == id or intersection["south_light"] == id:
        # TODO: Code logic to build light state object
        if state == 7:
            state = 6
    elif intersection["east_light"] == id or intersection["west_light"] == id:
        # TODO: Code logic to build light state object
        state += 4
        if state == 7:
            state = 6
    else:
        return ERROR_NOT_FOUND
    
    return jsonify({id: {"intersection_id": intersection_id, "state" : state, "remaining_ms": state_durations[state] - time}})


# # REST call to provide intersection and direction of light given ID
# # Returns 401 if ID not found in database
# # Returns 404 if ID not assigned to location
# @app.route('/getLightLocation/<uuid>', methods=['GET'])
# def getLightLocation(id):
#     return 501

# REST call to assign light ID to intersection
# Returns 401 if ID not found in database
@app.route('/setLightLocation/<uuid>', methods=['POST'])
def setLightLocation(id):
    return 501

# REST call to set timing information for intersection
@app.route('/setLightTiming/', methods=['POST'])
def setLightTiming():
    return 501

if __name__ == '__main__':
    app.run(debug=True)