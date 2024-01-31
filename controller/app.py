# Flask app for web interface and REST api

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, Response
import uuid
import json
from time import monotonic
import os
import sys
import RPi.GPIO as GPIO

app = Flask(__name__)

ERROR_NOT_IMPLEMENTED = 501
ERROR_SERVER = 500
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
    return render_template('index.html')

# # REST call to get unique light ID
# # Returns 500 if error accessing database
# @app.route('/getLightID', methods=['GET'])
# def getLightID():
#     # Generate new ID every time
#     id = uuid.uuid4()
    
#     # TODO: Store ID in database
    
#     return str(id)

# REST call to set street lights
@app.route('/setStreetLights', methods=['POST'])
def setStreetLights():
  # Check if east and west variables are in request
  if "east" not in request.json or "west" not in request.json:
    return Response("Missing east or west", status=ERROR_SERVER)
  
  # Get east and west variables from request
  if(request.json["east"]) == "true":
    GPIO.output(18, GPIO.HIGH)
  else:
    GPIO.output(18, GPIO.LOW)
    
  if(request.json["west"]) == "true":
    GPIO.output(23, GPIO.HIGH)
  else:
    GPIO.output(23, GPIO.LOW)
    
  return Response("Success", status=STATUS_OK)

# REST call to get list of all IDs
# Returns 500 if error accessing database
# If successful, returns json object witth lists of format:
# unassigned: [ <uuid>, ... ],
# assigned: [ <uuid>, ... ]
@app.route('/getLightIDs', methods=['GET'])
def getLightIDs():
  unassigned = []
  assigned = []
  indicated = []
  with open(os.path.dirname(__file__) + "/traffic.json", "r") as json_file:
      traffic = json.load(json_file)
      for uuid in traffic["light_map"]:
          if traffic["light_map"][uuid]["intersection_id"] == -1:
              unassigned.append(uuid)
          else:
              assigned.append(uuid)
          if traffic["light_map"][uuid]["state"] == -1:
              indicated.append(uuid)
      
  return jsonify({"unassigned": unassigned, "assigned": assigned, "indicated": indicated})

# REST call to get list of all intersection names
# Returns 500 if error accessing database
# If successful, returns json object with list of format:
# [ <intersection_name>, ... ]
@app.route('/getIntersections', methods=['GET'])
def getIntersections():
  intersections = []
  with open(os.path.dirname(__file__) + "/traffic.json", "r") as json_file:
      traffic = json.load(json_file)
      for intersection in traffic["intersections"]:
          intersections.append(intersection["name"])
      
  return jsonify(intersections)

# REST call to remove ID from database
@app.route('/removeLightID', methods=['POST'])
def removeLightID():
    return Response("Not implemented", status=ERROR_NOT_IMPLEMENTED)

# REST call to get light state for all intersections
# Returns 500 if error accessing database
@app.route('/getLightState', methods=['GET'])
def getLightStateAll():
    # TODO: Get light state from database
    # TODO: Update state given timing information and time passed
    # TODO: Return simplified json with just state information
    
    # TODO: Calculate current state of all uuids and return list of json objects
    
    return Response("Not implemented", status=ERROR_NOT_IMPLEMENTED)
  
# REST call to set light into error state
# Returns 401 if ID not found in database
@app.route('/setLightError', methods=['POST'])
def setLightError():
    if "uuid" not in request.json:
        return Response("Missing uuid", status=ERROR_SERVER)
    
    with open(os.path.dirname(__file__) + "/traffic.json", "r") as json_file:
        traffic = json.load(json_file)
        
    # Find if there's another controller with state -1, and if so, set it to 0
    # Its true state will be updated on the next call to getLightState
    for other_uuid in traffic["light_map"]:
        if traffic["light_map"][other_uuid]["state"] == -1:
            traffic["light_map"][other_uuid]["state"] = 0
            
    # Check value of provided uuid
    uuid = request.json["uuid"]
    if uuid == "":
        return Response("Removed error state", status=STATUS_OK)
    if uuid not in traffic["light_map"]:
        return Response("ID not found in database", status=ERROR_UNKNOWN_ID)
          
    # Set state of provided uuid (if any) to -1
    traffic["light_map"][uuid]["state"] = -1
    traffic["light_map"][uuid]["remaining_ms"] = 5000
    with open(os.path.dirname(__file__) + "/traffic.json", "w") as json_file:
        json.dump(traffic, json_file, indent=2)
        
    return Response("Success", status=STATUS_OK)

