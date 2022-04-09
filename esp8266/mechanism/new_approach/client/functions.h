void setNTP() {
    // Set time via NTP, as required for x.509 validation
    configTime(3 * 3600, 0, "time.nist.gov", "pool.ntp.org");
    Serial.print(F("Waiting for NTP time sync: "));
    time_t now = time(nullptr);

    while (now < 8 * 3600 * 2) {
        delay(100);
        Serial.print(F("."));
        now = time(nullptr);
    }

    Serial.println(F(""));

    struct tm timeinfo;

    gmtime_r(&now, &timeinfo);

    Serial.print(F("Current time: "));
    Serial.print(asctime(&timeinfo));
}

int request(const char *method, const char *path, JsonDocument& doc_request, JsonDocument& doc_response, String request_body = "") {
    // 200: Successful
    // -1: Connection failed
    // -2: Deserialize failed
    Serial.println("FreeHeap:");
    Serial.println(ESP.getFreeHeap());
    if (WiFi.status() == WL_CONNECTED) {

        bool is_https = true;

        if (https.begin(*client, "https://" + String(hostserver) + ":" + String(hostport) + String(path))) {
            https.addHeader("Content-Type", "application/json");
            Serial.printf("[HTTPS] %s...\n", (String) method);
            // start connection and send HTTP header
            https.setTimeout(10000);
            if (request_body == "") {
                serializeJson(doc_request, request_body);
            }

            Serial.println(F("Attempting HTTPS request. Request body:"));
            Serial.println(request_body);
            int httpCode;

            if (method == "GET") {
                delay(0);
                httpCode = https.GET();
            } else if (method == "POST") {
                delay(0);
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
        } else {
            Serial.printf("[HTTPS] Unable to connect\n");
        }
        https.end();
    } else {
        Serial.println(F("WiFi not connected"));
    }
}

void register_asset(unsigned long long * institute_key, unsigned long long * public_key, String asset_name) {

    //Request body
    StaticJsonDocument<100> doc_request;
    doc_request["asset_name"] = asset_name;

    //Response body
    StaticJsonDocument<100> doc_response;

    //Request
    int response_code = request("POST", "/api/register/asset", doc_request, doc_response);
    if (response_code == 200) {
        Serial.println(F("Success registering and getting institute_key."));
    } else {
        Serial.println(F("Unsuccessful registering."));
        *institute_key = -999;
        return;
    }

    //Extract variable from response
    JsonVariant response1 = doc_response["institute_key"];;
    *institute_key = response1.as<unsigned long long>();

    JsonVariant response2 = doc_response["public_key"];;
    *public_key = response2.as<unsigned long long>();
    return;
}

String bytearray_to_hex(byte bytearray[], int len) {
    String hex = "";
    for (int i = 0; i < len; i++) {
        hex += String(bytearray[i], HEX);
    }
    return hex;
}

bool determine_action(String jsonBody) {

    //Response body
    StaticJsonDocument<48> doc_response;
    StaticJsonDocument<48> doc_request;
    //Request
    int response_code = request("POST", "/api/booking/verify", doc_request, doc_response, jsonBody);
    if (response_code == 200) {
        Serial.println(F("Success contacting server to determine action."));
    } else {
        Serial.println(F("Unsuccessful contacting server to determine action."));
        return false;
    }

    //Extract variable from response
    JsonVariant response = doc_response["permitted"];
    return response.as<bool>();
}

void actuate_access(bool isPermitted) {
    if (isPermitted) {
        Serial.println(F("Permitted."));
        if (thingState == 0) {
            Serial.println(F("Changing state to HIGH"));
            thingState = 1;
        } else {
            Serial.println(F("Changing state to LOW"));
            thingState = 0;
        }
        digitalWrite(thingPin, thingState);
    } else {
        Serial.println(F("Not permitted!"));
    }
}
