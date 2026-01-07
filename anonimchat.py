import telebot
from telebot import types
import random

# === BOT MA'LUMOTLARI ===
BOT_TOKEN = "8518056832:AAHItL8m3WSWdTN_zsyx-YTjGpImpTp7XwY"
ADMIN_ID = 6576561907  # O'zingizning Telegram ID'ingizni qo'ying

bot = telebot.TeleBot(BOT_TOKEN)

# === XOTIRA ===
registered_users = {}   # {user_id: phone_number}
waiting_users = []       # Kutayotganlar ro'yxati
active_chats = {}        # {user_id: partner_id}


# === START BUYRUG'I ===
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id

    if user_id == ADMIN_ID:
        bot.send_message(message.chat.id, "👑 Salom, Admin! Siz tizimga kirdingiz.")
        return

    if user_id in registered_users:
        bot.send_message(
            message.chat.id,
            "👋 Qaytganingizdan xursandmiz!\n\n"
            "👉 /search - suhbatdosh topish\n"
            "❌ /stop - chatni to‘xtatish"
        )
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        contact_btn = types.KeyboardButton("📞 Raqamni ulashish", request_contact=True)
        markup.add(contact_btn)
        bot.send_message(
            message.chat.id,
            "🔒 Iltimos, tizimdan foydalanish uchun telefon raqamingizni ulashing:",
            reply_markup=markup
        )


# === KONTAKT QABUL QILISH ===
@bot.message_handler(content_types=['contact'])
def contact_handler(message):
    user_id = message.from_user.id
    phone = message.contact.phone_number

    registered_users[user_id] = phone
    bot.send_message(
        message.chat.id,
        f"✅ Raqamingiz qabul qilindi: +{phone}\n"
        "Endi siz tizimdan foydalana olasiz.\n\n"
        "👉 /search - suhbatdosh topish\n"
        "❌ /stop - chatni to‘xtatish",
        reply_markup=types.ReplyKeyboardRemove()
    )


# === ADMIN PANEL ===
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        return
    online = len(waiting_users)
    active = len(active_chats) // 2
    total_users = len(registered_users)

    bot.send_message(
        message.chat.id,
        f"👑 Admin panel\n"
        f"📱 Ro‘yxatdan o‘tganlar: {total_users}\n"
        f"🕓 Kutayotganlar: {online}\n"
        f"💬 Faol chatlar: {active}"
    )


# === TASODIFIY CHAT ===
@bot.message_handler(commands=['search'])
def search_partner(message):
    user_id = message.from_user.id

    if user_id not in registered_users:
        bot.send_message(message.chat.id, "📛 Avval raqamingizni ulashing. /start ni bosing.")
        return

    if user_id in active_chats:
        bot.send_message(user_id, "Siz allaqachon suhbatdasiz. ❌ /stop bilan yakunlang.")
        return

    if waiting_users:
        partner_id = waiting_users.pop(0)
        active_chats[user_id] = partner_id
        active_chats[partner_id] = user_id
        bot.send_message(user_id, "💬 Suhbatdosh topildi! Yozishni boshlang 👇")
        bot.send_message(partner_id, "💬 Suhbatdosh topildi! Yozishni boshlang 👇")
    else:
        waiting_users.append(user_id)
        bot.send_message(user_id, "🔎 Suhbatdosh qidirilmoqda... Kuting.")


# === CHAT TO‘XTATISH ===
@bot.message_handler(commands=['stop'])
def stop_chat(message):
    user_id = message.from_user.id

    if user_id in active_chats:
        partner_id = active_chats[user_id]
        bot.send_message(partner_id, "❌ Suhbatdosh chatni yakunladi.")
        bot.send_message(user_id, "✅ Chat yakunlandi.")
        del active_chats[partner_id]
        del active_chats[user_id]
    elif user_id in waiting_users:
        waiting_users.remove(user_id)
        bot.send_message(user_id, "❌ Qidiruv to‘xtatildi.")
    else:
        bot.send_message(user_id, "Siz hech kim bilan suhbatda emassiz.")


# === XABARLARNI UZATISH ===
@bot.message_handler(func=lambda message: True)
def forward_message(message):
    user_id = message.from_user.id
    if user_id in active_chats:
        partner_id = active_chats[user_id]
        bot.send_message(partner_id, message.text)
    elif user_id != ADMIN_ID:
        bot.send_message(user_id, "📢 Avval /search orqali suhbatdosh toping.")


# === ISHGA TUSHURISH ===
print("🤖 Bot ishga tushdi...")
bot.polling(none_stop=True)

