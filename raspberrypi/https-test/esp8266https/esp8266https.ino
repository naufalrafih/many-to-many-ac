
#include <Arduino.h>

#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include "certificate.h"

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

  // Set time via NTP, as required for x.509 validation
  configTime(3 * 3600, 0, "time.nist.gov", "pool.ntp.org");
  Serial.print("Waiting for NTP time sync: ");
  time_t now = time(nullptr);

  while (now < 8 * 3600 * 2) { 
    delay(500);
    Serial.print(".");
    now = time(nullptr);
  }

  Serial.println("");

  struct tm timeinfo;

  gmtime_r(&now, &timeinfo);

  Serial.print("Current time: ");
  Serial.print(asctime(&timeinfo));

  Serial.println("Connecting");
  wifiClient.connect(hostserver, hostport);
  if (!wifiClient.connected()) {
    Serial.println("Can't connect!!!");
    delay(1000);
    return;
  }

  Serial.println("Connected!");
  wifiClient.write("GET ");
  wifiClient.write("/");
  wifiClient.write(" HTTP/1.0\r\nHost: ");
  wifiClient.write("192.168.43.128");
  wifiClient.write("\r\nUser-Agent: ESP8266\r\n");
  wifiClient.write("\r\n");
  
  delay(5000);
}
