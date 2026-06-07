import requests
import time

TELEGRAM_TOKEN = "توکن جدیدت رو اینجا بذار"
WEATHER_API_KEY = "کلید openweathermap ات رو اینجا بذار"

CITIES = {
    "شیراز": "Shiraz",
    "تهران": "Tehran",
    "اصفهان": "Isfahan",
    "مشهد": "Mashhad",
    "تبریز": "Tabriz",
    "کیش": "Kish",
}

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": text})

def get_weather(city_en):
    url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": f"{city_en},IR",
        "appid": WEATHER_API_KEY,
        "units": "metric",
        "cnt": 7
    }
    r = requests.get(url, params=params)
    return r.json()

def best_day(data):
    best = None
    best_score = -99

    for item in data["list"]:
        temp = item["main"]["temp"]
        humidity = item["main"]["humidity"]
        weather = item["weather"][0]["main"]
        score = 0

        if 18 <= temp <= 28:
            score += 3
        elif 15 <= temp <= 32:
            score += 1

        if weather == "Clear":
            score += 3
        elif weather == "Clouds":
            score += 1
        elif weather in ["Rain", "Thunderstorm"]:
            score -= 2

        if humidity < 50:
            score += 2
        elif humidity < 70:
            score += 1

        if score > best_score:
            best_score = score
            best = item

    return best

def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    params = {"timeout": 10}
    if offset:
        params["offset"] = offset
    r = requests.get(url, params=params)
    return r.json()

def process(chat_id, text):
    found_city = None
    found_city_en = None

    for city_fa, city_en in CITIES.items():
        if city_fa in text:
            found_city = city_fa
            found_city_en = city_en
            break

    if not found_city:
        send_message(chat_id,
            "سلام! 👋\n\n"
            "بنویس مثلاً: میخوام برم شیراز\n\n"
            "شهرهایی که میشناسم:\n"
            "شیراز، تهران، اصفهان، مشهد، تبریز، کیش"
        )
        return

    try:
        data = get_weather(found_city_en)
        day = best_day(data)

        temp = day["main"]["temp"]
        humidity = day["main"]["humidity"]
        weather = day["weather"][0]["description"]
        date = day["dt_txt"].split(" ")[0]

        if temp <= 28:
            advice = "✅ هوا عالیه، برو!"
        else:
            advice = "⚠️ کمی گرمه، آب زیاد ببر!"

        msg = (
            f"🌤 بهترین روز برای سفر به {found_city}:\n\n"
            f"📅 تاریخ: {date}\n"
            f"🌡 دما: {temp:.0f} درجه\n"
            f"💧 رطوبت: {humidity}%\n"
            f"☁️ وضعیت: {weather}\n\n"
            f"{advice}"
        )
        send_message(chat_id, msg)

    except Exception as e:
        print(f"خطا: {e}")
        send_message(chat_id, "مشکلی پیش اومد، دوباره امتحان کن.")

print("ربات شروع به کار کرد... 🤖")
offset = None

while True:
    try:
        updates = get_updates(offset)
        if updates.get("result"):
            for update in updates["result"]:
                offset = update["update_id"] + 1
                if "message" in update and "text" in update["message"]:
                    chat_id = update["message"]["chat"]["id"]
                    text = update["message"]["text"]
                    print(f"پیام: {text}")
                    process(chat_id, text)
        time.sleep(2)
    except Exception as e:
        print(f"خطا: {e}")
        time.sleep(5)
