// ESP8266 app that establishes connection to webserver and gets status from json file
// then sends commands over I2C

#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include <Wire.h>
#include <ArduinoJson.h>

#include "mapping.h"

#define SSID "ssid"
#define PASSWORD "password"
#define SERVER "http://192.168.0.1/"

String uuid = "";
int intersection_id = -1;
String intersection_location = "";

// Turn on built-in LED and spam the UART with a message every couple seconds
void set_error() {
    while (true) {
        Serial.println("Error");
        digitalWrite(LED_BUILTIN, HIGH);
        delay(1000);
        digitalWrite(LED_BUILTIN, LOW);
        delay(1000);
    }
}

void set_traffic_light(int addr, int state) {
  Wire.beginTransmission(addr);
  Wire.write(OUTPUT_REGISTER);
  Wire.write(state);
  Wire.endTransmission();
}

int enter_state(int led_mask, int blink_mask, int blink_duration, int state_duration, int interrupt_mask) {
    int time = 0;
    int interrupt_state = 0;
    
    // Do not blink
    if (blink_duration <= 0) {
        blink_duration = state_duration;
    }

    set_traffic_light(NE_CORNER_ADDR, led_mask);
    set_traffic_light(NW_CORNER_ADDR, led_mask);
    set_traffic_light(SW_CORNER_ADDR, led_mask);
    set_traffic_light(SE_CORNER_ADDR, led_mask);

    while(time < state_duration && !(interrupt_state & interrupt_mask)) {
        delay(100);
        time++;

        if (time % blink_duration == 0) {
            led_mask ^= blink_mask;
            set_traffic_light(NE_CORNER_ADDR, led_mask);
            set_traffic_light(NW_CORNER_ADDR, led_mask);
            set_traffic_light(SW_CORNER_ADDR, led_mask);
            set_traffic_light(SE_CORNER_ADDR, led_mask);
        }

        interrupt_state &= interrupt_mask;

        if (interrupt_state) {
            break;
        }
    }
    return interrupt_state;
}

void led_test() {
    enter_state(RED_LIGHT, 0, 0, 5, 0);
    enter_state(YELLOW_LIGHT, 0, 0, 5, 0);
    enter_state(GREEN_LIGHT, 0, 0, 5, 0);
    enter_state(DNW, 0, 0, 5, 0);
    enter_state(WALK, 0, 0, 5, 0);
    enter_state(DNW_PERP, 0, 0, 5, 0);
    enter_state(WALK_PERP, 0, 0, 5, 0);
}

void setup() {
    pinMode(LED_BUILTIN, OUTPUT);
    Serial.begin(115200);
    Wire.begin();
    WiFi.begin(SSID, PASSWORD);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("");
    Serial.println("WiFi connected");

    uint8_t buf[] = {0x00,    // Start at register 0
                     0x00,    // All outputs
                     0x00, 0x00, 0x00, 0x00,
                     0x00,    // Configuration: sequential operation, slew rate enabled
                     0x00,    // Pull up resistors (not relevant cause no inputs)
                     0x00, 0x00,
                     0x00,    // All LEDs start off
                     };

    Wire.beginTransmission(NE_CORNER_ADDR);
    Wire.write(buf, 11);
    Wire.endTransmission();
}

void loop() {
    led_test();

    // TODO: 

    // If uuid is not set, get it from the server from call to server at /getLightID
    if (strlen(uuid) == 0) {
        HTTPClient http;
        http.begin(SERVER + "getLightID")
        int httpCode = http.GET();
        if (httpCode > 0) {
            String payload = http.getString();
            Serial.println(payload);
            DynamicJsonDocument doc(1024);
            deserializeJson(doc, payload);
            uuid = doc["uuid"].as<String>();
            intersection_id = doc["intersection_id"].as<int>();
            intersection_location = doc["intersection_location"].as<String>();
        }
        delay(1000);
        return;
    }

    // If uuid is set, but location isn't known, get it from the server at /getLightLocation/<uuid>
    if(intersection_id == -1) {
        HTTPClient http;
        http.begin(SERVER + "getLightLocation/" + uuid);
        int httpCode = http.GET();
        if (httpCode > 0) {
            String payload = http.getString();
            Serial.println(payload);
            DynamicJsonDocument doc(1024);
            deserializeJson(doc, payload);
            intersection_id = doc["intersection_id"].as<int>();
            intersection_location = doc["intersection_location"].as<String>();
        }
        delay(1000);
        return;
    }

    // If uuid and location are known, get the state from the server at /getLightState/<uuid>
    HTTPClient http;
    http.begin(SERVER + "getLightState/" + uuid);
    int httpCode = http.GET();
    if (httpCode == 200) {
        String payload = http.getString();
        Serial.println(payload);
        DynamicJsonDocument doc(1024);
        deserializeJson(doc, payload);
        int state = doc["state"].as<int>();
        int state_duration = doc["state_duration"].as<int>();
        int blink_duration = doc["blink_duration"].as<int>();
        int interrupt_mask = doc["interrupt_mask"].as<int>();
        int interrupt_state = enter_state(state, 0, blink_duration, state_duration, interrupt_mask);
        if (interrupt_state & interrupt_mask) {
            http.begin(SERVER + "setLightState/" + uuid + "/" + interrupt_state);
            http.GET();
        }
    } else if (httpCode == 401) {
        // If the server returns 401, the light is not registered, so we need to register it
        uuid = "";
        intersection_id = -1;
        intersection_location = "";
    }
}