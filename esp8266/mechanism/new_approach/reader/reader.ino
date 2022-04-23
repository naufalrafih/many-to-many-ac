#define ARDUINOJSON_USE_LONG_LONG 1
#include <ArduinoJson.h>
#include <SPI.h>
#include <MFRC522.h>
#include <SoftwareSerial.h>
#include <gmp-ino.h>

#define RST_PIN         5           // Configurable, see typical pin layout above
#define SS_PIN          4          // Configurable, see typical pin layout above

#include "functions.h"

//unsigned long long sector_key_int = 164567021437205;
unsigned long long institute_key = 0;
unsigned long long public_key = 0;

MFRC522 mfrc522(SS_PIN, RST_PIN);   // Create MFRC522 instance
SoftwareSerial linkSerial(0, 2);

void setup() {
    pinMode(BUILTIN_LED,OUTPUT);
    Serial.begin(115200);
    linkSerial.begin(4800);
    delay(10);
    while (institute_key == 0 | public_key == 0) {
        Serial.println("Getting sector_key...");
        linkSerial.println("k");
        if (linkSerial.available()) {
            byte keys_buf[12];
            linkSerial.readBytesUntil('\n', keys_buf, 12);
            for (int i = 0; i < 6; i++) {
                Serial.printf("institute_key[%d] = %d\n", i, keys_buf[i]);
            }
            for (int i = 0; i < 6; i++) {
                Serial.printf("public_key[%d] = %d\n", i, keys_buf[i + 6]);
            }
            Serial.println("Acquired keys:");
            institute_key =
                ((unsigned long long) keys_buf[0] << 40) | ((unsigned long long) keys_buf[1] << 32) |
                ((unsigned long long) keys_buf[2] << 24) | ((unsigned long long) keys_buf[3] << 16) |
                ((unsigned long long) keys_buf[4] << 8) | ((unsigned long long) keys_buf[5] << 0);
            Serial.printf("institute_key = %llu\n", institute_key);
            institute_key = institute_key << 16;
            institute_key = institute_key >> 16;
            public_key =
                ((unsigned long long) keys_buf[6] << 40) | ((unsigned long long) keys_buf[7] << 32) |
                ((unsigned long long) keys_buf[8] << 24) | ((unsigned long long) keys_buf[9] << 16) |
                ((unsigned long long) keys_buf[10] << 8) | ((unsigned long long) keys_buf[11] << 0);
            Serial.printf("public_key = %llu\n", public_key);
            public_key = public_key << 16;
            public_key = public_key >> 16;
            break;
        }
        delay(1000);
    }

    SPI.begin();
    mfrc522.PCD_Init();


}

void loop() {

    //Detect card. If no card is detected, reset loop.
    if ( ! mfrc522.PICC_IsNewCardPresent()) {
        return;
    }

    // Select one of the cards
    if ( ! mfrc522.PICC_ReadCardSerial()) {
        return;
    }

    unsigned long long uid = (mfrc522.uid.uidByte[0] << 24) | (mfrc522.uid.uidByte[1] << 16) | (mfrc522.uid.uidByte[2] << 8) | (mfrc522.uid.uidByte[3] << 0);
    uid = uid << 32;
    uid = uid >> 32;
    Serial.printf("UID: %llu\n", uid);

    MFRC522::MIFARE_Key sector_key;
    sector_key = calculate_key(institute_key, uid, public_key);
    for (byte i = 0; i < 6; i++) {
        Serial.printf("sector_key[%d] = %d\n", i, sector_key.keyByte[i]);
    }

    digitalWrite(BUILTIN_LED, HIGH);
    card_contents card_contents = iterate_sectors(sector_key, mfrc522);
    digitalWrite(BUILTIN_LED, LOW);
    String request_body = verify_request_body(card_contents, mfrc522);

    Serial.println("Request body:");
    Serial.println(request_body);
    linkSerial.println("TEST");
    linkSerial.println(request_body);
}
