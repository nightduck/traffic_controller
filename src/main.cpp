// ESP8266 app that establishes connection to webserver and gets status from json file
// then sends commands over I2C

#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include <Wire.h>
#include <ArduinoJson.h>
#include <EEPROM.h>
#include <Adafruit_NeoPixel.h>

#include "mapping.h"

#define SSID "MiniCity"
#define PASSWORD "mckelvey"
#define SERVER "http://10.42.0.1:5000/"

#define EEPROM_SIZE 512

#define AUTO_LED_PIN 12
#define AUTO_LED_COUNT 6
#define PED_LED_PIN 13
#define PED_LED_COUNT 4

//#define FACTORY_RESET

String uuid = "";
int intersection_id = -1;
String intersection_location = "";

Adafruit_NeoPixel auto_lights(AUTO_LED_COUNT, AUTO_LED_PIN, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel ped_lights(PED_LED_COUNT, PED_LED_PIN, NEO_GRB + NEO_KHZ800);

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

  Serial.print("0x");
  Serial.println(state, HEX);
}


void set_traffic_lights(int led_mask) {
  if (led_mask & RED_LIGHT) {
    auto_lights.setPixelColor(0, 0xFF0000); // Red
    auto_lights.setPixelColor(3, 0xFF0000);
  }
  if (led_mask & YELLOW_LIGHT) {
    auto_lights.setPixelColor(1, 0xFFFF00); // Yellow
    auto_lights.setPixelColor(4, 0xFFFF00);
  }
  if (led_mask & GREEN_LIGHT) {
    auto_lights.setPixelColor(2, 0x00FF00); // Green
    auto_lights.setPixelColor(5, 0x00FF00);
  }
  if (led_mask & DNW) {
    ped_lights.setPixelColor(0, 0xFFA500);  // Orange
  }
  if (led_mask & WALK) {
    ped_lights.setPixelColor(1, 0xAAAAA);   // White
  }
  if (led_mask & DNW_PERP) {
    ped_lights.setPixelColor(2, 0xFFA500);  // Orange
  }
  if (led_mask & WALK_PERP) {
    ped_lights.setPixelColor(3, 0xAAAAA);   // White
  }
  Serial.print("0x");
  Serial.println(led_mask, HEX);
}

// int enter_state(int led_mask, int blink_mask, int blink_duration, int state_duration, int interrupt_mask) {
//     int time = 0;
//     int interrupt_state = 0;
    
//     // Do not blink
//     if (blink_duration <= 0) {
//         blink_duration = state_duration;
//     }

//     set_traffic_light(NE_CORNER_ADDR, led_mask);
//     set_traffic_light(NW_CORNER_ADDR, led_mask);
//     set_traffic_light(SW_CORNER_ADDR, led_mask);
//     set_traffic_light(SE_CORNER_ADDR, led_mask);

//     while(time < state_duration && !(interrupt_state & interrupt_mask)) {
//         delay(100);
//         time++;

//         if (time % blink_duration == 0) {
//             led_mask ^= blink_mask;
//             set_traffic_light(NE_CORNER_ADDR, led_mask);
//             set_traffic_light(NW_CORNER_ADDR, led_mask);
//             set_traffic_light(SW_CORNER_ADDR, led_mask);
//             set_traffic_light(SE_CORNER_ADDR, led_mask);
//         }

//         interrupt_state &= interrupt_mask;

//         if (interrupt_state) {
//             break;
//         }
//     }
//     return interrupt_state;
// }

