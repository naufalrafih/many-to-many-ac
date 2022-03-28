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

unsigned long long mpz2ull(mpz_t z) {
    unsigned long long result = 0;
    mpz_export(&result, 0, -1, sizeof result, 0, 0, z);
    return result;
}

void ull2mpz(mpz_t z, unsigned long long ull) {
    mpz_import(z, 1, -1, sizeof ull, 0, 0, &ull);
}

MFRC522::MIFARE_Key calculate_key(unsigned long long institute_key, unsigned long long uid, unsigned long long public_key) {
    mpz_t i, p, u, r;
    mpz_init(i);
    mpz_init(p);
    mpz_init(u);
    mpz_init(r);

    ull2mpz(i, institute_key);
    ull2mpz(u, uid);
    ull2mpz(p, public_key);

    mpz_powm(r, i, u, p);

    unsigned long long sector_key_int = mpz2ull(r);
    
    MFRC522::MIFARE_Key key;
    for (byte i = 0; i < 6; i++) {
        key.keyByte[i] = 0xFF & (sector_key_int >> (40-i*8));
    }
    return key;
}

typedef struct {
    byte data[4][16];
} sector_data;


sector_data read_sector(int sector_number, MFRC522::MIFARE_Key sector_key) {
    MFRC522::StatusCode status;
    byte blocks[4];
    for (int i = 0; i < 4; i++) blocks[i] = sector_number*4 + i;
    sector_data sector_data;

    status = mfrc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, blocks[0], &sector_key, &(mfrc522.uid));
    if (status != MFRC522::STATUS_OK) {
        Serial.print(F("Authentication failed: "));
        Serial.println(mfrc522.GetStatusCodeName(status));
        for (int i = 0; i < 4; i++) {
            for (int j = 0; j < 16; j++) {
                sector_data.data[i][j] = 0xFF;
            }
        }
        return sector_data;
    }

    for (int i = 0; i < 4; i++) { //Iterate through blocks in the sector
        byte buffer_block[16];
        byte len = 16;

        //Read data from block
        status = mfrc522.MIFARE_Read(blocks[i], buffer_block, &len);
        if (status != MFRC522::STATUS_OK) {
            Serial.print(F("Reading failed: "));
            Serial.println(mfrc522.GetStatusCodeName(status));
              
            for (int i = 0; i < 4; i++) {
                for (int j = 0; j < 16; j++) {
                    sector_data.data[i][j] = 0xFF;
                }
            }
            return sector_data;
        }

        //Move data from buffer to sector_data for corresponding block
        for (int j = 0; j < 16; j++) {
            sector_data.data[i][j] = buffer_block[j];
        }
    }

    return sector_data;
}
