import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

TOKEN = "7300998241:AAEKarzMXoz9Sgi6f1RRpA-HoJ4-oatDgVE"
WEATHER_API_KEY = "12f1c000ced74607ac3135014251503"
user_data = {}

async def start(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton("Укажите ваш регион", callback_data="set_region")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привет! Чтобы узнать прогноз, сначала выберите ваш регион.", reply_markup=reply_markup)

async def receive_region(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    city = update.message.text
    user_data[user_id] = city

    keyboard = [
        [KeyboardButton("Текущая погода")],
        [KeyboardButton("Прогноз на день")],
        [KeyboardButton("Прогноз на 3 дня")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

    await update.message.reply_text(f"Ваш город: {city}\nВыберите тип прогноза:", reply_markup=reply_markup)

    def get_clothing_recommendation(temp):
        if temp > 25:
            recommendation = "👕 Сегодня жарко! Надевайте футболку, шорты и солнцезащитные очки. Не забудьте воду!"
        elif temp > 15:
            recommendation = "🧥 Сегодня тепло. Надевайте легкую куртку или кофту, можно джинсы."
        elif temp > 5:
            recommendation = "🧣 Прохладно. Рекомендуем куртку, свитер и закрытую обувь."
        elif temp > -5:
            recommendation = "🧥 Холодно! Надевайте теплую куртку, шапку и перчатки."
        else:
            recommendation = "❄ Очень холодно! Нужна теплая одежда, перчатки, шарф и зимняя обувь."
        # if "rain" in condition or "дождь" in condition:
        #     return "☔ Похоже на дождь. Возьмите зонтик или дождевик!"
        # elif "snow" in condition or "снег" in condition:
        #     return "❄ На улице снег. Наденьте теплую обувь и перчатки!"
    return recommendation
def get_current_weather(city):
    url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}&lang=ru"
    response = requests.get(url).json()

    if "error" in response:
        return "Город не найден."

    temp = response["current"]["temp_c"]
    condition = response["current"]["condition"]["text"]
    recommendation = get_clothing_recommendation(temp)

    return f"🌍 {city}\n🌡 {temp}°C\n☁️ {condition}\n👕 {recommendation}"
def get_daily_forecast(city):
    url = f"http://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={city}&days=1&lang=ru"
    response = requests.get(url).json()

    if "error" in response:
        return "Город не найден. Проверьте название."

    forecast = response['forecast']['forecastday'][0]['day']
    max_temp = forecast['maxtemp_c']
    min_temp = forecast['mintemp_c']
    avg_temp = forecast['avgtemp_c']
    condition = forecast['condition']['text']
    def get_clothing_recommendation(avg_temp):
        if avg_temp > 25:
            return "👕 Сегодня жарко! Надевайте футболку, шорты и солнцезащитные очки. Не забудьте воду!"
        elif avg_temp > 15:
            return "🧥 Сегодня тепло. Надевайте легкую куртку или кофту, можно джинсы."
        elif avg_temp > 5:
            return "🧣 Прохладно. Рекомендуем куртку, свитер и закрытую обувь."
        elif avg_temp > -5:
            return "🧥 Холодно! Надевайте теплую куртку, шапку и перчатки."
        else:
            return "❄ Очень холодно! Нужна теплая одежда, перчатки, шарф и зимняя обувь."
        # if "rain" in condition or "дождь" in condition:
        #     return "☔ Похоже на дождь. Возьмите зонтик или дождевик!"
        # elif "snow" in condition or "снег" in condition:
        #     return "❄ На улице снег. Наденьте теплую обувь и перчатки!"
    recommendation = get_clothing_recommendation(avg_temp, condition)
    return f"🌍 Город: {city}🌡 Макс. температура: {max_temp}°C❄️ Мин. температура: {min_temp}°C☀️ {recommendation}"

def get_future_forecast(city, days=3):
    url = f"http://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={city}&days={days}&lang=ru"
    response = requests.get(url).json()

    if "error" in response:
        return "Город не найден. Проверьте название."

    forecast = response['forecast']['forecastday'][0]['day']
    max_temp = forecast['maxtemp_c']
    min_temp = forecast['mintemp_c']
    avg_temp = forecast['avgtemp_c']
    def get_clothing_recommendation(avg_temp):
        if avg_temp > 25:
            return "👕 Сегодня жарко! Надевайте футболку, шорты и солнцезащитные очки. Не забудьте воду!"
        elif avg_temp > 15:
            return "🧥 Сегодня тепло. Надевайте легкую куртку или кофту, можно джинсы."
        elif avg_temp > 5:
            return "🧣 Прохладно. Рекомендуем куртку, свитер и закрытую обувь."
        elif avg_temp > -5:
            return "🧥 Холодно! Надевайте теплую куртку, шапку и перчатки."
        else:
            return "❄ Очень холодно! Нужна теплая одежда, перчатки, шарф и зимняя обувь."
    recommendation = get_clothing_recommendation(avg_temp)
    return f"📅 Прогноз на {days} дня вперед\n🌍 Город: {city}\n🌡 Макс. температура: {max_temp}°C\n❄️ Мин. температура: {min_temp}°C\n☀️ Погода:{recommendation}"

async def handle_text(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    text = update.message.text

    if user_id not in user_data:
        await receive_region(update, context)
    else:
        await update.message.reply_text(get_current_weather(user_data[user_id]))

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("Бот запущен...")
    app.run_polling()

if name == "__main__":
    main()