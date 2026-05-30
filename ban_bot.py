from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, CallbackContext
import json
import asyncio
import re
import os
import unicodedata

test_mode = False

auto_kick = True

# BADWORDS는 config 파일(config.json)의 "BADWORDS" 키에서 실시간으로 로드됩니다. (load_badwords 참고)
# 아래 값은 config에 "BADWORDS" 키가 없을 때만 쓰는 기본값(fallback)입니다.
BADWORDS_DEFAULT = ["김대중","운지","노짱","부엉이","노무","이기","무현","섹스"]
BADWORDS_MAX_GAP = 10

# --- 설정/로드 ---
CONFIG_PATH = "config_test.json" if test_mode else "config.json"
with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

TOKEN = config["TOKEN"]
ADMIN_ID = config["ADMIN_ID"]
NOTICE_CHAT_ID = config.get("NOTICE_CHAT_ID", None)
KICK_EXCEPTIONS = config.get("KICK_EXCEPTIONS", []) or []
# SILENT_CHAT_ID: 이 목록에 있는 그룹에서는 봇이 사용자에게 보내는 안내 메시지를 전부 생략합니다.
# (삭제/강퇴 같은 조치 자체는 그대로 수행하고, 안내는 안 보낸 채 로그(print)만 남김)
SILENT_CHAT_ID = config.get("SILENT_CHAT_ID", []) or []

def is_silent_chat(chat_id):
    """SILENT_CHAT_ID에 속한 채팅이면 True. 이런 방에선 사용자 안내 메시지를 보내지 않고 로그만 남긴다."""
    return chat_id in SILENT_CHAT_ID

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

    if update.effective_user is None or update.effective_user.id != ADMIN_ID:
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
            
            # === 영구밴 조건들은 KICK_EXCEPTIONS와 무관하게 항상 적용됨 (예외방에서도 영구밴) ===
            display_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
            username = user.username or ""

            # 키릴 문자(러시아어) 닉네임 → 영구 차단 (unban 없음)
            if contains_cyrillic(display_name) or contains_cyrillic(username):
                try:
                    # unban 없이 영구 차단
                    await context.bot.ban_chat_member(chat_id=update.message.chat_id, user_id=user.id)
                    print(f"🚫 러시아어 닉네임 강퇴: {display_name} (@{username})")
                except Exception as e:
                    # 한 명 실패가 같은 배치의 다른 유저 처리를 막지 않도록 로그만 남기고 진행
                    print(f"러시아어 닉네임 강퇴 실패: {e}")
                continue

            # username 없는 계정 → 영구 차단 (unban 없음)
            if not username:
                try:
                    await context.bot.ban_chat_member(chat_id=update.message.chat_id, user_id=user.id)
                    print(f"🚫 username 없음 영구 강퇴: {display_name} (id={user.id})")
                except Exception as e:
                    print(f"username 없음 강퇴 실패: {e}")
                continue

            # === 여기부터는 일시밴(재초대 가능). KICK_EXCEPTIONS 채팅은 건너뜀 ===
            # return이 아니라 continue: 같은 배치로 들어온 다른 유저는 계속 처리해야 함
            if update.message.chat_id in KICK_EXCEPTIONS:
                continue

            try:
                await context.bot.ban_chat_member(chat_id=update.message.chat_id, user_id=user.id)
                await context.bot.unban_chat_member(chat_id=update.message.chat_id, user_id=user.id)
            except Exception as e:
                # 실제로 강퇴가 안 됐으면 안내 메시지도 보내지 않는다 (강퇴 메시지 오발송 버그 방지)
                print(f"자동 강퇴 실패(메시지 미발송): {e}")
                continue
            print(f"자동 강퇴: {display_name} (id={user.id})")
            # 강퇴가 실제로 성공했고, 조용한 방이 아닐 때만 안내 메시지 전송
            if not is_silent_chat(update.message.chat_id):
                try:
                    await update.message.reply_text(f"{user.first_name}님이 자동 강퇴되었습니다. 🚫 (다시 초대 가능)")
                except Exception as e:
                    # 안내 메시지 실패가 같은 배치의 다른 유저 처리를 막지 않도록 (강퇴는 이미 성공)
                    print(f"강퇴 안내 메시지 실패: {e}")

# ========== 스팸 링크 댓글 감지 & 유저 강퇴 ==========
def is_reply_to_notice(message):
    ref_msg = getattr(message, "reply_to_message", None)
    if ref_msg != None:
        try:
            if ref_msg.sender_chat.id in NOTICE_CHAT_ID:
                return True
        except Exception as e:
            # 채팅내 reply일 가능성이 높음
            print(e)
            return False
        
    return False

def contains_cyrillic(text: str) -> bool:
    """키릴 문자(러시아어 등) 포함 여부 확인"""
    if not text:
        return False
    cyrillic_pattern = re.compile(r'[\u0400-\u04FF]')
    return bool(cyrillic_pattern.search(text))

