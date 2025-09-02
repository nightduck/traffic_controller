# Firmware

This folder contains the code that is deployed on our custom PCBs in each traffic fixture. It is a single file, `main.cpp`, but compilation relies on the PlatformIO extension for VSCode. It is highly recommended to use these two tools as your development environment.

## Behavior

The traffic controller in each light operates in a loop where it connects to and pings the "getLightState/" API call from the controlhub using the controller's unique ID. The API call returns the current state that the controller should be in, and for how long.

If a successful status code is returned (200), then that state is entered for the prescribed amount of time, which indicates which lights should turn on (as well as if any of them should be blinkding). The `enter_state` function is used to perform this action. After the prescribed time has elapsed, the loop begins again (without resetting the lights), and the controller queries the controlhub again.

If an error code 401 is returned, then the controlhub is unaware of the controller's ID. So a call to "register/" is made and the loop begins again.

If any other error is returned from "getLightState/", the "Connection error" state is entered for 5 seconds.

### States
All positive states are normal operating states. All negative states correspond to error codes

* 0 - Green light
* 1 - Green light, do-not-walk light is blinking
* 2 - Yellow light, do-not-walk light is solid 
* 3 - Red light, front facing and perpendicular do-not-walk lights are both on
* 4 - Red light, perpendicular pedestrian light turns white
* 5 - Red light, perpendicular pedestrian light starts blinking orange
* 6 - Same as state 3
* -1 - Connection error: indicates that the controller couldn't find the controlhub
* -2 - Unassigned: indicates that the controller has not been mapped to a location, and therefore isn't in operation
* -3 - Identify: used to indicate which traffic controller is selected in the web gui, in case it needs to be assigned or reassigned

## Debugging

A 6-pin SMD pin header is on the main traffic controller PCB. You can connect to this using the [ESP PROG](https://www.digikey.com/en/products/detail/espressif-systems/ESP-PROG/10259352). The controller is constantly outputting debug information over UART that you can read, in the event that a board is malfunctioning.