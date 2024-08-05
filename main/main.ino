const int inputPin = 7;
const int outputPin = 13;
const int pwmPin = 9;

String option = "";

int count = 0;
unsigned long previousMillis = 0;
int aux = 0;

int measure_values_count = 0;
int set_freq = 0;
float given_freq = 0;
float last_freq = 11;
String given_freq_string = "10";

float pulse_width =1;
unsigned long pulse_width_int =1;
unsigned long stay_off_time = 1;
unsigned long stay_on_time = 1;

unsigned long currentMillis = 0;

void setup() {
  Serial.begin(115200);
  pinMode(inputPin, INPUT);
  pinMode(outputPin, OUTPUT);
  digitalWrite(outputPin, LOW);
  pinMode(pwmPin, OUTPUT);
  analogWrite(pwmPin, 0);
}

void read_option() {
  Serial.println("Option: ");
  while (Serial.available() == 0) {}
  option = Serial.readStringUntil('\n');
  if (option == "measure") {
    measure_values_count = 0;
    measure_function();
  }
  if (option == "start_s") {
    set_freq = 1;
    read_desired_freq();
  }
  if (option == "speed1") {
    analogWrite(pwmPin, 255);
    delay(1000);
    analogWrite(pwmPin, 100);
  }
  if (option == "speed2") {
    analogWrite(pwmPin, 255);
    delay(1000);
    analogWrite(pwmPin, 150);
  }
  if (option == "speed3") {
    analogWrite(pwmPin, 255);
    delay(1000);
    analogWrite(pwmPin, 255);
  }
  if (option == "speed4") {
    analogWrite(pwmPin, 200);
  }
  if (option == "speed0") {
    analogWrite(pwmPin, 0);
  }
}

void read_desired_freq() {
  while (set_freq == 1) {
    if (Serial.available() > 0) {
    }
    given_freq_string = Serial.readStringUntil('\n');
    if (given_freq_string == "s") {
      set_freq = 0;
      Serial.println("Stopped successfully");
    } else {
      given_freq = given_freq_string.toFloat();
      if (given_freq !=0 and given_freq!=last_freq)
      {
        last_freq=given_freq;
      }
      init_freq_output(last_freq);
    }
  }
}

void init_freq_output(float received_freq) {
  pulse_width = 1000000 / received_freq;

  pulse_width_int = long(pulse_width);

  stay_on_time = pulse_width_int / 10;
  stay_off_time = pulse_width_int - stay_on_time;

  unsigned long start_time = millis();
  while (millis() - start_time < 3000) {
    digitalWrite(outputPin, HIGH);
    delayMicroseconds(stay_on_time);
    digitalWrite(outputPin, LOW);
    delay(stay_off_time/1000);
  }
}

void measure_function() {
  while (measure_values_count < 11) {
    currentMillis = millis();
    if (digitalRead(inputPin) == HIGH && aux == 0) {
      aux = 1;
      count++;
    }
    if (digitalRead(inputPin) == LOW && aux == 1) {
      aux = 0;
    }
    if (currentMillis - previousMillis >= 1000) {
      Serial.println(count);
      previousMillis = 0;
      count = 0;
      previousMillis = currentMillis;
      measure_values_count += 1;
    }
  }
}

void loop() {
  read_option();
}

