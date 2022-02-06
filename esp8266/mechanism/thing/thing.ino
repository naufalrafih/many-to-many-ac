
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

}

void loop() {
    if (Serial.available() > 0) {
        int c = Serial.read();

        //Request body
        StaticJsonDocument<48> doc_request;
        doc_request["asset_name"] = "lamp";

        //Response body
        StaticJsonDocument<48> doc_response;
        
        //Request
        int response_code = request("POST","/api/register/asset",doc_request,doc_response);
        if (response_code == 200) {
            Serial.println("Request successful.");
        } else {
            Serial.println("Request unsuccessful.");
            return;
        }
        
        //Extract variable from response
        const char * key_a = doc_response["key_a"];
        Serial.printf("key_a: %s\n",key_a);
    }
}
