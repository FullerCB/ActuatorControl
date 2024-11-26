//UPLOAD THIS CODE TO ARDUINO IDE SOFTWARE AND RUN - NO NEE

const int continuityPin = 7; // Pin used for continuity check

void setup() {
    pinMode(continuityPin, INPUT_PULLUP); // Use pull-up resistor for simplicity
    Serial.begin(9600);                  // Start serial communication
}

void loop() {
    int state = digitalRead(continuityPin);
    if (state == LOW) {
        Serial.println(1); // Continuity detected
    }
    else {
        Serial.println(0); // No continuity
    }
    delay(5); // Small delay for stability
}