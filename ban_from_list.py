from telegram import Bot
import asyncio
import json
import os
from dotenv import load_dotenv

# ========== 환경 변수 로드 ==========
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = int(os.getenv("CHANNEL"))  # 예: -1001234567890

# 강퇴 목록 파일
CYRILLIC_USERS_FILE = "cyrillic_users.json"


async def ban_users_from_list():
    bot = Bot(token=BOT_TOKEN)
    
    # JSON 파일 로드
    with open(CYRILLIC_USERS_FILE, "r", encoding="utf-8") as f:
        users = json.load(f)
    
    print(f"📋 강퇴 대상: {len(users)}명")
    print("=" * 60)
    
    success_count = 0
    fail_count = 0
    
    for user in users:
        user_id = user["id"]
        name = user["name"]
        
        try:
            await bot.ban_chat_member(chat_id=CHANNEL, user_id=user_id)
            print(f"✅ 강퇴 성공: {name} (ID: {user_id})")
            success_count += 1
        except Exception as e:
            print(f"❌ 강퇴 실패: {name} (ID: {user_id}) - {e}")
            fail_count += 1
        
        # Rate limit 방지 (0.5초 대기)
        await asyncio.sleep(0.5)
    
    print("=" * 60)
    print(f"📊 결과: 성공 {success_count}명, 실패 {fail_count}명")
    
    await bot.close()


if __name__ == "__main__":
    asyncio.run(ban_users_from_list())
