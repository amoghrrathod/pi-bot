# Pi-Bot – Your Chill Personal Telegram Assistant

A Telegram bot hosted on my Raspberry Pi that hits you with:

🌦 Live weather updates  
📈 Real-time stock prices
🙃 Sass when you try to chat randomly

Built in Python with full async support (`aiohttp` + `python-telegram-bot`). Runs headless on Raspberry Pi, so I can message it from anywhere in the world and get structured, useful info back.

## 🧠 Features

- `/weather <city>` — grabs weather from WeatherAPI
- `/stocks` — pulls live stock data from AlphaVantage
- Custom bot responses with a personal tone (because boring bots are so 2020)
- Handles errors, invalid city names, and API fails gracefully

## ⚙️ Stack

- Python
- Asyncio + aiohttp
- Telegram Bot API
- Hosted on Raspberry Pi
- WeatherAPI + AlphaVantage APIs

## 🚀 Run It

```bash
pip install python-telegram-bot aiohttp load_dotenv
# Make a .env file add all the API Keys- BOT_TOKEN, WEATHER_KEY & STOCK_KEY (remeber to not keep any spaces between the equal(=) signs)
python bot.py
```
