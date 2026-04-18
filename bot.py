import os
import requests
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ── مفاتيح API ──────────────────────────────────────────
TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_KEY")

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# ── جلب الأسعار ─────────────────────────────────────────
def get_crypto_prices():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "bitcoin,ethereum,tether,binancecoin,solana,ripple,cardano,dogecoin",
        "vs_currencies": "usd",
        "include_24hr_change": "true"
    }
    r = requests.get(url, params=params).json()
    return r

def get_metals_prices():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "tether-gold,silver,platinum",
        "vs_currencies": "usd"
    }
    r = requests.get(url, params=params).json()
    return r

def get_forex_prices():
    url = "https://api.exchangerate-api.com/v4/latest/USD"
    r = requests.get(url).json()
    rates = r["rates"]
    return {
        "EGP": rates.get("EGP"),
        "EUR": rates.get("EUR"),
        "GBP": rates.get("GBP"),
        "SAR": rates.get("SAR"),
        "AED": rates.get("AED"),
        "KWD": rates.get("KWD"),
    }

# ── الأوامر ──────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 أهلاً بك في بوت الأسعار الذكي!\n\n"
        "📌 الأوامر المتاحة:\n\n"
        "💰 العملات الرقمية:\n"
        "/crypto - أسعار أهم العملات\n\n"
        "🥇 المعادن:\n"
        "/metals - أسعار الذهب والفضة والبلاتين\n\n"
        "💵 العملات العادية:\n"
        "/forex - أسعار الصرف\n\n"
        "📊 تحليل:\n"
        "/analyze BTCUSDT - تحليل عملة\n\n"
        "🔔 تنبيهات:\n"
        "/alert BTC 80000 - نبهني لما BTC يوصل 80000\n\n"
        "🤖 أو اكتب أي سؤال وأنا هرد عليك!"
    )

async def crypto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ جاري جلب الأسعار...")
    try:
        data = get_crypto_prices()
        coins = {
            "bitcoin": ("₿ Bitcoin", "BTC"),
            "ethereum": ("Ξ Ethereum", "ETH"),
            "tether": ("💵 Tether", "USDT"),
            "binancecoin": ("🔶 BNB", "BNB"),
            "solana": ("◎ Solana", "SOL"),
            "ripple": ("💧 XRP", "XRP"),
            "cardano": ("🔵 Cardano", "ADA"),
            "dogecoin": ("🐕 Dogecoin", "DOGE"),
        }
        msg = "💰 أسعار العملات الرقمية:\n\n"
        for coin_id, (name, symbol) in coins.items():
            price = data[coin_id]["usd"]
            change = data[coin_id].get("usd_24h_change", 0)
            arrow = "📈" if change > 0 else "📉"
            msg += f"{name}\n${price:,.4f} {arrow} {change:+.2f}%\n\n"
        await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text("❌ حدث خطأ، حاول تاني.")

async def metals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ جاري جلب الأسعار...")
    try:
        data = get_metals_prices()
        msg = "🥇 أسعار المعادن (للأوقية):\n\n"
        if "tether-gold" in data:
            msg += f"🥇 الذهب: ${data['tether-gold']['usd']:,.2f}\n"
        if "silver" in data:
            msg += f"🥈 الفضة: ${data['silver']['usd']:,.2f}\n"
        if "platinum" in data:
            msg += f"⬜ البلاتين: ${data['platinum']['usd']:,.2f}\n"
        await update.message.reply_text(msg)
    except:
        await update.message.reply_text("❌ حدث خطأ، حاول تاني.")

async def forex(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ جاري جلب الأسعار...")
    try:
        data = get_forex_prices()
        msg = "💵 أسعار الصرف مقابل الدولار:\n\n"
        flags = {"EGP": "🇪🇬", "EUR": "🇪🇺", "GBP": "🇬🇧", "SAR": "🇸🇦", "AED": "🇦🇪", "KWD": "🇰🇼"}
        names = {"EGP": "جنيه مصري", "EUR": "يورو", "GBP": "جنيه إسترليني", "SAR": "ريال سعودي", "AED": "درهم إماراتي", "KWD": "دينار كويتي"}
        for currency, rate in data.items():
            if rate:
                msg += f"{flags[currency]} {names[currency]}: {rate:.2f}\n"
        await update.message.reply_text(msg)
    except:
        await update.message.reply_text("❌ حدث خطأ، حاول تاني.")

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("اكتب اسم العملة مثلاً:\n/analyze BTC")
        return
    coin = context.args[0].upper()
    await update.message.reply_text(f"⏳ جاري تحليل {coin}...")
    try:
        data = get_crypto_prices()
        coin_map = {"BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana", "BNB": "binancecoin", "XRP": "ripple"}
        coin_id = coin_map.get(coin)
        if coin_id and coin_id in data:
            price = data[coin_id]["usd"]
            change = data[coin_id].get("usd_24h_change", 0)
            prompt = f"""أنت محلل مالي خبير في العملات الرقمية.
سعر {coin} الحالي: ${price:,.2f}
التغير في 24 ساعة: {change:+.2f}%
قدم تحليلاً مختصراً باللغة العربية في 5 أسطر فقط يشمل:
- تقييم الوضع الحالي
- توقع قصير المدى
- نصيحة للمستثمر"""
        else:
            prompt = f"قدم تحليلاً مختصراً باللغة العربية لعملة {coin} في 5 أسطر."
        response = model.generate_content(prompt)
        await update.message.reply_text(f"🤖 تحليل {coin}:\n\n{response.text}")
    except:
        await update.message.reply_text("❌ حدث خطأ في التحليل.")

# قاموس التنبيهات
alerts = {}

async def alert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("الاستخدام:\n/alert BTC 80000\nسينبهك لما BTC يوصل 80000$")
        return
    coin = context.args[0].upper()
    try:
        target = float(context.args[1])
        user_id = update.message.chat_id
        if user_id not in alerts:
            alerts[user_id] = []
        alerts[user_id].append({"coin": coin, "target": target})
        await update.message.reply_text(f"✅ تم ضبط التنبيه!\nسيتم إعلامك لما {coin} يوصل ${target:,.2f}")
    except:
        await update.message.reply_text("❌ رقم غير صحيح.")

async def ai_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text
    await update.message.reply_text("🤖 جاري التفكير...")
    try:
        prompt = f"""أنت مساعد ذكي متخصص في الأسواق المالية والعملات الرقمية والمعادن.
أجب على السؤال التالي باللغة العربية بشكل مختصر ومفيد:
{user_msg}"""
        response = model.generate_content(prompt)
        await update.message.reply_text(response.text)
    except:
        await update.message.reply_text("❌ حدث خطأ، حاول تاني.")

# ── تشغيل البوت ─────────────────────────────────────────
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("crypto", crypto))
app.add_handler(CommandHandler("metals", metals))
app.add_handler(CommandHandler("forex", forex))
app.add_handler(CommandHandler("analyze", analyze))
app.add_handler(CommandHandler("alert", alert))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_reply))

app.run_polling()
