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

int request(const char *method, const char *path, JsonDocument& doc_request, JsonDocument& doc_response) {
    // 200: Successful
    // -1: Connection failed
    // -2: Deserialize failed
    BearSSL::WiFiClientSecure wifiClient;
    wifiClient.setFingerprint(fp);

    setNTP();

    bool is_https = true;
    HTTPClient https;

    if (https.begin(wifiClient, hostserver, hostport, path, is_https)) {
        Serial.printf("[HTTPS] %s...\n", (String) method);
        // start connection and send HTTP header

        String request_body;
        serializeJson(doc_request, request_body);

        https.addHeader("Content-Type", "application/json");
        int httpCode;
        if (method == "GET") {
            httpCode = https.GET();
        } else if (method == "POST") {
            httpCode = https.POST(request_body);
        }

        // httpCode will be negative on error
        if (httpCode > 0) {
            // HTTP header has been send and Server response header has been handled
            Serial.printf("[HTTPS] %s... code: %d\n", (String) method, httpCode);

            // file found at server
            if (httpCode == HTTP_CODE_OK || httpCode == HTTP_CODE_MOVED_PERMANENTLY) {
                String payload = https.getString();
                Serial.println(payload);
                DeserializationError error = deserializeJson(doc_response, payload);
                if (error) {
                    Serial.print(F("deserializeJson() failed: "));
                    Serial.println(error.f_str());
                    return -2;
                }
                return 200;
            }
        } else {
            Serial.printf("[HTTPS] %s... failed, error: %s\n", (String) method, https.errorToString(httpCode).c_str());
            return httpCode;
        }
    }
}

void register_asset(unsigned long long * institute_key, String asset_name) {
    
    //Request body
    StaticJsonDocument<48> doc_request;
    doc_request["asset_name"] = asset_name;

    //Response body
    StaticJsonDocument<48> doc_response;

    //Request
    int response_code = request("POST", "/api/register/asset", doc_request, doc_response);
    if (response_code == 200) {
        Serial.println("Success registering and getting institute_key.");
    } else {
        Serial.println("Unsuccessful registering.");
        *institute_key = -999;
        return;
    }

    //Extract variable from response
    JsonVariant response = doc_response["institute_key"];;
    *institute_key = response.as<unsigned long long>();
    return;
}
