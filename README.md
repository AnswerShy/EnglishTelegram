# Telegram bot for english learning

# Start
To start using bot create .env file in root with params:
```json
TELEGRAM_API_KEY = "Key for your TG bot"

AI_API_KEY="AI API key"
AI_API_MODEL="AI Model thats you want to use"
AI_API_URL="URL to your AI API"

MONGODB_URI="MONGODB URI for save users"
```
After that start with:
```bash
docker compose up --build
```
If you need to reload bot:
```bash
docker compose down
docker compose build --no-cache
docker compose up
```
or
```bash
bash rebuild-docker.sh
```


