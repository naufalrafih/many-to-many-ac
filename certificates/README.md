Untuk membuat SSL certificate dan private key-nya menggunakan openSSL (version >=1.1.1):

    openssl req -x509 -newkey rsa:4096 -nodes \
    -out cert.pem -keyout key.pem -days 365 \
    -subj "/C=ID/ST=West Java/L=Bandung/O=ITB/OU=STEI/CN=10.0.0.5" \
    -addext 'subjectAltName=IP:10.0.0.5'

Option ```-subj``` digunakan untuk mengatur field sertifikat:

| Field | Meaning             |
| ----- | ------------------- |
| /C=   | Country             |
| /ST=  | State               |
| /L=   | Location            |
| /O=   | Organization        |
| /OU=  | Organizational Unit |
| /CN=  | Common Name         |

Option ```-addext 'subjectAltName=...'``` digunakan untuk mengatur field subjectAltName