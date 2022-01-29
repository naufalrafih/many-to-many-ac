
#include <Arduino.h>

#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include "certificate.h"
#include "functions.h"

const char* ssid     = "mywifi";
const char* password = "543216789";
//const char* hostserver = "192.168.137.145";
IPAddress hostserver(192, 168, 137, 145);
uint16_t hostport = 5000;

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
  BearSSL::WiFiClientSecure wifiClient;

  Serial.println("Establishing certificate...");
  wifiClient.setTrustAnchors(&certificate);

  setNTP();
  
  Serial.println("Connecting");
  wifiClient.connect(hostserver, hostport);
  if (!wifiClient.connected()) {
    Serial.println("Can't connect!!!");
    delay(1000);
    return;
  }

  Serial.println("Connected!");

  getRequest(&wifiClient, "/");
  
  delay(5000);
}