int enter_state(int state, int duration_ms, int interrupt_mask) {
  Serial.println("Entering state " + String(state) + " for " + String(duration_ms) + "ms");
  int led_mask, blink_mask, time = 0, interrupt_state = 0;
  switch(state) {
    case 0:
      led_mask = GREEN_LIGHT | WALK | DNW_PERP;
      blink_mask = 0;
      break;
    case 1:
      led_mask = GREEN_LIGHT | DNW | DNW_PERP;
      blink_mask = DNW;
      break;
    case 2:
      led_mask = YELLOW_LIGHT | DNW | DNW_PERP;
      blink_mask = 0;
      break;
    case 3:
      led_mask = RED_LIGHT | DNW | DNW_PERP;
      blink_mask = 0;
      break;
    case 4:
      led_mask = RED_LIGHT | DNW | WALK_PERP;
      blink_mask = 0;
      break;
    case 5: 
      led_mask = RED_LIGHT | DNW | DNW_PERP;
      blink_mask = DNW_PERP;
      break;
    case 6:
      led_mask = RED_LIGHT | DNW | DNW_PERP;
      blink_mask = 0;
      break;
    default:
      led_mask = RED_LIGHT | WALK; // Impossible state
      blink_mask = RED_LIGHT;
      break;
  }

  set_traffic_lights(led_mask);

  while(time < duration_ms && !(interrupt_state & interrupt_mask)) {
    delay(100);
    time+=100;

    if (time % 800 == 0) {
      led_mask ^= blink_mask;
      set_traffic_lights(led_mask);
    }
  }

  return interrupt_state;
}

// Defunct due to API change
// void led_test() {
//     enter_state(RED_LIGHT, 5, 0);
//     enter_state(YELLOW_LIGHT, 5, 0);
//     enter_state(GREEN_LIGHT, 5, 0);
//     enter_state(DNW, 5, 0);
//     enter_state(WALK, 5, 0);
//     enter_state(DNW_PERP, 5, 0);
//     enter_state(WALK_PERP, 5, 0);
// }

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

    auto_lights.begin();
    ped_lights.begin();

    EEPROM.begin(EEPROM_SIZE);
    
    // If fresh device, generate a uuid
    #ifndef FACTORY_RESET
    if (EEPROM.read(0) == 0x01) {
      Serial.println("Reading UUID");
      char c;
      int i = 1;
      while ((c = EEPROM.read(i++)) != 0) {
        uuid += c;
      }
    } else
    #endif
    {
      Serial.println("Generating UUID");
      uuid = "";
      for (int i = 0; i < 8; i++) {
        uuid += String(random(16), HEX);
      }
      uuid += "-";
      for (int i = 0; i < 3; i++) {
        for (int i = 0; i < 4; i++) {
          uuid += String(random(16), HEX);
        }
        uuid += "-";
      }
      for (int i = 0; i < 12; i++) {
        uuid += String(random(16), HEX);
      }
      EEPROM.write(0, 0x01);
      for (int i = 0; i < uuid.length(); i++) {
        EEPROM.write(i + 1, uuid[i]);
      }
      EEPROM.write(uuid.length() + 1, 0x00);
      EEPROM.commit();
    }

    Serial.println(uuid);
}

void loop() {
    // led_test();

    // If uuid and location are known, get the state from the server at /getLightState/<uuid>
    HTTPClient http;
    WiFiClient wifi;
    http.begin(wifi, String(SERVER) + "getLightState/" + uuid);
    int httpCode = http.GET();
    Serial.println("Got code" + String(httpCode));
    if (httpCode == 200) {
        String payload = http.getString();
        Serial.println(payload);
        DynamicJsonDocument doc(1024);
        deserializeJson(doc, payload);
        int state = doc[uuid]["state"].as<int>();
        int remaining_ms = doc[uuid]["remaining_ms"].as<int>();
        int blink_duration = doc[uuid]["blink_duration"].as<int>();
        // int interrupt_mask = doc["interrupt_mask"].as<int>();
        Serial.println("State: " + String(state) + " Remaining: " + String(remaining_ms) + " Blink: " + String(blink_duration));
        int interrupt_state = enter_state(state, remaining_ms, 0);
        // if (interrupt_state & interrupt_mask) {
        //     http.begin(SERVER + "setLightState/" + uuid + "/" + interrupt_state);
        //     http.GET();
        // }
        // enter_state(state, remaining_ms, 0);
    } else if (httpCode == 401) {
        // If the server returns 401, the light is not registered. Do nothing
        // uuid = "";
        intersection_id = -1;
        intersection_location = "";
        delay(1000);
    } else {
      delay(1000);
    }
}