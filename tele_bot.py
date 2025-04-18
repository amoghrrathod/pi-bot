from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackContext,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)
import aiohttp

# Bot token and API key
tg_token = "7853128155:AAGYYN8Mokc6-8W97O2HuqDurUovIjZBQtE"
weather_api_key = "6053eb035f2240308c5171324242310"

# Conversation states
SELECTING_CITY = 1

# Default cities that users can quickly select
DEFAULT_CITIES = [
    "Cairo",
    "Lagos",
    "Kinshasa",
    "Johannesburg",
    "Nairobi",
    "Casablanca",
    "Accra",
    "Addis Ababa",
    "Algiers",
    "Tunis",
    "Khartoum",
    "Dar es Salaam",
    "Luanda",
    "Abidjan",
    "Dakar",
    "Cape Town",
    "Durban",
    "Port Elizabeth",
    "Pretoria",
    "Marrakesh",
    "Tokyo",
    "Delhi",
    "Shanghai",
    "Mumbai",
    "Beijing",
    "Dhaka",
    "Osaka",
    "Karachi",
    "Istanbul",
    "Manila",
    "Seoul",
    "Jakarta",
    "Guangzhou",
    "Shenzhen",
    "Bangkok",
    "Ho Chi Minh City",
    "Taipei",
    "Hong Kong",
    "Singapore",
    "Kuala Lumpur",
    "Bangalore",
    "Hyderabad",
    "Chennai",
    "Kolkata",
    "Lahore",
    "Riyadh",
    "Jeddah",
    "Dubai",
    "Abu Dhabi",
    "Doha",
    "Kuwait City",
    "Tehran",
    "Baghdad",
    "Kyoto",
    "Busan",
    "Yokohama",
    "Nagoya",
    "Sapporo",
    "Fukuoka",
    "Hanoi",
    "London",
    "Paris",
    "Madrid",
    "Barcelona",
    "Berlin",
    "Rome",
    "Milan",
    "Athens",
    "Amsterdam",
    "Brussels",
    "Vienna",
    "Munich",
    "Frankfurt",
    "Hamburg",
    "Zurich",
    "Geneva",
    "Copenhagen",
    "Stockholm",
    "Oslo",
    "Helsinki",
    "Prague",
    "Warsaw",
    "Budapest",
    "Bucharest",
    "Sofia",
    "Belgrade",
    "Dublin",
    "Edinburgh",
    "Glasgow",
    "Lisbon",
    "Porto",
    "Moscow",
    "St. Petersburg",
    "Kiev",
    "Minsk",
    "Valencia",
    "Seville",
    "Naples",
    "Turin",
    "Florence",
    "Lyon",
    "Marseille",
    "Nice",
    "Liverpool",
    "Manchester",
    "New York City",
    "Los Angeles",
    "Chicago",
    "Toronto",
    "Mexico City",
    "Houston",
    "Philadelphia",
    "Phoenix",
    "San Antonio",
    "San Diego",
    "Dallas",
    "San Jose",
    "Austin",
    "Jacksonville",
    "San Francisco",
    "Indianapolis",
    "Columbus",
    "Charlotte",
    "Seattle",
    "Denver",
    "Washington DC",
    "Boston",
    "El Paso",
    "Nashville",
    "Detroit",
    "Portland",
    "Las Vegas",
    "Memphis",
    "Louisville",
    "Baltimore",
    "Milwaukee",
    "Albuquerque",
    "Tucson",
    "Fresno",
    "Sacramento",
    "Montreal",
    "Calgary",
    "Ottawa",
    "Edmonton",
    "Winnipeg",
    "Vancouver",
    "Quebec City",
    "Hamilton",
    "Guadalajara",
    "Monterrey",
    "São Paulo",
    "Buenos Aires",
    "Rio de Janeiro",
    "Bogotá",
    "Lima",
    "Santiago",
    "Caracas",
    "Belo Horizonte",
    "Brasília",
    "Recife",
    "Porto Alegre",
    "Montevideo",
    "Córdoba",
    "Medellín",
    "Cali",
    "Quito",
    "Guayaquil",
    "La Paz",
    "Santa Cruz",
    "Asunción",
    "Fortaleza",
    "Salvador",
    "Curitiba",
    "Manaus",
    "Belém",
    "Sydney",
    "Melbourne",
    "Brisbane",
    "Perth",
    "Adelaide",
    "Auckland",
    "Wellington",
    "Christchurch",
    "Gold Coast",
    "Canberra",
    "Hobart",
    "Darwin",
    "Cairns",
    "Wollongong",
    "Newcastle",
    "Suva",
    "Port Moresby",
    "Nouméa",
    "Honolulu",
    "Papeete",
]


