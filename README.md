# Telegram 자동 강제퇴장 & 스팸 댓글 방지 봇

텔레그램 그룹/공지방(채널/토론방 등) 운영을 위한 강력한 자동화 봇입니다.

## 주요 기능

- **자동 강퇴:**  
  그룹에 새로 들어온 "사람" 멤버를 자동으로 강퇴(즉시 언밴하여 재초대 가능).  
  *봇 계정은 강퇴하지 않습니다.*

- **스팸 링크 댓글 완전 차단:**  
  첫 댓글이 http/https 링크를 포함하면 즉시 강퇴,  
  이미 댓글을 작성한 유저의 링크 댓글은 삭제 처리(추방X).

- **첫 댓글 환영:**  
  사용자가 링크 없는 첫 댓글을 남기면 환영 메시지를 자동으로 답글로 전송.

- **공지방/토론방 모두 대응:**  
  채널, 포워딩된 토론방 등 모든 연동 환경 지원.

- **관리자 명령 및 인증 영속:**  
  `/auth`(최초 1회 인증), `/stop`, `/restart`  
  인증 상태가 파일에 저장·복원. (재시작시 재인증 불필요)

---

## 설치 및 실행

1. **파이썬 패키지 설치**
    ```bash
    pip install python-telegram-bot
    ```

2. **설정파일 작성**
    - `copy.config.json`을 복사해 `config.json`으로 파일명 변경
    - 값 입력: `TOKEN`, `ADMIN_ID`, `NOTICE_CHAT_ID`
    ```json
    {
        "TOKEN": "YOUR_BOT_TOKEN",
        "ADMIN_ID": 123456789,
        "NOTICE_CHAT_ID": -1001234567890
    }
    ```

3. **봇 실행**
    ```bash
    python ban_bot.py
    ```

4. **최초 인증**
    - Telegram에서 ADMIN_ID 계정으로 `/auth` 명령 전송(1회)
    - 추후 재시작시 자동 인증(별도 인증 불필요)

---

## 명령어

- `/auth`: 관리자 인증(최초 1회, 관리자만)
- `/stop`: 봇 일시정지(관리자만)
- `/restart`: 봇 재시작(관리자만)

---

## 동작 규칙 및 특이사항

- **자동 강퇴 동작**  
  - 새 멤버(사람)이 그룹에 입장하면 자동으로 강퇴(즉시 언밴)됩니다.
  - 강퇴된 사용자는 그룹 인원에서는 제외되지만,  
    **공지방(채널)을 통해 그룹 글에 "댓글"은 계속 달 수 있습니다.**
    (텔레그램의 구조적 특징, 포워딩/토론방 연동으로 인한 현상)
  - 강퇴된 사용자를 다시 그룹으로 초대하려면  
    **관리자가 `/stop` 명령으로 봇을 일시정지** 후 수동으로 초대하면  
    정상적으로 재참여가 가능합니다.

- **댓글 관련 상세 규칙**
    1. **유저가 그룹/채널에 "최초"로 댓글**
        - 댓글에 http/https 링크가 **포함** →  
          즉시 그룹(chat_id)과 공지방(NOTICE_CHAT_ID) 양쪽에서 해당 유저 강퇴, 메시지 삭제.
        - 댓글에 링크가 **없음** →  
          "첫 댓글 환영" 답글 자동 전송, 이후 댓글부터 일반 유저로 간주.
    2. **이미 댓글을 한번이라도 남긴 유저**
        - 이후 올리는 댓글에서 http/https 링크는 **항상 삭제**(강퇴X).
        - 링크 없는 일반 댓글은 모두 허용.

---

## 기타 안내

- **봇을 공지방/토론방(그룹)에 '관리자'로 등록해야 메시지 삭제·강퇴가 정상 작동합니다.**
- writers.json, auth_status.json 등 데이터 파일은 봇 폴더에 자동 생성·관리됩니다.

---

# Telegram Auto-Kick & Anti Spam-Reply Bot

A robust and automatic moderation bot for Telegram groups/channels.

## Features

- **Auto-kick new human members** (instantly bans & unbans for spam protection, re-invite allowed, bots ignored)
- **Strict anti-link reply:**  
  - First comment with http/https link → user is banned from both the group (`chat_id`) and channel (`NOTICE_CHAT_ID`), message deleted.
  - For existing users: any comment with a link is always deleted (not banned).
- **Welcome for first comment:**  
  If the first comment is a plain message, a welcome reply is sent.
- **Supports notice channels & discussion/forward groups**
- **Persistent admin authentication & commands:**  
  `/auth` (one-time), `/stop`, `/restart`. Auth status auto-restored on restart.

---

## Installation & Usage

1. **Install required package**
    ```bash
    pip install python-telegram-bot
    ```

2. **Prepare your config**
    - Copy `copy.config.json` to `config.json`
    - Fill in `TOKEN`, `ADMIN_ID`, `NOTICE_CHAT_ID`
    ```json
    {
        "TOKEN": "YOUR_BOT_TOKEN",
        "ADMIN_ID": 123456789,
        "NOTICE_CHAT_ID": -1001234567890
    }
    ```

3. **Run the bot**
    ```bash
    python ban_bot.py
    ```

4. **Authenticate (one-time):**
    Send `/auth` as ADMIN_ID in Telegram.  
    No need to authenticate again after restart.

---

## Commands

- `/auth`: authenticate the bot (admin only, once)
- `/stop`: pause the bot (admin only)
- `/restart`: resume the bot (admin only)

---

## Ban/Moderation details & FAQ

- **Auto-kick**:  
  On join, a human user is immediately banned and unbanned from the group.
  *Note: even after being removed, users can still post comments via the notice/channel post (Telegram limitation) unless they're re-invited.*

- **How to re-invite kicked users:**  
  Pause the bot via `/stop`, add the person manually, then `/restart` the bot.

- **Reply moderation:**  
    1. **First ever comment**
        - Contains a link → ban from both chat_id/NOTICE_CHAT_ID, delete message.
        - No link → send welcome reply, track as regular user.
    2. **Existing user**
        - Any comment with a link is deleted (but no ban).
        - Comments without links are always welcome.

---

## Notes

- **The bot must be admin** in both your notice channel and group/discussion for delete/kick to work!
- All data (`writers.json`, `auth_status.json` etc.) are auto-managed in the bot's directory.