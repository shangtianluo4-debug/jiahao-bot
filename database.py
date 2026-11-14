import aiosqlite

DB_PATH = "bot_data.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        # 伺服器設定 (歡迎/離開/建議審核/匿名頻道)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS guild_settings (
                guild_id INTEGER PRIMARY KEY,
                welcome_channel INTEGER,
                welcome_msg TEXT,
                leave_channel INTEGER,
                leave_msg TEXT,
                suggest_review_channel INTEGER,
                suggest_public_channel INTEGER,
                anon_channel INTEGER,
                anon_count INTEGER DEFAULT 0
            )
        """)
        # 抽獎資料表
        await db.execute("""
            CREATE TABLE IF NOT EXISTS giveaways (
                message_id INTEGER PRIMARY KEY,
                channel_id INTEGER,
                guild_id INTEGER,
                prize TEXT,
                winners_count INTEGER,
                end_time REAL,
                role_id INTEGER,
                participants TEXT,
                ended INTEGER DEFAULT 0
            )
        """)
        # 活動報名資料表
        await db.execute("""
            CREATE TABLE IF NOT EXISTS events (
                message_id INTEGER PRIMARY KEY,
                channel_id INTEGER,
                guild_id INTEGER,
                title TEXT,
                description TEXT,
                event_time REAL,
                max_slots INTEGER,
                participants TEXT,
                reminded INTEGER DEFAULT 0
            )
        """)
        # 活躍度資料表
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                guild_id INTEGER,
                user_id INTEGER,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                last_daily REAL DEFAULT 0,
                last_hourly REAL DEFAULT 0,
                PRIMARY KEY (guild_id, user_id)
            )
        """)
        # 關鍵字自動回覆資料表
        await db.execute("""
            CREATE TABLE IF NOT EXISTS keywords (
                guild_id INTEGER,
                trigger_word TEXT,
                reply_text TEXT,
                PRIMARY KEY (guild_id, trigger_word)
            )
        """)
        await db.commit()
