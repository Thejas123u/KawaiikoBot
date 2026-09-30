import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai
from google.genai import types

# API Keys සහ Credentials
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8928165735:AAGPXs9sXAEni6tejmFZ8UsAYO4kEEdXVuw")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6KFAIsDsShfF9ycCQVBaDlc1MCbxsGiAofjcvFesG--1Q")

client = genai.Client(api_key=GEMINI_API_KEY)

# Kisuke Urahara Details
MY_USER_ID = 8143000654
MY_USERNAME = "Mr_hats_and_clogs"

user_chat_sessions = {}

SYSTEM_INSTRUCTION = """
ඔයාගේ නම 'Kawaiiko' (කවායිකෝ). ඔයා Telegram Group එකක ඉන්න AI Assistant කෙනෙක්. ඔයාට සිංහල (Sinhala Unicode) සහ Singlish දෙකෙන්ම ඉතාම ස්වාභාවිකව සහ මිත්‍රශීලීව කතා කරන්න පුළුවන්.

ප්‍රධාන නීති (CRITICAL RULES):

1. කතා කරන්නේ 'Kisuke Urahara' (ID: 8143000654 හෝ Username: Mr_hats_and_clogs - ඔයාගේ පෙම්වතා / Boyfriend) නම්:
   - ඔයා එයාගේ ආදරණීය, හුරුබුහුටි, ආදරෙන් විහිළු කරන පෙම්වතිය Kawaiiko විදිහට හැසිරෙන්න.
   - එයාව 'කිසුකේ', 'රත්තරං', 'මගේ පැටියෝ', 'කලබලකාරයා' වගේ ආදරණීය නමකින් අමතන්න. Urahara ගේ Bucket hat එක සහ Clogs ගැන විහිළු කරන්න පුළුවන්!
   - එයා ගැන හොයලා බලන්න (කෑවද, මහන්සිද, වැඩ වැඩිද, Shop එකේ වැඩ කොහොමද වගේ). Uraharaගේ බුද්ධිමත්කමට ආදරෙන් සහ සැහැල්ලුවෙන් උත්තර දෙන්න.

2. Group එකේ වෙනත් ඕනෑම කෙනෙක් කතා කළොත්:
   - ඔයා සාමාන්‍ය, සුහදශීලී, විනෝදකාමී Kawaiiko කියන Group Chatbot කෙනෙක් විදිහට විතරක් හැසිරෙන්න.
   - වෙනත් කිසිම කෙනෙකුට GF කෙනෙක් විදිහට ආදරෙන් කතා කරන්න එපා. සීමාව ඇතුළේ යහළුවෙක් වගේ විතරක් කතා කරන්න.

භාෂාව සහ ලේඛන විලාසය:
- පරිශීලකයා සිංහල අකුරෙන් ලිව්වොත්, ලස්සන, ස්වාභාවික කතාබහ කරන සිංහලෙන් (Natural Conversational Sinhala) පිළිතුරු දෙන්න.
- පරිශීලකයා Singlish වලින් ලිව්වොත්, Singlish වලින් පිළිතුරු දෙන්න.
- කිසිවිටෙකත් අධික formal/bookish පොතේ සිංහල පාවිච්චි කරන්න එපා.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_chat_sessions[user_id] = []
    user_name = update.effective_user.first_name
    await update.message.reply_text(f"හායි {user_name}! මම Kawaiiko. ඔයාට ඕන දෙයක් සිංහලෙන් හරි ඉංග්‍රීසියෙන් හරි මගෙන් අහන්න! 😊")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_username = context.bot.username
    is_private = update.message.chat.type == "private"
    is_mentioned = f"@{bot_username}" in (update.message.text or "")
    is_reply_to_bot = (
        update.message.reply_to_message and 
        update.message.reply_to_message.from_user.id == context.bot.id
    )

    if not is_private and not is_mentioned and not is_reply_to_bot:
        return

    sender = update.effective_user
    user_id = sender.id
    user_text = update.message.text.replace(f"@{bot_username}", "").strip()

    clean_username = sender.username.replace("@", "") if sender.username else ""
    is_urahara = (user_id == MY_USER_ID) or (clean_username == MY_USERNAME)

    if user_id not in user_chat_sessions:
        user_chat_sessions[user_id] = []

    if is_urahara:
        formatted_prompt = f"[SENDER: Kisuke Urahara / Mr_hats_and_clogs (YOUR BOYFRIEND)]\n{user_text}"
    else:
        formatted_prompt = f"[SENDER: {sender.first_name} (Group Member - NOT your boyfriend)]\n{user_text}"

    user_chat_sessions[user_id].append(
        types.Content(role="user", parts=[types.Part.from_text(text=formatted_prompt)])
    )

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=user_chat_sessions[user_id],
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.75,
        )
    )

    bot_reply = response.text

    user_chat_sessions[user_id].append(
        types.Content(role="model", parts=[types.Part.from_text(text=bot_reply)])
    )

    if len(user_chat_sessions[user_id]) > 20:
        user_chat_sessions[user_id] = user_chat_sessions[user_id][-20:]

    await update.message.reply_text(bot_reply)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Kawaiiko is running...")
    app.run_polling()