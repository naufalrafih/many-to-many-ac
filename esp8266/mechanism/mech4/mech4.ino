#include <Arduino.h>
#define ARDUINOJSON_USE_LONG_LONG 1
#include <ArduinoJson.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include <SPI.h>
#include <MFRC522.h>
#include <gmp-ino.h>

//Wiring: https://www.instructables.com/MFRC522-RFID-Reader-Interfaced-With-NodeMCU/
#define RST_PIN         5           // Configurable, see typical pin layout above
#define SS_PIN          4          // Configurable, see typical pin layout above

MFRC522 mfrc522(SS_PIN, RST_PIN);   // Create MFRC522 instance

const char* ssid     = "mywifi";
const char* password = "543216789";
const char* hostserver = "192.168.137.1";
//IPAddress hostserver(192, 168, 137, 1);
uint16_t hostport = 35754;

static const char fp[] PROGMEM = "ED:3F:4A:CC:DB:DB:57:A5:C8:39:AE:65:D7:59:33:94:0E:1D:56:E0";
#include "functions.h"

unsigned long long institute_key;
String asset_name = "rock";
unsigned long long public_key = 231587109249421;
unsigned long long uid = 3642882455;

void setup() {
    Serial.begin(115200);
    SPI.begin();
    mfrc522.PCD_Init();
    delay(10);

    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);
    Serial.print("Connecting to ");
    Serial.print(ssid); Serial.println(" ...");

    int i = 0;
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(++i); Serial.print(' ');
    }

    Serial.println('\n');
    Serial.println("Connection established!");
    Serial.print("IP address:\t");
    Serial.println(WiFi.localIP());         // Send the IP address of the ESP8266 to the computer

    register_asset(&institute_key, asset_name);
    while (institute_key == -999) {
        delay(500); -
        Serial.println("Try registering and getting institute_key again...");
        register_asset(&institute_key, asset_name);
    }
}

void loop() {

    MFRC522::MIFARE_Key sector_key;

    Serial.println("Starting loop");
    Serial.printf("institute_key: %llu\n", institute_key);
    //Detect card. If no card is detected, reset loop.
    if ( ! mfrc522.PICC_IsNewCardPresent()) {
        return;
    }

    // Select one of the cards
    if ( ! mfrc522.PICC_ReadCardSerial()) {
        return;
    }

    sector_key = calculate_key(institute_key, uid, public_key);
    for (byte i = 0; i < 6; i++) {
        sector_key.keyByte[i] = 0xFF;
        Serial.printf("sector_key[%d] = %d\n", i, sector_key.keyByte[i]);
    }

    card_contents card_contents = iterate_sectors(sector_key);
    DynamicJsonDocument JsonBody = verify_request_body(card_contents);
    mfrc522.PCD_StopCrypto1();
    return;
}
