import asyncio, os, random, re
from rubika_bot_api.api import Robot
from rubika_bot_api import filters

TOKEN = os.environ.get("RUBIKA_TOKEN", "")
ADMINS = set(os.environ.get("ADMIN_IDS", "").split(","))
MAX_WARN = 3

bot = Robot(token=TOKEN)
warns = {}

LINK_RE = re.compile(
    r"(https?://|www\.|t\.me/|rubika\.ir/|@\w{4,}|\b\w+\.(com|ir|org|net)\b)",
    re.I,
)

AUTO_REPLIES = {
    "سلام": "سلام! خوش اومدی 🌹",
    "خوبی": "مرسی، تو خوبی؟ 😊",
    "ربات": "من اینجام، چه کمکی از دستم برمیاد؟",
}

FACTS = [
    "قلب میگو توی سرشه 🦐",
    "زنبور برای یه قاشق عسل باید میلیون‌ها گل رو بگرده 🐝",
    "اثر انگشت هیچ دو نفری یکی نیست ☝️",
]

CHALLENGES = [
    "چالش: ۱۰ ثانیه بدون پلک زدن به صفحه نگاه کن 👀",
    "چالش: اسم ۵ شهر که با «ک» شروع می‌شن رو بگو!",
    "چالش: یه جمله بگو که همه‌ی کلماتش با «م» شروع بشن 😄",
]


async def safe_delete(robot, msg):
    try:
        await robot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)
    except Exception as e:
        print("delete failed:", e)


async def safe_ban(robot, chat_id, user_id):
    try:
        await robot.ban_chat_member(chat_id, user_id)
        return True
    except Exception as e:
        print("ban failed:", e)
        return False


@bot.on_started_bot()
async def on_start(robot, chat_id):
    await robot.send_message(
        chat_id,
        "سلام! من ربات مدیریت‌ام 🤖\n/fact /dice /challenge /id",
    )


@bot.on_message(filters=filters.text)
async def handle(robot, msg):
    text = msg.text.strip()
    uid = str(msg.sender_id)
    is_admin = uid in ADMINS

    # دستورات سرگرمی
    if text == "/id":
        return await msg.reply(f"شناسه‌ی شما: {uid}")
    if text == "/fact":
        return await msg.reply(random.choice(FACTS))
    if text == "/dice":
        return await msg.reply(f"🎲 تاس تو: {random.randint(1, 6)}")
    if text == "/challenge":
        return await msg.reply(random.choice(CHALLENGES))

    # قفل لینک و تبلیغ + اخطار
    if not is_admin and LINK_RE.search(text):
        await safe_delete(robot, msg)
        warns[uid] = warns.get(uid, 0) + 1
        if warns[uid] >= MAX_WARN:
            ok = await safe_ban(robot, msg.chat_id, msg.sender_id)
            warns[uid] = 0
            note = "از گروه حذف شد 🚫" if ok else "به حد اخطار رسید ⚠️"
            return await robot.send_message(msg.chat_id, f"کاربر {note}")
        return await robot.send_message(
            msg.chat_id,
            f"⚠️ ارسال لینک ممنوعه. اخطار {warns[uid]} از {MAX_WARN}",
        )

    # پاسخ خودکار
    if text in AUTO_REPLIES:
        await msg.reply(AUTO_REPLIES[text])


if __name__ == "__main__":
    asyncio.run(bot.run())
