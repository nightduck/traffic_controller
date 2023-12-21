#include <Arduino.h>
#include <Wire.h>

#include "mapping.h"

void set_traffic_light(int addr, int state) {
  Wire.beginTransmission(addr);
  Wire.write(OUTPUT_REGISTER);
  Wire.write(state);
  Wire.endTransmission();
}


int enter_state(int ne_led_mask, int nw_led_mask, int sw_led_mask, int se_led_mask,
                int ne_blink_mask, int nw_blink_mask, int sw_blink_mask, int se_blink_mask,
                int blink_duration, int state_duration, int interrupt_mask) {
  int time = 0;
  int interrupt_state = 0;
  
  // Do not blink
  if (blink_duration <= 0) {
    blink_duration = state_duration;
  }

  set_traffic_light(NE_CORNER_ADDR, ne_led_mask);
  set_traffic_light(NW_CORNER_ADDR, nw_led_mask);
  set_traffic_light(SW_CORNER_ADDR, sw_led_mask);
  set_traffic_light(SE_CORNER_ADDR, se_led_mask);

  while(time < state_duration && !(interrupt_state & interrupt_mask)) {
    delay(100);
    time++;

    if (time % blink_duration == 0) {
      ne_led_mask ^= ne_blink_mask;
      nw_led_mask ^= nw_blink_mask;
      sw_led_mask ^= sw_blink_mask;
      se_led_mask ^= se_blink_mask;
      set_traffic_light(NE_CORNER_ADDR, ne_led_mask);
      set_traffic_light(NW_CORNER_ADDR, nw_led_mask);
      set_traffic_light(SW_CORNER_ADDR, sw_led_mask);
      set_traffic_light(SE_CORNER_ADDR, se_led_mask);
    }

    // TODO: Read interrupt state, pursuant to mask

    interrupt_state &= interrupt_mask;

    if (interrupt_state) {
      break;
    }
  }
  return interrupt_state;
}

void led_test() {
  enter_state(RED_LIGHT, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0);
  enter_state(0, RED_LIGHT, 0, 0, 0, 0, 0, 0, 0, 5, 0);
  enter_state(0, 0, RED_LIGHT, 0, 0, 0, 0, 0, 0, 5, 0);
  enter_state(0, 0, 0, RED_LIGHT, 0, 0, 0, 0, 0, 5, 0);

  enter_state(YELLOW_LIGHT, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0);
  enter_state(0, YELLOW_LIGHT, 0, 0, 0, 0, 0, 0, 0, 5, 0);
  enter_state(0, 0, YELLOW_LIGHT, 0, 0, 0, 0, 0, 0, 5, 0);
  enter_state(0, 0, 0, YELLOW_LIGHT, 0, 0, 0, 0, 0, 5, 0);
  
  enter_state(GREEN_LIGHT, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0);
  enter_state(0, GREEN_LIGHT, 0, 0, 0, 0, 0, 0, 0, 5, 0);
  enter_state(0, 0, GREEN_LIGHT, 0, 0, 0, 0, 0, 0, 5, 0);
  enter_state(0, 0, 0, GREEN_LIGHT, 0, 0, 0, 0, 0, 5, 0);
  
  enter_state(DNW, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0);
  enter_state(0, DNW, 0, 0, 0, 0, 0, 0, 0, 5, 0);
  enter_state(0, 0, DNW, 0, 0, 0, 0, 0, 0, 5, 0);
  enter_state(0, 0, 0, DNW, 0, 0, 0, 0, 0, 5, 0);
  
  enter_state(WALK, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0);
  enter_state(0, WALK, 0, 0, 0, 0, 0, 0, 0, 5, 0);
  enter_state(0, 0, WALK, 0, 0, 0, 0, 0, 0, 5, 0);
  enter_state(0, 0, 0, WALK, 0, 0, 0, 0, 0, 5, 0);
  
  enter_state(DNW_PERP, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0);
  enter_state(0, DNW_PERP, 0, 0, 0, 0, 0, 0, 0, 5, 0);
  enter_state(0, 0, DNW_PERP, 0, 0, 0, 0, 0, 0, 5, 0);
  enter_state(0, 0, 0, DNW_PERP, 0, 0, 0, 0, 0, 5, 0);
  
  enter_state(WALK_PERP, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0);
  enter_state(0, WALK_PERP, 0, 0, 0, 0, 0, 0, 0, 5, 0);
  enter_state(0, 0, WALK_PERP, 0, 0, 0, 0, 0, 0, 5, 0);
  enter_state(0, 0, 0, WALK_PERP, 0, 0, 0, 0, 0, 5, 0);
}

