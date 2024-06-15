Build & run all services:

1. git clone https://github.com/lIkesimba9/web_demo.git
2. [Optionally: for using "Gemini"-network via VPN] Create and put ```config``` folder (with ```auth.txt``` and ```credentials.ovpn```) to ```./web_demo/gemini_proxy```

3. Start services:

Optionaly: ```RUN_OLLAMA```
Optionaly: ```<you_google_api_token>``` (from ```https://aistudio.google.com/app/apikey```)
Required: ```<you_telegram_bot_token>```

Required: openssl
```
chmod +x start_services.sh
```

YOLOV8
./start_services.sh ```<you_telegram_bot_token>```
```

YOLOV8 + GEMINI
./start_services.sh ```<you_telegram_bot_token>``` ```<you_google_api_token>```


YOLOV8 + GEMINI + OLLAMA
```
./start_services.sh ```<you_telegram_bot_token>``` ```<you_google_api_token>``` RUN_OLLAMA
```

4. Run in browser:
```
http://localhost:8004/docs
```
