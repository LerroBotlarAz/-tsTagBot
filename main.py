import asyncio
import random
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from config import Config

app = Client("pro_tagger", api_id=Config.API_ID, api_hash=Config.API_HASH, bot_token=Config.BOT_TOKEN)

# Bot dayandırılması üçün kontrol
TAG_PROCESS = {}

# Tağ zamanı istifadə olunacaq emojilər
EMOJIS = ["🚀", "✨", "💎", "🔥", "📢", "🌟", "⚡", "🌈", "💠", "✅"]

@app.on_message(filters.command("start") & filters.private)
async def start_private(client, message):
    text = (
        f"👋 **Salam {message.from_user.mention}!**\n\n"
        "🚀 Mən qruplar üçün nəzərdə tutulmuş ən sürətli **Tağ Botuyam.**\n\n"
        "💡 **Nələr edə bilərəm?**\n"
        "• Qrup üzvlərini müxtəlif üsullarla tağ edirəm.\n"
        "• Adminləri xüsusi olaraq çağırıram.\n"
        "• Sürətli və limitlərə uyğun işləyirəm."
    )
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Məni Qrupa Əlavə Et", url=f"https://t.me/{(await client.get_me()).username}?startgroup=true")],
        [InlineKeyboardButton("🇦🇿 Rəsmi Kanal", url="https://t.me/Arazzq")]
    ])
    await message.reply(text, reply_markup=buttons)

@app.on_message(filters.command("help") & filters.group)
async def help_group(client, message):
    help_text = (
        "🛠 **Botun Əmrləri:**\n\n"
        "🔹 `/tag` [mesaj] - Üzvləri 5-li tağ edir.\n"
        "🔹 `/single` [mesaj] - Üzvləri tək-tək tağ edir.\n"
        "🔹 `/atag` - Ancaq adminləri çağırır.\n"
        "🔹 `/stop` - Davam edən tağ prosesini dayandırır."
    )
    await message.reply(help_text)

@app.on_message(filters.command(["tag", "single"]) & filters.group)
async def tagging_engine(client, message):
    global TAG_PROCESS
    chat_id = message.chat.id
    
    # Əgər artıq bir tağ gedirsə, yenisini başlatma
    if TAG_PROCESS.get(chat_id):
        return await message.reply("⚠️ **Hazırda bir tağ prosesi davam edir!**\nDayandırmaq üçün `/stop` yazın.")

    TAG_PROCESS[chat_id] = True
    mode = message.command[0] # tag və ya single
    tag_msg = message.text.split(None, 1)[1] if len(message.command) > 1 else "Üzvlər diqqət! 📢"
    
    members = []
    async for member in client.get_chat_members(chat_id):
        if not member.user.is_bot and not member.user.is_deleted:
            members.append(member.user.mention)

    if not members:
        TAG_PROCESS[chat_id] = False
        return await message.reply("❌ Üzvləri götürmək mümkün olmadı.")

    await message.reply(f"✅ **Tağ Başladı!**\n📊 **Ümumi Üzv:** {len(members)}\n🛠 **Rejim:** {'5-li' if mode == 'tag' else 'Tək-tək'}")

    step = 5 if mode == "tag" else 1
    
    for i in range(0, len(members), step):
        if not TAG_PROCESS.get(chat_id):
            break
        
        batch = members[i:i+step]
        emoji = random.choice(EMOJIS)
        output = f"{emoji} {tag_msg}\n\n" + " ".join(batch)
        
        await client.send_message(chat_id, output)
        await asyncio.sleep(2.5) # Telegram limitlərinə düşməmək üçün

    TAG_PROCESS[chat_id] = False
    await client.send_message(chat_id, "🏁 **Tağ prosesi başa çatdı.**")

@app.on_message(filters.command("atag") & filters.group)
async def admin_tag(client, message):
    chat_id = message.chat.id
    admins = []
    async for member in client.get_chat_members(chat_id, filter="administrators"):
        if not member.user.is_bot:
            admins.append(member.user.mention)
    
    await client.send_message(chat_id, "👮‍♂️ **Adminlər çağırılır:**\n\n" + " ".join(admins))

@app.on_message(filters.command("stop") & filters.group)
async def stop_tagging(client, message):
    global TAG_PROCESS
    chat_id = message.chat.id
    if TAG_PROCESS.get(chat_id):
        TAG_PROCESS[chat_id] = False
        await message.reply("🛑 **Tağ dayandırıldı.**")
    else:
        await message.reply("ℹ️ Hazırda aktiv tağ yoxdur.")

print("Bot işə düşdü...")
app.run()
