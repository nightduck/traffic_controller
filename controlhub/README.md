# Controlhub

This contains code for the webserver that runs on the main controlhub to govern all the traffic controllers, as well as providing a web interface to users.

It is structed as a flask server, where the `/` url serves the webpage, and all other urls act as REST API calls that return json data.

## Setup

The server script, `app.py` can be run standalone (useful for debugging), but when running in production, it's reccomended to install it as a server, using the `install_controlhub.sh` script.

    ./setup_pi.sh               # Configure the hotspot, if this is a new Pi
    python -m pip install -r requirements.txt   # First install prereqs
    ./install_controlhub.sh     # Install controlhub as server and set it to start on bootup

## Debugging

The current status of the server and a recent text dump of its logs can be found with the following command

    sudo systemctl status traffic_controller.service

The server can also be rebooted with

    sudo systemctl restart traffic_controller.service

To stop the server (for debugging purposes), use the following command

    sudo systemctl stop traffic_controller.service

Or, if you want to prevent the server from restarting on reboot, disable it

    sudo systemctl disable traffic_controller.service

## Webpage

All frontend code (html and javascript) is in `templates/index.html`. I've documented none of it because I hate frontend development. Consult the MiniCity Electronics Cheatsheet for instructions on how to use the webpage, and read the list of [API calls](#api-calls) below. That should be enough to figure it out.

## Backend

The current state of the system is set in a json file called `traffic.json`. An example is provided in this folder. It contains a light of intersections in the city, and a dictionary of known traffic controllers index by IDs.

### Intersection Object Keys

Each intersection object in `traffic.json` has the following keys, detailed below.

`name` - Name of the intersection. Rendered on the webpage
`north` - ID of the traffic controller that is north facing
`south` - ID of the traffic controller that is north facing
`east` - ID of the traffic controller that is east facing
`west` - ID of the traffic controller that is west facing
`id` - ID of the intersection. Will correspond to its index in the intersections list
`ns_green_ms` - How many milliseconds north/south traffic has the green light
`ew_green_ms` - How many milliseconds east/west traffic has the green light
`ns_yellow_ms` - How many milliseconds north/south traffic has the yellow light
`ew_yellow_ms` - How many milliseonds east/west traffic has the yellow light
`all_red_ms` - How many milliseconds all lights are set to red
`pedestrian_ms` - How many milliseconds a pedestrian light will be set white. Must be less than `ns_green_ms` and `ew_green_ms`.
`timing_offset_ms` - Timing offset to adjust all transitions. By default, this is zero, so all lights change in perfect sync. To get a green wave, set this to be positive number, such as the time to drive between two adjacent intersections.

There was originally a feature on the webpage planned that would allow you to adjust these numbers, but that was never completed. To adjust timings, the `traffic.json` file has to be editted manually.

### Light object keys

Each light object in `light_map` is indexed by its unique ID. The object itself contains the following keys

`intersection_id` - The id/index of the intersection to which this traffic controller belongs to
`direction` - set to "north", "south", "east", or "west", depending on the direction the traffic controller is facing
`state` - Which state the traffic is currently in. See the `README.md` in `src` for documentation on states
`remaining_ms` - Time remaining in this state. This variable is not regularly updated in the `traffic.json` file (if at all).


### API Calls

The rest of the calls in `app.py` are for the REST API and their behavior and usage are documented below.

`/setStreetLights` - This toggles the street lights by toggling a GPIO pin on the Pi that's connected to a relay switch. It's called when checking or unchecking the "Lights" checkbox on the webpage

`/getStreetLights` - This returns the current state of the street lights (where "True" is on and "False" is off) as a json string of the format: {"lights": boolVal}. This is used to initially configure the webpage

`/getLightIDs` - Returns lists all known traffic controller IDs categorized according to whether they are unassigned to a location, assigned, or in an indication state.

`/getIntersections` - Returns the content of `intersections` in `traffic.json` (just a list of all intersection objects)

`/removeLightID` - Unregisters a traffic light ID from the server. Takes the UUID as a string in the HTTP json request

`/setLightError` - Edits the `traffic.json` file so a particular traffic ID will have an error state. Takes a json object in the HTTP request field of the format: {"uuid" : uuid_string, "state" : state_int}

`/getLightState/<uuid>` - Computes up-to-date values for the `state` and `remaining_ms` parameters for the traffic controller corresponding to the UUID given in the URL. It returns a json object matching the format described above in [Light object keys](#light-object-keys).

`/register/<uuid>` - Registers a UUID with the controlhub

`/setLightLocation/<uuid>` - Assigns a traffic controller to an intersection. The intersection ID and traffic light direction are provided as json arguments in the HTTP request.