#define damage_pin 2

unsigned long start = 0;
int damage_time = 0;
bool damage_active = false;

void setup() {
  Serial.begin(9600);
  pinMode(damage_pin, OUTPUT);
  while (!Serial) {
    ;
  }
  digitalWrite(damage_pin, LOW);
}

void loop() {
  if (Serial.available() > 0) {
    int number = Serial.parseInt();
    while (Serial.available() > 0 && Serial.read() != '\n');
    
    if (number > 0) {
      damage_time = number;
      start = millis();
      damage_active = true;
      digitalWrite(damage_pin, HIGH);
    }
  }
  
  if (damage_active && (millis() - start >= (unsigned long)damage_time * 1000)) {
    digitalWrite(damage_pin, LOW);
    damage_active = false;
  }
}