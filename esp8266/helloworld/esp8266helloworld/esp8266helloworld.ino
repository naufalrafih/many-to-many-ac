
#include <Arduino.h>

#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>

const char* ssid     = "mywifi";
const char* password = "543216789";
String hostserver = "192.168.137.1";
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
  // wait for WiFi connection
  if ((WiFi.status() == WL_CONNECTED)) {

    WiFiClient client;

    HTTPClient http;
    String url = "http://" + hostserver + ":" + String(hostport) + "/";
    Serial.print("Inititating HTTP client to " + url + "\n");
    if (http.begin(client, url)) {  // HTTP


      Serial.print("Sending HTTP GET.\n");
      int httpCode = http.GET();

      if (httpCode > 0) { //Success
        Serial.printf("Success. Got HTTP code: %d\n", httpCode);

        // file found at server
        if (httpCode == HTTP_CODE_OK || httpCode == HTTP_CODE_MOVED_PERMANENTLY) {
          String payload = http.getString();
          Serial.println(payload);
        }
      } else {
        Serial.printf("Unsuccessful. Error: %s\n", http.errorToString(httpCode).c_str());
      }

      http.end();
    } else {
      Serial.printf("Unable to connect.\n");
    }
  }

  delay(5000);
}
