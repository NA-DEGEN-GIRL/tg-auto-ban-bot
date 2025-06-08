from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, CallbackContext
import json
import asyncio
import re
import os

test_mode = False

if test_mode:
    # --- 설정/로드 ---
    with open("config_test.json", "r") as f:
        config = json.load(f)
else:
    # --- 설정/로드 ---
    with open("config.json", "r") as f:
        config = json.load(f)

TOKEN = config["TOKEN"]
ADMIN_ID = config["ADMIN_ID"]
NOTICE_CHAT_ID = config.get("NOTICE_CHAT_ID", None)

AUTH_STATE_PATH = "auth_status.json"

def save_auth_state(authenticated: bool):
    with open(AUTH_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump({"authenticated": authenticated}, f)

def load_auth_state():
    if os.path.exists(AUTH_STATE_PATH):
        with open(AUTH_STATE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("authenticated", False)
    return False

authenticated = load_auth_state()

stopped = False  # 일시중지 상태를 저장할 전역 변수


# --- 유저 기록 (공지방별) ---
if test_mode:
    WRITER_DB_PATH = "writers_test.json"
else:
    WRITER_DB_PATH = "writers.json"

def load_writers():
    if os.path.exists(WRITER_DB_PATH):
        with open(WRITER_DB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        # {chat_id(str): [user_id, ...]} 형태
        return {int(k): set(map(str, v)) for k, v in data.items()}
    return {}

def save_writers():
    with open(WRITER_DB_PATH, "w", encoding="utf-8") as f:
        data = {str(k): list(v) for k, v in group_writers.items()}
        json.dump(data, f, ensure_ascii=False)

# 최초 로드
group_writers = load_writers()

# ========== 관리자 인증 ==========
async def auth_command(update: Update, context: CallbackContext):
    global authenticated

    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ You are not allowed to authenticate this bot.")
        return

    if authenticated:
        await update.message.reply_text("✅ Already authenticated!")
        return

    authenticated = True
    save_auth_state(authenticated)
    await update.message.reply_text("✅ 인증이 완료되었습니다. 봇이 이제 동작을 시작합니다.")

# ========== 새 유저 감지 & 강퇴 ==========
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

# ========== 스팸 링크 댓글 감지 & 유저 강퇴 ==========
def is_reply_to_notice(message):
    ref_msg = getattr(message, "reply_to_message", None)
    if ref_msg != None:
        if ref_msg.sender_chat.id == NOTICE_CHAT_ID:
            return True
        
    return False

async def spam_reply_handler(update: Update, context: CallbackContext):
    if not authenticated or stopped or NOTICE_CHAT_ID is None or update.effective_user.id == ADMIN_ID:
        return

    msg = update.message

    # --- 첫 댓글을 쓰는 유저인지 판별 ---
    chat_id = msg.chat_id
    user_id = str(msg.from_user.id)
    writers = group_writers.setdefault(chat_id, set())
    is_first_comment = user_id not in writers

    # 기록 및 저장
    if is_first_comment:
        print(f"[FIRST_REPLY] {user_id}가 방({chat_id})에서 처음 댓글을 달았습니다.")

    writers.add(user_id)
    save_writers()

    if not msg or not (msg.text or msg.caption):
        return
    
    if not msg.reply_to_message:
        return

    # 공지 원글에 대한 댓글인가?
    is_reply = is_reply_to_notice(msg)

    # http(s) 링크 포함 여부
    is_link_contains = True
    text = msg.text or msg.caption
    if not re.search(r'http[s]?://', text, re.IGNORECASE):
        # 링크는 없고 첫댓글 환영식
        if is_first_comment:
            user = msg.from_user
            name = f"{user.first_name} {user.last_name or ''}".strip()
            await msg.reply_text(f"{name} 첫 댓글 고맙다. 앞으로 분위기 잘 띄워라 🎉")
        return
    
    print('text',text)
    print('link cointained?',is_link_contains)
    print('first comment?', is_first_comment)
    print('is reply?',is_reply)

    # --- 메시지 삭제 ---
    # 처음 글을 쓰거나, 댓글인경우엔 링크를 항상 비허용 (삭제처리만)
    if is_first_comment or is_reply:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
            print(f"메시지 삭제: {user_id}")
        except Exception as e:
            print(f"메시지 삭제 실패: {e}")
    else:
        print('처음 쓰는 유저가 아니라 냅둠')

    # --- 유저 강퇴/언밴 ---
    # 첫음 글쓰는데 링크 있으면 무조건 강퇴
    if is_first_comment:
        try:
            await context.bot.ban_chat_member(chat_id=NOTICE_CHAT_ID, user_id=int(user_id))
            await context.bot.ban_chat_member(chat_id=chat_id, user_id=int(user_id))
            print(f"유저 {user_id} 강퇴 완료")
        except Exception as e:
            print(f"유저 강퇴 실패: {e}")

# ========== 기타 명령 ==========
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
    global authenticated
    app = Application.builder().token(TOKEN).build()

    # 명령어 핸들러 등록
    app.add_handler(CommandHandler("auth", auth_command))
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("stop", stop_command))
    app.add_handler(CommandHandler("restart", restart_command))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, kick_user))
    app.add_handler(MessageHandler(filters.ALL, spam_reply_handler))  # ← spam reply 감지

    print("🤖 봇이 실행 중입니다...")
    if not authenticated:
        print("[관리자 인증을 받을 때까지 대기합니다. 텔레그램에서 /auth (ADMIN_ID로) 명령을 보내세요.]")
    app.run_polling()

if __name__ == "__main__":
    main()
