#include <cstdio>
#include <cstdlib>

#include "Arduino.h"
#include "../firmware/DoorAlarm/DoorAlarm.ino"

namespace {
unsigned long clockMs = 0;
int sensorMv = 142;
int button = HIGH;
int buzzer = LOW;

void expect(bool condition, const char* scenario) {
  if (!condition) {
    std::fprintf(stderr, "FAIL at %lu ms: %s\n", clockMs, scenario);
    std::exit(1);
  }
}

void ticks(unsigned count) {
  for (unsigned i = 0; i < count; ++i) loop();
}
}

void pinMode(int pin, int mode) {
  expect((pin == 21 && mode == INPUT) || (pin == 22 && mode == OUTPUT), "pin mode");
}
void digitalWrite(int pin, int value) {
  expect(pin == 22, "buzzer is on GPIO22");
  buzzer = value;
}
int digitalRead(int pin) {
  expect(pin == 21, "switch button is on GPIO21");
  return button;
}
int analogReadMilliVolts(int pin) {
  expect(pin == 34, "photodiode is on GPIO34");
  return sensorMv;
}
unsigned long millis() { return clockMs; }
void delay(unsigned long ms) { clockMs += ms; }

int main() {
  setup();
  ticks(25);
  expect(buzzer == LOW, "startup without beam stays silent");

  sensorMv = 3171;
  ticks(13);
  expect(buzzer == LOW, "valid beam arms without sounding");
  sensorMv = 142;
  ticks(2);
  sensorMv = 3171;
  ticks(2);
  expect(buzzer == LOW, "brief drop does not trip alarm");

  sensorMv = 142;
  ticks(3);
  expect(buzzer == HIGH, "10 ms stable drop trips the alarm");
  sensorMv = 3171;
  ticks(13);
  expect(buzzer == HIGH, "restored beam does not silence alarm");
  button = LOW;
  ticks(1);
  expect(buzzer == LOW, "pressed switch button silences alarm");
  button = HIGH;
  ticks(1);

  sensorMv = 142;
  ticks(3);
  expect(buzzer == HIGH, "an armed alarm detects another break");
  button = LOW;
  ticks(4);
  expect(buzzer == LOW, "silenced alarm stays quiet while blocked");
  button = HIGH;
  sensorMv = 3171;
  ticks(12);
  sensorMv = 142;
  ticks(3);
  expect(buzzer == LOW, "less than 60 ms of return does not rearm");
  sensorMv = 3171;
  ticks(13);
  sensorMv = 142;
  ticks(3);
  expect(buzzer == HIGH, "60 ms stable return rearms after a blocked silence");
  std::puts("PASS: startup, stable break, latch, switch, and rearm");
}
