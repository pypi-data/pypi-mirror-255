const int input = 2; // Input pin
int pulse = 0; // Count of pulses
bool last_gpio_state = false;
unsigned long last_trigger_time = 0; // Time of the last trigger
const unsigned long trigger_delay = 10000; // 10-second delay
bool is_trigger_ignored = false; // Flag to ignore triggers
unsigned long time_btwn_triggers_ms = 0;

void setup() {
  pinMode(input, INPUT);
  Serial.begin(1000000);
  Serial.println(F("Wiliot Yield Counter"));
}

void loop() {
  bool cur_gpio_state = digitalRead(input);

  // Check for the rising edge
  if (cur_gpio_state == true && last_gpio_state == false) {
    if (!is_trigger_ignored) {
      pulse++;
      is_trigger_ignored = true; // Start ignoring triggers
      last_trigger_time = millis(); // Record the time of this trigger
      Serial.print(pulse);
      Serial.println(" pulses detected.");
    }
  }

  // Check if 10 seconds have passed since the last trigger
  if (is_trigger_ignored && (millis() - last_trigger_time > trigger_delay)) {
    is_trigger_ignored = false; // Stop ignoring triggers after 10 seconds
  }

  last_gpio_state = cur_gpio_state;
}
