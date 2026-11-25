// VisionSpec: read three HC-SR04 sensors and send distances over USB serial.
// Output line: left,front,right  (centimetres, -1 means no echo)

const int SENSOR_COUNT = 3;
const int TRIG_PINS[SENSOR_COUNT] = {2, 4, 6};  // left, front, right
const int ECHO_PINS[SENSOR_COUNT] = {3, 5, 7};

const unsigned long ECHO_TIMEOUT_US = 25000UL;  // about 4 m

long readDistanceCm(int trigPin, int echoPin) {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  unsigned long duration = pulseIn(echoPin, HIGH, ECHO_TIMEOUT_US);
  if (duration == 0) {
    return -1;
  }
  return duration / 58;
}

void setup() {
  Serial.begin(115200);
  for (int i = 0; i < SENSOR_COUNT; i++) {
    pinMode(TRIG_PINS[i], OUTPUT);
    pinMode(ECHO_PINS[i], INPUT);
  }
}

void loop() {
  for (int i = 0; i < SENSOR_COUNT; i++) {
    Serial.print(readDistanceCm(TRIG_PINS[i], ECHO_PINS[i]));
    if (i < SENSOR_COUNT - 1) {
      Serial.print(',');
    }
    delay(30);  // lets the echo fade so sensors do not hear each other
  }
  Serial.println();
  delay(60);
}