def message_contains_link(msg):
    # 텍스트 내 http, https 링크
    text = msg.text or msg.caption or ""
    if re.search(r'http[s]?://', text, re.IGNORECASE):
        return True
    
    # claim 문구
    if re.search(r'claim', text, re.IGNORECASE):
        return True
    
    # @xxxbot문구
    if re.search(r'@\w*bot\b', text, re.IGNORECASE):
        return True
    
    # '하이퍼링크/URL' entity 존재 시
    entities = list(msg.entities or []) + list(msg.caption_entities or [])
    for ent in entities:
        # text_link: 마크다운/HTML 등으로 삽입된 하이퍼링크
        # url: 자동 감지 URL (보통 http로 시작하는 걸로 자동 탐지됨)
        if ent.type in ['url', 'text_link']:
            return True
    return False

def message_is_too_long(msg, limit=1000):
    text = msg.text or msg.caption or ""
    return len(text) >= limit

def normalize_korean(text):
    # NFC: 조합형 한글을 완성형으로 바꿔준다
    return unicodedata.normalize('NFC', text)

# --- BADWORDS 실시간 로드 (config 파일을 수정하면 봇 재시작 없이 즉시 반영됨) ---
_badwords_cache = {"mtime": None, "words": BADWORDS_DEFAULT}

def load_badwords():
    """config 파일의 "BADWORDS" 키를 읽어 반환한다.
    파일이 수정되면(mtime 변경) 자동으로 다시 읽어 실시간 반영하고,
    변경이 없으면 캐시를 그대로 쓴다. 읽기/파싱 실패 시 직전 값을 유지한다."""
    try:
        mtime = os.path.getmtime(CONFIG_PATH)
        if mtime != _badwords_cache["mtime"]:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            words = data.get("BADWORDS", BADWORDS_DEFAULT)
            if isinstance(words, list):
                _badwords_cache["words"] = [str(w) for w in words if str(w)]
                _badwords_cache["mtime"] = mtime  # 파싱 성공했을 때만 mtime 확정
                print(f"[BADWORDS] 갱신: {len(_badwords_cache['words'])}개 단어 로드됨")
            else:
                # 리스트가 아니면(문자열/딕트/null 등) 기존값 유지하고 mtime은 확정하지 않음
                # → 다음 호출에서 다시 시도하게 해서 잘못된 값이 캐시로 굳지 않도록 함
                print(f"[BADWORDS] BADWORDS가 리스트가 아님(무시, 기존값 유지): {type(words).__name__}")
    except Exception as e:
        print(f"[BADWORDS] 로드 실패, 기존값 유지: {e}")
    return _badwords_cache["words"]

def message_contains_profanity(msg, badwords, max_gap=4):
    raw_text = (msg.text or msg.caption or "").lower()
    cleaned_text = re.sub(r'\s+', '', raw_text) 
    cleaned_text = normalize_korean(cleaned_text) # 한글 정규화
    
    for bad in badwords:
        if len(bad) < 1:
            continue
        
        # 비속어 자체에 정규표현식 특수문자가 있을 경우를 대비해 이스케이프 처리
        # \b (단어 경계)는 제거하여, "이기"가 "이기적" 안에 있더라도 탐지하도록 합니다.
        pattern = re.escape(bad) 
        
        # print(f"검사패턴: {pattern}, 검사대상: {cleaned_text}")
        if re.search(pattern, cleaned_text, re.IGNORECASE):
            # print("탐지: ", bad)
            return True
            
    return False