async def start_command(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Hello! I am your Telegram Bot.")
    await help_command(update, context)


async def echo(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("How's it going?")


async def weather_cmd(update: Update, context: CallbackContext) -> int:
    """Handle the /weather command - offer city selection options"""
    # Check if a city was provided directly with the command
    if context.args and len(context.args) > 0:
        city = " ".join(context.args)
        await get_weather(update, context, city)
        return ConversationHandler.END

    # Otherwise show city selection options
    keyboard = []
    # Create rows with 2 buttons each
    for i in range(0, len(DEFAULT_CITIES), 2):
        row = []
        row.append(
            InlineKeyboardButton(
                DEFAULT_CITIES[i], callback_data=f"city_{DEFAULT_CITIES[i]}"
            )
        )
        if i + 1 < len(DEFAULT_CITIES):
            row.append(
                InlineKeyboardButton(
                    DEFAULT_CITIES[i + 1], callback_data=f"city_{DEFAULT_CITIES[i + 1]}"
                )
            )
        keyboard.append(row)

    # Add a button to enter custom city
    keyboard.append(
        [InlineKeyboardButton("Enter a different city", callback_data="custom_city")]
    )

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Please select a city or enter a custom location:", reply_markup=reply_markup
    )
    return SELECTING_CITY


async def button_callback(update: Update, context: CallbackContext) -> int:
    """Handle button selection"""
    query = update.callback_query
    await query.answer()

    if query.data.startswith("city_"):
        city = query.data.replace("city_", "")
        await get_weather(update, context, city, is_callback=True)
        return ConversationHandler.END
    elif query.data == "custom_city":
        await query.edit_message_text("Please type the name of the city:")
        return SELECTING_CITY


async def text_input(update: Update, context: CallbackContext) -> int:
    """Handle text input for custom city"""
    city = update.message.text
    await get_weather(update, context, city)
    return ConversationHandler.END


async def get_weather(
    update: Update, context: CallbackContext, city: str, is_callback: bool = False
) -> None:
    """Fetch and format weather data for the specified city"""
    try:
        weather_url = (
            f"http://api.weatherapi.com/v1/current.json?key={weather_api_key}&q={city}"
        )

        async with aiohttp.ClientSession() as session:
            async with session.get(weather_url) as response:
                if response.status != 200:
                    message = f"Failed to fetch weather data for {city}. Please check the city name and try again."
                    if is_callback:
                        await update.callback_query.edit_message_text(message)
                    else:
                        await update.message.reply_text(message)
                    return

                data = await response.json()

                # Extract weather details
                location = data["location"]["name"]
                country = data["location"]["country"]
                temp_c = data["current"]["temp_c"]
                temp_f = data["current"]["temp_f"]
                condition = data["current"]["condition"]["text"]
                humidity = data["current"]["humidity"]
                wind_kph = data["current"]["wind_kph"]
                feels_like = data["current"]["feelslike_c"]

                weather_message = (
                    f"🌤 Weather in {location}, {country}:\n"
                    f"🌡 Temperature: {temp_c}°C ({temp_f}°F)\n"
                    f"🤔 Feels like: {feels_like}°C\n"
                    f"☁ Condition: {condition}\n"
                    f"💧 Humidity: {humidity}%\n"
                    f"💨 Wind Speed: {wind_kph} km/h"
                )

                if is_callback:
                    await update.callback_query.edit_message_text(weather_message)
                else:
                    await update.message.reply_text(weather_message)

    except Exception as e:
        error_message = f"Error fetching weather data: {e}"
        if is_callback:
            await update.callback_query.edit_message_text(error_message)
        else:
            await update.message.reply_text(error_message)


async def stocks(update: Update, context: CallbackContext):
    """Fetch and display top 5 stocks based on daily percentage change."""
    stock_symbols = ["AAPL", "GOOGL", "AMZN", "MSFT", "TSLA"]  # Can be expanded
    api_key = "H1XE0RT2V2MA1160"

    stock_data = []

    async with aiohttp.ClientSession() as session:
        for symbol in stock_symbols:
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
            async with session.get(url) as response:
                if response.status != 200:
                    continue  # Skip if request fails

                data = await response.json()
                if "Global Quote" in data:
                    quote = data["Global Quote"]
                    price = float(quote["05. price"])
                    change_percent = float(quote["10. change percent"].replace("%", ""))

                    stock_data.append(
                        {"symbol": symbol, "price": price, "change": change_percent}
                    )

    # Sort by highest percentage change
    stock_data.sort(key=lambda x: x["change"], reverse=True)

    # Format response
    message = "📊 **Top 5 Stocks Today:**\n"
    for stock in stock_data[:5]:
        message += f"📈 {stock['symbol']}: ${stock['price']} ({stock['change']}% 🔺)\n"

    await update.message.reply_text(message)


async def help_command(update: Update, context: CallbackContext) -> None:
    help_text = (
        "Available commands:\n\n"
        "/start - Begin interacting with the bot\n"
        "/weather - Get weather information\n"
        "  You can use it in these ways:\n"
        "  • /weather - Shows city selection menu\n"
        "  • /weather Paris - Gets weather for Paris directly\n"
        "/help - Shows this help message"
    )
    await update.message.reply_text(help_text)


async def cancel(update: Update, context: CallbackContext) -> int:
    """Cancel the conversation"""
    await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END


if __name__ == "__main__":
    print("Starting the bot...")

    app = Application.builder().token(tg_token).build()

    # Create conversation handler for weather command
    weather_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("weather", weather_cmd)],
        states={
            SELECTING_CITY: [
                CallbackQueryHandler(button_callback),
                MessageHandler(filters.TEXT & ~filters.COMMAND, text_input),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Add handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(weather_conv_handler)
    app.add_handler(CommandHandler("stocks", stocks))
    app.add_handler(CommandHandler("help", help_command))

    print("Looking for new messages...")
    app.run_polling()
