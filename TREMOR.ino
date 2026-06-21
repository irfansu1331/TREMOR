#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

#define DHTPIN 4
#define DHTTYPE DHT22

const char* ssid = "EYANG-2.4G";
const char* password = "8184880557";

const char* mqtt_server = "192.168.18.233";
const int mqtt_port = 1883;

const char* mqtt_user = "tremor";
const char* mqtt_password = "#tr3m0r";

WiFiClient espClient;
PubSubClient client(espClient);
DHT dht(DHTPIN, DHTTYPE);

LiquidCrystal_I2C lcd(0x27, 16, 2);

unsigned long lastRead = 0;
unsigned long lastPublish = 0;

const long readInterval = 3000;
const long publishInterval = 10000;

float temperature = 0;
float humidity = 0;

void setup_wifi() {

  Serial.println();
  Serial.println("=================================");
  Serial.println("TREMOR DHT22 MQTT");
  Serial.println("=================================");

  WiFi.setHostname("TREMOR-DHT22");

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Connecting WiFi");
  lcd.setCursor(0, 1);
  lcd.print("Please wait");

  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("WiFi Connected");

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("WiFi Connected");

  delay(1500);
}

void reconnect() {

  while (!client.connected()) {

    String clientId = "TREMOR-";
    clientId += String(random(0xffff), HEX);

    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Connecting");
    lcd.setCursor(0, 1);
    lcd.print("MQTT...");

    if (client.connect(
          clientId.c_str(),
          mqtt_user,
          mqtt_password,
          "tremor/status",
          0,
          true,
          "offline")) {

      Serial.println("MQTT Connected");

      client.publish(
        "tremor/status",
        "online",
        true);

      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("MQTT Connected");

      delay(1000);

    } else {

      Serial.print("MQTT Failed rc=");
      Serial.println(client.state());

      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("MQTT Failed");
      lcd.setCursor(0, 1);
      lcd.print("rc=");
      lcd.print(client.state());

      delay(5000);
    }
  }
}

void setup() {

  Serial.begin(115200);

  randomSeed(micros());

  dht.begin();

  Wire.begin(21, 22);

  lcd.begin();
  lcd.backlight();

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("TREMOR SYSTEM");
  lcd.setCursor(0, 1);
  lcd.print("Starting...");

  delay(2000);

  setup_wifi();

  client.setServer(mqtt_server, mqtt_port);
}

void loop() {

  if (!client.connected()) {
    reconnect();
  }

  client.loop();

  unsigned long now = millis();

  if (now - lastRead >= readInterval) {

    lastRead = now;

    temperature = dht.readTemperature();
    humidity = dht.readHumidity();

    if (isnan(temperature) || isnan(humidity)) {

      Serial.println("DHT22 Read Failed!");

      client.publish(
        "tremor/error",
        "DHT22 Read Failed"
      );

      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("DHT22 ERROR");

      return;
    }

    lcd.clear();

    lcd.setCursor(0, 0);
    lcd.print("POP Temp:");
    lcd.print(temperature, 1);
    lcd.print("C");

    lcd.setCursor(0, 1);
    lcd.print("BLP Hum :");
    lcd.print(humidity, 0);
    lcd.print("%");

    Serial.println("--------------------------------");

    Serial.print("Temperature : ");
    Serial.print(temperature);
    Serial.println(" C");

    Serial.print("Humidity    : ");
    Serial.print(humidity);
    Serial.println(" %");

    Serial.println("--------------------------------");
  }

  if (now - lastPublish >= publishInterval) {

    lastPublish = now;

    int rssi = WiFi.RSSI();

    char payload[200];

    snprintf(
      payload,
      sizeof(payload),
      "{\"device\":\"esp32-dht22\",\"temperature\":%.2f,\"humidity\":%.2f,\"rssi\":%d}",
      temperature,
      humidity,
      rssi
    );

    client.publish(
      "tremor/dht22",
      payload,
      true
    );

    Serial.println("=== MQTT PUBLISHED ===");
    Serial.println(payload);
    Serial.println("======================");
  }
}