# REST call to get light state for specified ID
# Returns 401 if ID not found in database
# Returns 500 if timestamp is invalid
# If valid, returns json object with state information of format:
# uuid: {
#   id: <uuid>,
#   intersection_id: <intersection_id>,
#   direction: <position>,
#   state: <state>,
#   remaining_ms: <remaining_ms>
# }
@app.route('/getLightState/<uuid>', methods=['GET'])
def getLightState(uuid):
    # Calculate current state of uuid and return json object with info
    intersection = None
    traffic = None
    with open(os.path.dirname(__file__) + "/traffic.json", "r") as json_file:
        traffic = json.load(json_file)
        if uuid not in traffic["light_map"]:
            return Response("ID not found in database", status=ERROR_UNKNOWN_ID)
        if traffic["light_map"][uuid]["state"] == -1 or traffic["light_map"][uuid]["intersection_id"] == -1:
            # If light is in error state, return json object as-is
            return jsonify(traffic["light_map"][uuid])
        intersection_id = traffic["light_map"][uuid]["intersection_id"]
        intersection = traffic["intersections"][intersection_id]
        
    state_durations = [intersection["ns_green_ms"] - intersection["pedestrian_ms"], intersection["pedestrian_ms"], intersection["ns_yellow_ms"], intersection["all_red_ms"],
                       intersection["ew_green_ms"] - intersection["pedestrian_ms"], intersection["pedestrian_ms"], intersection["ew_yellow_ms"], intersection["all_red_ms"]]
    
    for i in range(1, len(state_durations)):
        state_durations[i] += state_durations[i-1]
        
    time = (monotonic() * 1000 - intersection["timing_offset_ms"]) % state_durations[-1]
    
    state = 0
    while time >= state_durations[state]:
        state += 1
        
    if intersection["north"] == uuid:
        position = "north"
        reported_state = state
    elif intersection["south"] == uuid:
        position = "south"
        reported_state = state
    elif intersection["east"] == uuid:
        position = "east"
        reported_state = (state + 4) % 8
    elif intersection["west"] == uuid:
        position = "west"
        reported_state = (state + 4) % 8
    else:
        return Response("ID not found in database", status=ERROR_UNKNOWN_ID)
      
    if reported_state == 7:
      reported_state = 6
    
    return jsonify({"id": uuid, "intersection_id": intersection_id, "direction" : position, "state" : reported_state, "remaining_ms": state_durations[state] - time})
    # TODO: Update json file with new state and duration data
    #return Response(result, status=STATUS_OK, mimetype='application/json')

# REST call to assign light ID to intersection
# Returns 401 if ID not found in database
@app.route('/setLightLocation/<uuid>', methods=['POST'])
def setLightLocation(uuid):
    if "intersection_id" not in request.json:
        return Response("Missing intersection_id", status=ERROR_SERVER)
    if "direction" not in request.json:
        return Response("Missing direction", status=ERROR_SERVER)
    intersection_id = request.json["intersection_id"]
    direction = request.json["direction"]
    
    with open(os.path.dirname(__file__) + "/traffic.json", "r") as json_file:
        traffic = json.load(json_file)
        
    # Lookup intersection to see if existing controller has been assigned to this location
    intersection = traffic["intersections"][intersection_id]
    
    # If so, lookup that controller and reset it to unassigned
    old_controller_uuid = intersection[direction]
    if old_controller_uuid != "":
        old_controller = traffic["light_map"][old_controller_uuid]
        old_controller["intersection_id"] = -1
        old_controller["state"] = 0
        old_controller["remaining_ms"] = 5000
        old_controller["direction"] = "none"
        traffic["light_map"][old_controller_uuid] = old_controller  # Update json
        
    # In either case, assign this controller to the location
    intersection[direction] = uuid
    traffic["intersections"][intersection_id] = intersection
    
    # Update light_map
    controller = traffic["light_map"][uuid]
    controller["intersection_id"] = intersection_id
    controller["direction"] = direction
    controller["state"] = 0
    controller["remaining_ms"] = 1000
    traffic["light_map"][uuid] = controller
        
    with open(os.path.dirname(__file__) + "/traffic.json", "w") as json_file:
        json.dump(traffic, json_file, indent=2)
        
    return Response("Success", status=STATUS_OK)

# REST call to set timing information for intersection
@app.route('/setLightTiming/', methods=['POST'])
def setLightTiming():
    return Response("Not implemented", status=ERROR_NOT_IMPLEMENTED)

if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(18, GPIO.OUT)
    GPIO.setup(23, GPIO.OUT)
    app.run(host='0.0.0.0', port=5000)
    GPIO.cleanup()