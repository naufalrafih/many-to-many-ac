import os
from Crypto.Util import number

def generate_keys(a, c, u, d):

    ukey = pow(a,u,c)
    dkey = pow(a,d,c)
    keyij_u = pow(ukey,d,c)
    keyij_d = pow(dkey,u,c)
    len_keyij = round(len(hex(keyij_u)[2:])/2)

    if (keyij_u == keyij_d) and (len_keyij == 6):
        return (ukey, dkey, keyij_u), False 
    else:
        return  (0, 0, 0), True

def generate_entity_key(a, id, c):
    return pow(a, id, c)

def generate_keyij(key, id, c):
    keyij = pow(key, id, c)
    len_keyij = round(len(hex(keyij)[2:])/2)

    if (len_keyij == 6):
        return keyij, False
    else:
        return 0, True

a = number.getPrime(47, os.urandom)
c = number.getPrime(48, os.urandom)
u = int.from_bytes(os.urandom(4),'big')
d = int.from_bytes(os.urandom(4),'big')

(ukey, dkey, keyij), error = generate_keys(a, c, u, d)

if not error:
    print(f"u:{u}")
    print(f"d:{d}")
    print(f"a:{a}")
    print(f"c:{c}")
    print(f"ukey:{ukey}")
    print(f"dkey:{dkey}")
    print(f"keyij:{keyij}")
else:
    print("Error kale")


json_array = {
    "access_permits":[
        {
            "sector": 0,
            "access_permit": {
                "book_id": "9ab2938abc",
                "asset_name": "batu",
                "start_date": "08032022",
                "end_date": "12032022",
            }
        },
        {
            "sector": 14,
            "access_permit": {
                "book_id": "8sbj108ala",
                "asset_name": "batu",
                "start_date": "10032022",
                "end_date": "12032022"
            }
        }
    ],
    "uid": "274w869hfun"
}

json_array = '{"access_permits":[{"sector": 0,"access_permit": {"book_id":"9ab2938abc","asset_name":"batu","start_date":"08032022","end_date":"12032022"}},{"sector": 14,"access_permit": {"book_id":"9ab2938abc","asset_name":"batu","start_date":"08032022","end_date":"12032022"}}]}'
