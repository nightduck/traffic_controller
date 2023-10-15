# Flask app for web interface and REST api

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import uuid

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

# REST call to get unique light ID
# Returns 500 if error accessing database
@app.route('/getLightID', methods=['GET'])
def getLightID():
    # Generate new ID every time
    id = uuid.uuid4()
    
    # TODO: Store ID in database
    
    return str(id)

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
    
    return 501

# REST call to get light state for specified ID
# Returns 401 if ID not found in database
@app.route('/getLightState/<uuid>', methods=['GET'])
def getLightState(id):
    # TODO: Get light state from database
    # TODO: Update state given timing information and time passed
    # TODO: Return simplified json with just state information, filtered by ID
    
    return 501

# REST call to provide intersection and direction of light given ID
# Returns 401 if ID not found in database
# Returns 404 if ID not assigned to location
@app.route('/getLightLocation/<uuid>', methods=['GET'])
def getLightLocation(id):
    return 501

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