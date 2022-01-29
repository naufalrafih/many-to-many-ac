1. Generate pem files: <br>
```openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365```

2. Allow firewall port 5000
3. Restart flask if occasionally
