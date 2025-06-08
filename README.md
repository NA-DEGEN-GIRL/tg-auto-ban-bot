# Telegram 자동 강제퇴장 & 스팸 댓글 방지 봇

텔레그램 그룹/공지방 운영을 위한 자동화 봇입니다.

## 주요 기능

- **자동 강퇴:** 그룹에 새로 들어온 "사람" 멤버를 자동 강퇴(언밴 포함)하여 다시 초대가 가능합니다.
- **스팸 링크 댓글 강퇴:**  
  공지방(채널) 또는 포워딩/토론방에서 공지글에 댓글 형태로 http(s) 링크가 포함된 메시지가 올라오면 **메시지를 즉시 삭제**하고, 사용자를 **그룹 및 공지방(chat_id, NOTICE_CHAT_ID 모두)에서 강퇴**합니다.
- **첫 댓글 환영 메시지:**  
  사용자가 해당 그룹에서 처음 댓글을 남길 경우 환영 메시지를 띄워줍니다. (링크 댓글/스팸 제외)
- **관리자 인증 영속 저장:**  
  인증 상태를 json 파일에 저장하여, 봇 재시작 시 재인증이 필요 없습니다.
- **관리자 명령:**  
  `/auth`(최초 1회), `/stop`, `/restart` 명령어로 봇을 제어할 수 있습니다.
- **원본/토론 그룹 둘 다 대응:**  
  공지방, 연결된 그룹 모두에서 동작.

---

## 필요 환경

- Python 3.8 이상
- 텔레그램 봇 토큰 ([@BotFather](https://t.me/BotFather)에서 발급)
- python-telegram-bot 패키지

### 설치 방법

```bash
pip install python-telegram-bot
```

---

## 사용법

1. **저장소 클론 및 폴더 이동**

2. **설정파일 작성**
    - `copy.config.json`을 `config.json`으로 복사
    - 값을 입력:
        - `TOKEN`: [@BotFather](https://t.me/BotFather)에서 받은 봇 토큰
        - `ADMIN_ID`: 자신의 텔레그램(숫자) 유저 ID
        - `NOTICE_CHAT_ID`: 관리할 "공지방"의 chat_id (예시: `-1001234567890`)

    ```json
    {
        "TOKEN": "YOUR_BOT_TOKEN",
        "ADMIN_ID": 123456789,
        "NOTICE_CHAT_ID": -1002342342342
    }
    ```

3. **봇 실행**
   ```bash
   python ban_bot.py
   ```

4. **최초 인증**
    - 텔레그램에서 ADMIN_ID 계정으로 `/auth` 명령어를 봇에게 보내 인증을 완료하세요.
    - 인증 완료 후 재실행 시 추가 인증이 필요 없습니다.

---

## 명령어

- `/auth` — 관리자 인증 (최초 1회, 관리자만)
- `/stop` — 봇 일시정지 (관리자만)
- `/restart` — 봇 재시작 (관리자만)

---

## 기타 안내

- 메시지 삭제/강퇴 기능을 위해 **봇을 공지방/그룹 모두에 '관리자'로 등록**해야 정상 동작합니다.
- writers.json, auth_status.json 등 데이터 파일은 봇 실행 폴더에 자동 관리됩니다.

---

# Telegram Auto-Kick & Anti Spam-Reply Bot

A powerful bot for managing your Telegram group/channel with automatic banning and spam link removal.

## Features

- **Auto-kick:** Instantly bans & unbans every new human member for spam protection (re-invitation possible).
- **Anti link-reply spam:**  
  If a reply (comment) containing an http(s) link is posted to a notice/channel message (including in forward/discussion groups), the bot deletes the message and bans the user from both chat_id and NOTICE_CHAT_ID.
- **Welcome first comment:**  
  New users posting their first comment in the group (non-link) are greeted with a welcome message.
- **Admin authentication persistence:**  
  Auth status is saved to a file, so no need to re-authenticate after bot restart.
- **Admin commands:**  
  `/auth` (one-time), `/stop`, `/restart`
- **Works both in main notice channel and discussion groups.**

## Requirements

- Python 3.8+
- Telegram bot token (get from [@BotFather](https://t.me/BotFather))
- python-telegram-bot package

### Install

```bash
pip install python-telegram-bot
```

## Setup

1. **Clone this repository and cd into the folder.**

2. **Configure your settings:**  
   - Copy `copy.config.json` to `config.json`
   - Fill in:
        - `TOKEN`: (Your bot token)
        - `ADMIN_ID`: (Numeric telegram user id)
        - `NOTICE_CHAT_ID`: (Your notice channel chat id, e.g. `-100xxxx`)

    Example:
    ```json
    {
        "TOKEN": "YOUR_BOT_TOKEN",
        "ADMIN_ID": 123456789,
        "NOTICE_CHAT_ID": -1002342342342
    }
    ```

3. **Run**
   ```bash
   python ban_bot.py
   ```

4. **Authenticate (one-time):**  
   Send `/auth` as ADMIN_ID to the bot in Telegram.
   No need to authenticate again after restart.

## Commands

- `/auth` — Authenticate the bot (admin only, once)
- `/stop` — Pause the bot (admin only)
- `/restart` — Resume the bot (admin only)

---

## Notes

- For message deletion and ban/unban features to work, you must add the bot as an **admin** in both your notice channel and discussion group!
- writers.json, auth_status.json and other data files are automatically managed in the bot's folder.