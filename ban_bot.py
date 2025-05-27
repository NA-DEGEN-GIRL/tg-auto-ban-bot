from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, CallbackContext
import json
import asyncio

with open("config.json", "r") as f:
    config = json.load(f)

TOKEN = config["TOKEN"]
ADMIN_ID = config["ADMIN_ID"]

stopped = False  # 일시중지 상태를 저장할 전역 변수
authenticated = False  # 인증 여부

async def auth_command(update: Update, context: CallbackContext):
    global authenticated

    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ You are not allowed to authenticate this bot.")
        return

    if authenticated:
        await update.message.reply_text("✅ Already authenticated!")
        return

    authenticated = True
    await update.message.reply_text("✅ 인증이 완료되었습니다. 봇이 이제 동작을 시작합니다.")

async def kick_user(update: Update, context: CallbackContext):
    # 인증되지 않았으면 동작하지 않음
    if not authenticated or stopped:
        return

    if update.message:
        for user in update.message.new_chat_members:
            if user.is_bot:
                print(f"🤖 {user.first_name} (봇) 감지 - 강퇴하지 않음")
                continue

            await context.bot.ban_chat_member(chat_id=update.message.chat_id, user_id=user.id)
            await context.bot.unban_chat_member(chat_id=update.message.chat_id, user_id=user.id)
            await update.message.reply_text(f"{user.first_name}님이 자동 강퇴되었습니다. 🚫 (다시 초대 가능)")

async def stop_command(update: Update, context: CallbackContext):
    if not authenticated:
        return
    if update.effective_user.id != ADMIN_ID:
        return

    global stopped
    stopped = True
    await update.message.reply_text("봇이 일시중지되었습니다.")

async def restart_command(update: Update, context: CallbackContext):
    if not authenticated:
        return
    if update.effective_user.id != ADMIN_ID:
        return

    global stopped
    stopped = False
    await update.message.reply_text("봇이 다시 가동되었습니다.")

async def start_command(update: Update, context: CallbackContext):
    # 인증 전임을 안내
    if authenticated:
        await update.message.reply_text("🤖 봇은 이미 인증되어 정상 운영 중입니다.")
    else:
        await update.message.reply_text(
            "🤖 관리자 인증이 필요합니다.\n"
            f"ADMIN_ID({ADMIN_ID}) 계정으로 /auth 명령을 보내세요."
        )

def main():
    app = Application.builder().token(TOKEN).build()

    # 명령어 핸들러 등록
    app.add_handler(CommandHandler("auth", auth_command))
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("stop", stop_command))
    app.add_handler(CommandHandler("restart", restart_command))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, kick_user))

    print("🤖 봇이 실행 중입니다...")
    print("[관리자 인증을 받을 때까지 대기합니다. 텔레그램에서 /auth (ADMIN_ID로) 명령을 보내세요.]")
    app.run_polling()

if __name__ == "__main__":
    main()
