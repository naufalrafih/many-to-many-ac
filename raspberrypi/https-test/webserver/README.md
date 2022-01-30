1. Generate pem files: <br>
```openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365```

2. Run ```pipenv install -r requirements.txt```
3. Allow firewall port 5000
4. Run ```pipenv run python3 app.py```
5. Restart flask if not responding
