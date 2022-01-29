void setNTP() {
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
}

void getRequest( BearSSL::WiFiClientSecure *wifiClient, const char *path) {
  wifiClient->write("GET ");
  wifiClient->write(path);
  wifiClient->write(" HTTP/1.0\r\n");
  wifiClient->write("User-Agent: ESP8266\r\n");
  wifiClient->write("\r\n");
}