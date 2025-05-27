from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, CallbackContext
import json

with open("config.json", "r") as f:
    config = json.load(f)

TOKEN = config["TOKEN"]
ADMIN_ID = config["ADMIN_ID"]

stopped = False  # 일시중지 상태를 저장할 전역 변수

async def kick_user(update: Update, context: CallbackContext):
    # 봇이 중지 상태면 아무것도 안 함
    if stopped:
        return

    # 명령을 내린 사람이 ADMIN_ID인지 확인
    #    if update.effective_user.id != ADMIN_ID:
    #    return

    if update.message:
        for user in update.message.new_chat_members:
            if user.is_bot:
                print(f"🤖 {user.first_name} (봇) 감지 - 강퇴하지 않음")
                continue

            await context.bot.ban_chat_member(chat_id=update.message.chat_id, user_id=user.id)
            await context.bot.unban_chat_member(chat_id=update.message.chat_id, user_id=user.id)
            await update.message.reply_text(f"{user.first_name}님이 자동 강퇴되었습니다. 🚫 (다시 초대 가능)")

async def stop_command(update: Update, context: CallbackContext):
    # 관리자만 사용 가능
    if update.effective_user.id != ADMIN_ID:
        return

    global stopped
    stopped = True
    await update.message.reply_text("봇이 일시중지되었습니다.")

async def restart_command(update: Update, context: CallbackContext):
    # 관리자만 사용 가능
    if update.effective_user.id != ADMIN_ID:
        return

    global stopped
    stopped = False
    await update.message.reply_text("봇이 다시 가동되었습니다.")

def main():
    app = Application.builder().token(TOKEN).build()

    # 명령어 핸들러 등록
    app.add_handler(CommandHandler("stop", stop_command))
    app.add_handler(CommandHandler("restart", restart_command))

    # 새 유저 감지 핸들러 등록
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, kick_user))

    print("🤖 봇이 실행 중입니다...")
    app.run_polling()

if __name__ == "__main__":
    main()
