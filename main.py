import os
import random
from datetime import datetime, timezone, timedelta
import discord
from discord.ext import commands, tasks
import aiosqlite
from database import init_db, DB_PATH

# 台灣時區 (UTC+8) 用於判斷早/午/晚安時態
TW_TZ = timezone(timedelta(hours=8))

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents, help_command=None)
        
        self.status_list = [
            "守護伺服器中 🛡️",
            "輸入 /幫助 查看指令 📜",
            "每天記得簽到領經驗 ✨",
            "正在監聽大家的早午晚安 ☀️",
            "託管於 Discloud ☁️"
        ]
        self.status_index = 0

    async def setup_hook(self):
        await init_db()
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                await self.load_extension(f"cogs.{filename[:-3]}")
        await self.tree.sync()
        self.change_status_task.start()

    # 7. 遊玩訊息：每 5 秒換一次
    @tasks.loop(seconds=5.0)
    async def change_status_task(self):
        status_text = self.status_list[self.status_index]
        await self.change_presence(activity=discord.Game(name=status_text))
        self.status_index = (self.status_index + 1) % len(self.status_list)

    @change_status_task.before_loop
    async def before_status(self):
        await self.wait_until_ready()

bot = MyBot()

# 4. 早安/午安/晚安 自動回覆 (仿 DGS弦樂式 時態偵測 + Embed)
GREETINGS = {
    "早安": [
        "早安喔！願今日你遇見的人，都對你溫柔以待。",
        "早安呀！新的一天開始了，記得吃頓豐盛的早餐開啟好心情 ☀️",
        "早安！太陽公公都曬屁股啦，今天也要元氣滿滿地前進喔！"
    ],
    "午安": [
        "午安！生活偶有波折，願此刻的小憩，為你蓄滿繼續前行的勇氣。",
        "午安呀！吃飽了嗎？下午工作或上課也要加油，別打瞌睡囉 ☕",
        "午安！忙了一整個早上，現在稍微伸個懶腰放鬆一下吧！"
    ],
    "晚安": [
        "晚安哇，期待你在夢裡成為大廚，做出的菜讓全世界都瘋狂。",
        "晚安！把今天的煩惱都留在枕頭外，祝你有個甜甜的好夢 🌙",
        "晚安呀，早點休息別熬夜滑手機囉，明天見！"
    ]
}

def get_current_period(hour: int) -> str:
    if 5 <= hour < 11:
        return "早上"
    elif 11 <= hour < 18:
        return "中午"
    else:
        return "晚上"

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot or not message.guild:
        return

    content = message.content.strip()

    # 檢查早/午/晚安
    matched_greet = None
    for key in ["早安", "午安", "晚安"]:
        if content.startswith(key) or content == key:
            matched_greet = key
            break

    if matched_greet:
        now_tw = datetime.now(TW_TZ)
        actual_period = get_current_period(now_tw.hour)
        quote = random.choice(GREETINGS[matched_greet])
        
        embed = discord.Embed(
            description=f"{message.author.mention}\n\n**{quote}**",
            color=discord.Color.gold()
        )
        # 時態不符時的幽默吐槽
        if (matched_greet == "早安" and actual_period != "早上") or \
           (matched_greet == "午安" and actual_period != "中午") or \
           (matched_greet == "晚安" and actual_period != "晚上"):
            embed.set_footer(text=f"順帶一提現在明明是{actual_period}為什麼要說{matched_greet} 🤨")
        else:
            embed.set_footer(text=f"現在時間 {now_tw.strftime('%H:%M')} • 祝你有美好的一天")
            
        await message.channel.send(embed=embed)

    # 9. 關鍵字系統檢查
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT trigger_word, reply_text FROM keywords WHERE guild_id = ?",
            (message.guild.id,)
        ) as cursor:
            rows = await cursor.fetchall()
            for trigger, reply in rows:
                if trigger in content:
                    await message.channel.send(reply)
                    break

    await bot.process_commands(message)

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise ValueError("找不到 DISCORD_TOKEN 環境變數！請在 Discloud 控制台設定環境變數。")
    bot.run(token)
