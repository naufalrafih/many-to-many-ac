
#include <Arduino.h>
#include <ArduinoJson.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>

const char* ssid     = "mywifi";
const char* password = "543216789";
const char* hostserver = "192.168.137.1";
//IPAddress hostserver(192, 168, 137, 1);
uint16_t hostport = 35754;

static const char fp[] PROGMEM = "ED:3F:4A:CC:DB:DB:57:A5:C8:39:AE:65:D7:59:33:94:0E:1D:56:E0";
#include "functions.h"

char * key_a;
String asset_name = "rock";

void setup() {
    Serial.begin(115200);
    delay(10);

    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);
    Serial.print("Connecting to ");
    Serial.print(ssid); Serial.println(" ...");

    int i = 0;
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.print(++i); Serial.print(' ');
    }

    Serial.println('\n');
    Serial.println("Connection established!");
    Serial.print("IP address:\t");
    Serial.println(WiFi.localIP());         // Send the IP address of the ESP8266 to the computer

    register_asset(&key_a, asset_name);
    while ((String) key_a == "FAILED") {
        delay(1000);
        Serial.println("Try getting key A again...");
        register_asset(&key_a, asset_name);
    }
}

void loop() {
    if (Serial.available() > 0) {
        int c = Serial.read();
        Serial.println("Pressed.");
        Serial.print("Key_A: "); Serial.println(key_a);
    }
}
