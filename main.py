import os
import telebot
from telebot import types
from flask import Flask
import threading

# Flask veb-server (Render o'chib qolmasligi uchun)
app = Flask(__name__)

# Bot sozlamalari
TOKEN = '8608266628:AAGfyMpC4w90S9GHnNsDpXULff20tlcLBuc'
bot = telebot.TeleBot(TOKEN)

# 🛠 TELEGRAM ID RAQAMINGIZ
ADMIN_ID = 6807375870  

# Foydalanuvchilar ro'yxati uchun vaqtinchalik baza
USERS_DB = set()
admin_state = {}

@app.route('/')
def home():
    return "Bot muvaffaqiyatli ishlamoqda..."

# Stars paketlari va narxlari (so'mda)
STARS_PRODUCTS = {
    "stars_50":  {"title": "50 ⭐️ Stars", "price": 16000,  "amount": 50},
    "stars_100": {"title": "100 ⭐️ Stars", "price": 35000, "amount": 100},
    "stars_150": {"title": "150 ⭐️ Stars", "price": 55000, "amount": 150},
    "stars_250": {"title": "250 ⭐️ Stars", "price": 70000, "amount": 250},
    "stars_350": {"title": "350 ⭐️ Stars", "price": 95000, "amount": 350},
    "stars_500": {"title": "500 ⭐️ Stars", "price": 135000, "amount": 500},
    "stars_1000": {"title": "1000 ⭐️ Stars", "price": 240000, "amount": 1000}
}

# 🌟 PASTDAGI TUGMALAR (Klaviatura)
def get_reply_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    btn_prices = types.KeyboardButton("⭐️ STARS narxlari")
    btn_admin = types.KeyboardButton("👤 Admin bilan bog'lanish")
    btn_reviews = types.KeyboardButton("💬 Fikrlar va sharhlar")
    btn_channel = types.KeyboardButton("📢 Bizning kanal")
    
    markup.add(btn_prices)
    markup.add(btn_admin, btn_reviews)
    markup.add(btn_channel)
    return markup

# Admin panel menyusi
def get_admin_menu():
    markup = types.InlineKeyboardMarkup()
    btn_send_ads = types.InlineKeyboardButton("📣 Reklama (Rassilka) yuborish", callback_data="admin_send_ads")
    btn_stats = types.InlineKeyboardButton("📊 Bot statistikasi", callback_data="admin_stats")
    markup.add(btn_send_ads)
    markup.add(btn_stats)
    return markup

# /start buyrug'i kelganda
@bot.message_handler(commands=['start'])
def start_message(message):
    USERS_DB.add(message.chat.id)
    
    welcome_text = (
        "🌟 Telegram Stars Savdo do'koniga xush kelibsiz!\n\n"
        "🤑 Stars paketlarini Telegram'dan ancha arzon narxda oling"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_reply_menu(), parse_mode="Markdown")

# /admin paneli
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(message.chat.id, "🛠 Xush kelibsiz Admin!\nBotni boshqarish paneli:", reply_markup=get_admin_menu(), parse_mode="Markdown")

# 🌟 PASTDAGI TUGMALAR BOSILGANDA ISHLAYDIGAN QISM
@bot.message_handler(func=lambda message: message.text in ["⭐️ STARS narxlari", "👤 Admin bilan bog'lanish", "💬 Fikrlar va sharhlar", "📢 Bizning kanal"])
def handle_reply_buttons(message):
    if message.text == "⭐️ STARS narxlari":
        markup = types.InlineKeyboardMarkup(row_width=2)
        buttons = []
        for key, product in STARS_PRODUCTS.items():
            btn = types.InlineKeyboardButton(f"{product['title']} — {product['price']:,} so'm", callback_data=f"buy_{key}")
            buttons.append(btn)
        markup.add(*buttons)
        bot.send_message(message.chat.id, "⭐️ Kerakli Stars paketini tanlang:", reply_markup=markup, parse_mode="Markdown")
        
    elif message.text == "👤 Admin bilan bog'lanish":
        bot.send_message(message.chat.id, "🎧 Savollar, takliflar yoki muammolar bo'yicha admin bilan bog'laning:\n👉 @muhammad_16")
        
    elif message.text == "💬 Fikrlar va sharhlar":
        bot.send_message(message.chat.id, "💬 Mijozlarimiz tomonidan qoldirilgan fikrlar va sharhlarni ko'rish uchun:\n👉 https://t.me/tg_yulduz_savdo")
        
    elif message.text == "📢 Bizning kanal":
        bot.send_message(message.chat.id, "📢 Yangiliklar, aksiyalar va eng so'nggi narxlardan xabardor bo'lish uchun kanalimiz:\n👉 https://t.me/tg_yulduz_savdo")

# Admindan reklama matnini qabul qilish
@bot.message_handler(func=lambda message: admin_state.get(message.chat.id) == "waiting_for_ad")
def receive_ad_text(message):
    admin_state[message.chat.id] = None
    success_count = 0
    bot.send_message(message.chat.id, "⏳ Reklama barcha foydalanuvchilarga yuborilmoqda...")
    
    for user_id in USERS_DB:
        try:
            bot.copy_message(chat_id=user_id, from_chat_id=message.chat.id, message_id=message.message_id)
            success_count += 1
        except:
            continue
    bot.send_message(message.chat.id, f"✅ Reklama yakunlandi!\n\n👥 Muvaffaqiyatli yetkazildi: {success_count} ta foydalanuvchiga.")

# Inline tugmalar boshqaruvi (Paket tanlanganda sizga havola beradi)
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    if call.data == "admin_send_ads" and call.message.chat.id == ADMIN_ID:
        admin_state[call.message.chat.id] = "waiting_for_ad"
        bot.send_message(call.message.chat.id, "📝 Reklama xabarini yuboring (Matn, rasm yoki video):")
        bot.answer_callback_query(call.id)
        
    elif call.data == "admin_stats" and call.message.chat.id == ADMIN_ID:
        stats_text = f"📊 Bot statistikasi:\n\n👥 Jami foydalanuvchilar: {len(USERS_DB)} ta\n🟢 Bot holati: Aktiv"
        bot.send_message(call.message.chat.id, stats_text)
        bot.answer_callback_query(call.id)
        
    # Xaridor paketni tanlaganda to'g'ridan-to'g'ri sizga yo'naltirish qismi
    elif call.data.startswith("buy_"):
        product_key = call.data.split("_", 1)[1]
        product = STARS_PRODUCTS.get(product_key)
        
        if product:
            payment_text = (
                f"🛒 Siz tanladingiz: {product['title']}\n"
                f"💰 Sotib olish narxi: {product['price']:,} so'm\n\n"
                f"🛍 Ushbu paketni sotib olish uchun hozir adminimizga yozing. Admin sizga karta raqamini beradi va pul o'tishi bilan Stars'ni tashlab beradi:\n\n"
                f"👉 Admin bilan bog'lanish: @muhammad_16"
            )
            bot.send_message(call.message.chat.id, payment_text, parse_mode="Markdown")
            bot.answer_callback_query(call.id)

def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
