#include <ESP8266WiFi.h>
#include <ArduinoJson.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include <SoftwareSerial.h>

#define ssid     "mywifi"
#define password "543216789"
#define hostserver "192.168.137.23"
//IPAddress hostserver(192, 168, 137, 1);
#define hostport 35754

SoftwareSerial linkSerial(0, 2);
std::unique_ptr<BearSSL::WiFiClientSecure>client(new BearSSL::WiFiClientSecure);
HTTPClient https;

int thingPin = 16; //D0
int thingState = 0;

static const char fp[] PROGMEM = "FE:1C:C4:34:7A:F4:A3:C7:26:9F:8A:AA:F0:1E:AD:25:4C:F1:5E:64";
#include "functions.h"

unsigned long long institute_key;
unsigned long long public_key;
#define asset_name "lamp"

void setup() {
    pinMode(thingPin, OUTPUT);
    digitalWrite(thingPin, thingState);
    Serial.begin(115200);
    linkSerial.begin(4800);
    delay(10);

    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);
    Serial.print(F("Connecting to "));
    Serial.print(ssid); Serial.println(F(" ..."));

    int i = 0;
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(++i); Serial.print(F(" "));
    }

    Serial.println(F("\n"));
    Serial.println(F("Connection established!"));
    Serial.print(F("IP address:\t"));
    Serial.println(WiFi.localIP());         // Send the IP address of the ESP8266 to the computer

    delay(50);

    client->setFingerprint(fp);
    setNTP();

    register_asset(&institute_key, &public_key, asset_name);
    while (institute_key == -999) {
        delay(500);
        Serial.println(F("Try registering and getting institute_key again..."));
        register_asset(&institute_key, &public_key, asset_name);
    }
}

void loop() {

    if (linkSerial.available()) {
        String received = linkSerial.readStringUntil('\n');
        if (received.charAt(0) == 'k') {
            Serial.println("Received key request. Sending...");
            byte key_buf[12];
            for (int i = 0; i < 6; i++) {
                key_buf[i] = 0xFF & (institute_key >> (40 - i * 8));
                key_buf[i + 6] = 0xFF & (public_key >> (40 - i * 8));
            }
            for (int i = 0; i < 6; i++) {
                Serial.printf("institute_key[%d] = %d\n",i, key_buf[i]);
            }
            for (int i = 0; i < 6; i++) {
                Serial.printf("public_key[%d] = %d\n",i, key_buf[i+6]);
            }
            linkSerial.write(key_buf, 12);
            linkSerial.print('\n');
            Serial.println("Sent!");
        } else if (received.charAt(0) == '{') {
            Serial.println("Received access permits.");
            actuate_access(determine_action(received));
        } else {
            Serial.println("Received an unknown command");
        }
    }
}
