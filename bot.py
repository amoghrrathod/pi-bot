from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEATHER_KEY = os.getenv("WEATHER_KEY")
STOCK_KEY = os.getenv("STOCK_KEY")

if not all([BOT_TOKEN, WEATHER_KEY, STOCK_KEY]):
    raise ValueError(
        "Dawg you need to add all the keys for this to work. Check your .env file."
    )


async def start_cmd(update: Update, context):
    await update.message.reply_text("Hey! It's ME! Try /help to see what i can do.")


async def echo_vibe(update: Update, context):
    await update.message.reply_text(
        "Dawg use /help to see what I can do. I'm not responding to random stuff."
    )


async def help_cmd(update: Update, context):
    help_text = (
        "Here's the help:\n"
        "/start - to check im alive\n"
        "/weather <city> - like '/weather yokohama' for weather\n"
        "/stocks - checks top 5 stocks\n"
        "/help - this list\n"
        "Just type anything else, and I'll not respond to yo ahh\n"
    )
    await update.message.reply_text(help_text)


async def weather_cmd(update: Update, context):
    if not context.args:
        await update.message.reply_text("Yo, bruh, throw me a city like /weather Tokyo")
        return

    city = " ".join(context.args)  # handles stuff like mumbai
    await grab_weather(update, context, city)


async def grab_weather(update: Update, context, city):
    try:
        url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_KEY}&q={city}"
        async with aiohttp.ClientSession() as sesh:
            async with sesh.get(url) as resp:
                if resp.status != 200:
                    await update.message.reply_text(
                        f"Dawg, '{city}' ain't showing up'.Check yo spelling."
                    )
                    return

                data = await resp.json()

                spot = data["location"]["name"]
                country = data["location"]["country"]
                temp_c = data["current"]["temp_c"]
                temp_f = data["current"]["temp_f"]
                mood = data["current"]["condition"]["text"]
                humid = data["current"]["humidity"]
                windy = data["current"]["wind_kph"]
                feels_like = data["current"]["feelslike_c"]

                # message schema
                weather_report = (
                    f"🌈 Weather in {spot}, {country}, fam:\n"
                    f"🔥 Temp: {temp_c}°C ({temp_f}°F)\n"
                    f"😎 Feels like: {feels_like}°C\n"
                    f"🌤️ Mood: {mood}\n"
                    f"💦 Humidity: {humid}%\n"
                    f"💨 Wind: {windy} km/h"
                )
                await update.message.reply_text(weather_report)

    except Exception as whoops:
        await update.message.reply_text(f"Ay, somethin' crashed: {whoops}")


async def stocks_cmd(update: Update, context):
    tickers = [
        "RELIANCE.BOM",
        "TCS.BOM",
        "HDFCBANK.BOM",
        "INFY.BOM",
        "BHARTIARTL.BOM",
        "AAPL",
        "GOOGL",
        "MSFT",
        "AMZN",
    ]
    stock_juice = []
    async with aiohttp.ClientSession() as sesh:
        for ticker in tickers:
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={STOCK_KEY}"
            async with sesh.get(url) as resp:
                if resp.status != 200:
                    continue
                data = await resp.json()
                if "Global Quote" in data and data["Global Quote"]:
                    quote = data["Global Quote"]
                    price = float(quote["05. price"])
                    change = float(quote["10. change percent"].replace("%", ""))
                    stock_juice.append(
                        {"ticker": ticker, "price": price, "change": change}
                    )
    stock_juice.sort(key=lambda x: x["change"], reverse=True)
    msg = "📈 Stock vibes, my dawg:\n"
    for stock in stock_juice[:5]:
        ticker_name = stock["ticker"].split(".")[0]
        msg += f"💸 {ticker_name}: ${stock['price']:.2f} ({stock['change']:.2f}% 🔥)\n"
    if not stock_juice:
        msg = "No stock scenes for today API is dying."
    await update.message.reply_text(msg)


def lessgo():
    print("MMMMM Bot is starting...")
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("weather", weather_cmd))
    app.add_handler(CommandHandler("stocks", stocks_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, echo_vibe)
    )  # catch random texts

    print("Wsg! How can I help you today?")
    app.run_polling()


if __name__ == "__main__":
    lessgo()