void basic_loop(int ns_duration, int ew_duration, int ns_yellow_duration, int ew_yellow_duration,
  int red_overlap, int pedestrian_warning) {
    // East-west traffic can go
    enter_state(RED_LIGHT | DNW | WALK_PERP, GREEN_LIGHT | WALK | DNW_PERP,
                RED_LIGHT | DNW | WALK_PERP, GREEN_LIGHT | WALK | DNW_PERP,
                0, 0, 0, 0,
                0, 10 * (ew_duration - pedestrian_warning), 0);

    // East-west pedestrian lights start blinking
    enter_state(RED_LIGHT | DNW | DNW_PERP, GREEN_LIGHT | DNW | DNW_PERP,
                RED_LIGHT | DNW | DNW_PERP, GREEN_LIGHT | DNW | DNW_PERP,
                DNW_PERP, 0, DNW_PERP, 0,
                0, 10 * pedestrian_warning, 0);

    // East-west traffic gets yellow light, pedestrians all do not cross
    enter_state(RED_LIGHT | DNW | DNW_PERP, YELLOW_LIGHT | DNW | DNW_PERP,
                RED_LIGHT | DNW | DNW_PERP, YELLOW_LIGHT | DNW | DNW_PERP,
                0, 0, 0, 0,
                0, 10 * ew_yellow_duration, 0);

    // All red to account for the assholes who "thought they could make it"
    enter_state(RED_LIGHT | DNW | DNW_PERP, RED_LIGHT | DNW | DNW_PERP,
                RED_LIGHT | DNW | DNW_PERP, RED_LIGHT | DNW | DNW_PERP,
                0, 0, 0, 0,
                0, 10 * red_overlap, 0);

    // North south traffic can go
    enter_state(GREEN_LIGHT | WALK | DNW_PERP, RED_LIGHT | DNW | WALK_PERP, 
                GREEN_LIGHT | WALK | DNW_PERP, RED_LIGHT | DNW | WALK_PERP, 
                0, 0, 0, 0,
                0, 10 * (ns_duration - pedestrian_warning), 0);

    // North-south pedestrian lights start blinking
    enter_state(GREEN_LIGHT | DNW | DNW_PERP, RED_LIGHT | DNW | DNW_PERP, 
                GREEN_LIGHT | DNW | DNW_PERP, RED_LIGHT | DNW | DNW_PERP, 
                0, DNW_PERP, 0, DNW_PERP,
                0, 10 * pedestrian_warning, 0);

    // East-west traffic gets yellow light, pedestrians all do not cross
    enter_state(YELLOW_LIGHT | DNW | DNW_PERP, RED_LIGHT | DNW | DNW_PERP, 
                YELLOW_LIGHT | DNW | DNW_PERP, RED_LIGHT | DNW | DNW_PERP, 
                0, 0, 0, 0,
                0, 10 * ns_yellow_duration, 0);

    // All red to account for the assholes who "thought they could make it"
    enter_state(RED_LIGHT | DNW | DNW_PERP, RED_LIGHT | DNW | DNW_PERP,
                RED_LIGHT | DNW | DNW_PERP, RED_LIGHT | DNW | DNW_PERP,
                0, 0, 0, 0,
                0, 10 * red_overlap, 0);
}

void setup() {
  // put your setup code here, to run once:
  Wire.begin();
  Wire.setClock(1000);
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
  Wire.beginTransmission(NW_CORNER_ADDR);
  Wire.write(buf, 11);
  Wire.endTransmission();
  Wire.beginTransmission(SW_CORNER_ADDR);
  Wire.write(buf, 11);
  Wire.endTransmission();
  Wire.beginTransmission(SE_CORNER_ADDR);
  Wire.write(buf, 11);
  Wire.endTransmission();
}

void loop() {
  //basic_loop(30, 30, 4, 4, 2, 10);
  led_test();
  //enter_state(RED_LIGHT, RED_LIGHT, RED_LIGHT, RED_LIGHT,
  //0, 0, 0, 0, 0, 1, 0);
}