async def spam_reply_handler(update: Update, context: CallbackContext):
    # 채널 명의 글/익명 관리자/채널 자동전달 등 '사용자 없는' 메시지는 무시
    # (update.message나 from_user가 None일 수 있어 .id 접근 전에 None을 먼저 가드 —
    #  effective_user가 None인 경우 .id에서 크래시 나던 버그 수정)
    msg = update.message
    if msg is None or msg.from_user is None:
        return
    # 텔레그램 시스템(자동전달) 계정 무시
    if msg.from_user.id == 777000:
        return
    
    if not authenticated or stopped or NOTICE_CHAT_ID is None or msg.from_user.id == ADMIN_ID:
        return

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

    # === 메시지 본문에 키릴 문자(러시아어)가 있으면 영구 강퇴 (unban 없음) ===
    # 닉네임뿐 아니라 댓글 내용에 러시아어가 섞여 있어도 즉시 삭제 + 영구밴
    if contains_cyrillic(msg.text or msg.caption or ""):
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
            print(f"키릴 메시지 삭제: {user_id}")
        except Exception as e:
            print(f"키릴 메시지 삭제 실패: {e}")
        try:
            # 모든 공지채널 + 현재방에서 영구 ban (재구독 불가)
            for notice_chat in NOTICE_CHAT_ID:
                await context.bot.ban_chat_member(chat_id=notice_chat, user_id=int(user_id))
            await context.bot.ban_chat_member(chat_id=chat_id, user_id=int(user_id))
            print(f"🚫 키릴 메시지 영구 강퇴: {user_id}")
        except Exception as e:
            print(f"키릴 메시지 강퇴 실패: {e}")
        return

    if not msg.reply_to_message and chat_id in NOTICE_CHAT_ID:
        return
    
    # 공지 원글에 대한 댓글인가?
    is_reply = is_reply_to_notice(msg)

    # http(s) 링크 포함 여부
    is_link_contains = True
    text = msg.text or msg.caption
    if not message_contains_link(msg):
        is_link_contains = False
        # 링크 없는 첫 댓글: 욕설/도배가 아닐 때만 환영하고 종료.
        # 욕설/도배면 환영하지 않고 아래 삭제 블록으로 진행한다 (강퇴는 안 함, 삭제만).
        if is_first_comment and not message_contains_profanity(msg, load_badwords(), BADWORDS_MAX_GAP) and not message_is_too_long(msg, 1000):
            if not is_silent_chat(chat_id):
                user = msg.from_user
                name = f"{user.first_name} {user.last_name or ''}".strip()
                await msg.reply_text(f"{name} 첫 댓글 고맙다. 앞으로 분위기 잘 띄워라 🎉")
            return
    
    #print('text',text)
    #print('link cointained?',is_link_contains)
    #print('first comment?', is_first_comment)
    #print('is reply?',is_reply)

    # --- 메시지 삭제 ---
    # 처음 글을 쓰거나, 댓글인경우엔 링크를 항상 비허용 (삭제처리만)
    if is_first_comment or is_reply:
        try:
            if is_link_contains:
                await context.bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
                print(f"메시지 삭제: {user_id}")
        except Exception as e:
            print(f"메시지 삭제 실패: {e}")
    else:
        print('처음 쓰는 유저가 아니라 냅둠')

    # --- 유저 강퇴/언밴 ---
    # 첫 댓글 + 링크 있으면 무조건 강퇴, 다른 채널도 구독 불가
    # (링크 없는 첫 댓글의 욕설/도배는 강퇴가 아니라 아래에서 '삭제'만 한다)
    if is_first_comment and is_link_contains:
        try:
            for notice_chat in NOTICE_CHAT_ID:
                await context.bot.ban_chat_member(chat_id=notice_chat, user_id=int(user_id))
                print(f"유저 {user_id} 강퇴 완료")

            await context.bot.ban_chat_member(chat_id=chat_id, user_id=int(user_id))
            print(f"유저 {user_id} 강퇴 완료")
        except Exception as e:
            print(f"유저 강퇴 실패: {e}")

    #print(message_contains_profanity(msg, load_badwords(), BADWORDS_MAX_GAP))

    if message_contains_profanity(msg, load_badwords(), BADWORDS_MAX_GAP):
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
            print(f"메시지 금지어 삭제: {user_id}")
            if not is_silent_chat(chat_id):
                user = msg.from_user
                name = f"{user.first_name} {user.last_name or ''}".strip()
                #await msg.reply_text(f"{name} 금지어 삭제")
                await context.bot.send_message(chat_id=chat_id, text=f"{name} 금지어 삭제")
        except Exception as e:
            print(f"메시지 삭제 실패: {e}")
    
    if message_is_too_long(msg, 1000):
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
            print(f"메시지 도배 삭제: {user_id}")
            if not is_silent_chat(chat_id):
                user = msg.from_user
                name = f"{user.first_name} {user.last_name or ''}".strip()
                #await msg.reply_text(f"{name} 장문 도배 삭제")
                await context.bot.send_message(chat_id=chat_id, text=f"{name} 장문 도배 삭제")
        except Exception as e:
            print(f"메시지 삭제 실패: {e}")

# ========== 기타 명령 ==========
async def stop_command(update: Update, context: CallbackContext):
    if not authenticated:
        return
    if update.effective_user is None or update.effective_user.id != ADMIN_ID:
        return

    global stopped
    stopped = True
    await update.message.reply_text("봇이 일시중지되었습니다.")

async def restart_command(update: Update, context: CallbackContext):
    if not authenticated:
        return
    if update.effective_user is None or update.effective_user.id != ADMIN_ID:
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
    if auto_kick:
        app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, kick_user))
    app.add_handler(MessageHandler(filters.ALL, spam_reply_handler))  # ← spam reply 감지

    print("🤖 봇이 실행 중입니다...")
    if not authenticated:
        print("[관리자 인증을 받을 때까지 대기합니다. 텔레그램에서 /auth (ADMIN_ID로) 명령을 보내세요.]")
    app.run_polling()

if __name__ == "__main__":
    main()
