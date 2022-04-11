String bytearray_to_hex(byte bytearray[], int len) {
    String hex = "";
    for (int i = 0; i < len; i++) {
        hex += String(bytearray[i], HEX);
    }
    return hex;
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
    Serial.println(F("calculate_key() called"));
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
        key.keyByte[i] = 0xFF & (sector_key_int >> (40 - i * 8));
    }
    return key;
}

typedef struct {
    byte data[3][16];
} sector_data;


bool read_sector(sector_data * sector_data, int sector_number, MFRC522::MIFARE_Key sector_key, MFRC522 &mfrc522) {
    Serial.println(F("read_sector() called"));
    MFRC522::StatusCode status;
    byte blocks[3];
    for (int i = 0; i < 3; i++) blocks[i] = sector_number * 4 + i;

    bool res;

    status = mfrc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, blocks[0], &sector_key, &(mfrc522.uid));
    if (status != MFRC522::STATUS_OK) {
        Serial.print(F("Authentication failed: "));
        Serial.println(mfrc522.GetStatusCodeName(status));
        for (int i = 0; i < 3; i++) {
            for (int j = 0; j < 16; j++) {
                (*sector_data).data[i][j] = 0xFF;
            }
        }
        res = false;
    } else {
        for (int i = 0; i < 3; i++) { //Iterate through blocks in the sector
            byte buffer_block[18];
            byte len = 18;

            //Read data from block
            status = mfrc522.MIFARE_Read(blocks[i], buffer_block, &len);
            if (status != MFRC522::STATUS_OK) {
                Serial.print(F("Reading failed: "));
                Serial.println(mfrc522.GetStatusCodeName(status));

                for (int i = 0; i < 3; i++) {
                    for (int j = 0; j < 16; j++) {
                        (*sector_data).data[i][j] = 0xFF;
                    }
                }
                res = false;
            } else {
                //Move data from buffer to sector_data for corresponding block
                for (int j = 0; j < 16; j++) {
                    (*sector_data).data[i][j] = buffer_block[j];
                }
                res = true;
            }
        }
    }

    return res;
}

typedef struct {
    byte book_id[16];
    byte asset_name[16];
    byte start_date[8];
    byte end_date[8];
} access_permit;

access_permit parse_sector_data(sector_data sector_data) {
    Serial.println("parse_sector_data() called");
    access_permit res;

    for (int i = 0; i < 16; i++) {
        res.book_id[i] = sector_data.data[2][i]; //book_id is in block 2
        res.asset_name[i] = sector_data.data[1][i]; //asset_name is in block 1
    }

    //    Serial.println("Asset name intarray:");
    //    for (int i = 0; i < 16; i++) {
    //        Serial.printf("%d\n", sector_data.data[1][i]);
    //    }

    for (int i = 0; i < 8; i++) {
        res.start_date[i] = sector_data.data[0][i]; //start_date is in block 0, byte 0-7
        res.end_date[i] = sector_data.data[0][i + 8]; //end_date is in block 0, byte 8-15
    }

    return res;
}

typedef struct {
    bool contains_permit[16]; //true if corresponding sector is successfully authed & read, false otherwise
    access_permit access_permits[16]; //contains the permits.
} card_contents; //Will be populated when iterating through all sectors.

card_contents iterate_sectors(MFRC522::MIFARE_Key sector_key, MFRC522 &mfrc522) {
    Serial.println(F("iterate_sectors() called"));
    card_contents card_contents;

    for (int sector = 0; sector < 16; sector++) {
        sector_data cur_sector_data;
        read_sector(&cur_sector_data, sector, sector_key, mfrc522);
        access_permit access_permit = parse_sector_data(cur_sector_data);
        if (access_permit.book_id[0] == 0xFF && access_permit.book_id[1] == 0xFF && access_permit.book_id[2] == 0xFF) { //sector doesn't contain permit
            card_contents.contains_permit[sector] = false;
            card_contents.access_permits[sector] = access_permit;

            Serial.println(F("Executing PICC_HaltA(), PCD_StopCrypto1, and ReadCardSerial"));
            byte buff[2];
            byte buff_size = 2;
            mfrc522.PCD_StopCrypto1();
            mfrc522.PICC_HaltA();
            delay(50);
            mfrc522.PICC_WakeupA(buff, &buff_size);
            delay(50);
            mfrc522.PICC_Select(&(mfrc522.uid), 0);
            delay(50);
        } else { //contains permit
            card_contents.contains_permit[sector] = true;
            card_contents.access_permits[sector] = access_permit;
        }
    }

    return card_contents;
}

String verify_request_body(card_contents card_contents, MFRC522 &mfrc522) {
    Serial.println(F("verify_request_body() called"));
    DynamicJsonDocument res(3072);
    byte uid[4];
    for (int i = 0; i < 4; i++) {
        uid[i] = mfrc522.uid.uidByte[i];
    }
    res["uid"] = bytearray_to_hex(uid, 4);
    JsonArray access_permits_arr = res.createNestedArray("access_permits");
    for (int i = 0; i < 16; i++) {
        if (card_contents.contains_permit[i]) {
            Serial.printf("Sector %d contains permit\n", i);
            JsonObject access_permit_obj = access_permits_arr.createNestedObject();
            access_permit_obj["sector"] = i;
            JsonObject access_permit_detail = access_permit_obj.createNestedObject("access_permit");
            access_permit_detail["book_id"] = bytearray_to_hex(card_contents.access_permits[i].book_id, 16);
            access_permit_detail["asset_name"] = bytearray_to_hex(card_contents.access_permits[i].asset_name, 16);
            access_permit_detail["start_date"] = bytearray_to_hex(card_contents.access_permits[i].start_date, 8);
            access_permit_detail["end_date"] = bytearray_to_hex(card_contents.access_permits[i].end_date, 8);
        }
    }
    String request_body;
    serializeJson(res, request_body);
    Serial.println(F("Serialize request body result:"));
    Serial.println(request_body);
    return request_body;
}

//void actuate_access(bool isPermitted) {
//    if (isPermitted) {
//        Serial.println(F("Permitted."));
//        if (thingState == 0) {
//            Serial.println(F("Changing state to HIGH"));
//            thingState = 1;
//        } else {
//            Serial.println(F("Changing state to LOW"));
//            thingState = 0;
//        }
//        digitalWrite(thingPin, thingState);
//    } else {
//        Serial.println(F("Not permitted!"));
//    }
//}
