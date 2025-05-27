# Telegram 자동 강제퇴장 봇

이 봇은 텔레그램 그룹에 새로 들어오는 모든 "사람" 멤버를 자동으로 강퇴(추방)하는 프로그램입니다.  
관리자는 `/stop`, `/restart` 명령으로 봇의 동작을 일시정지/재시작할 수 있습니다.

## 주요 기능

- 새로 들어온 사람 멤버를 자동으로 강퇴(즉시 언밴하여 재초대 가능).
- 봇 멤버의 경우 감지만 하며 강퇴하지 않음.
- `ADMIN_ID`로 지정한 관리자만 `/stop`, `/restart` 명령 가능.
- `config.json` 파일로 쉽게 환경설정.

## 필요환경

- Python 3.8 이상
- 텔레그램 봇 토큰 ([@BotFather](https://t.me/BotFather)에서 발급)

### 필수 설치 패키지

아래 명령어로 의존성 패키지를 설치하세요:
```bash
pip install python-telegram-bot
```

## 사용법

1. **저장소 클론 및 폴더 이동**

2. **설정파일 작성**
   - `copy.config.json`을 복사해 `config.json`으로 파일명을 바꿉니다.
   - `config.json`을 열어 아래처럼 값을 입력하세요.
     - `TOKEN`: [@BotFather](https://t.me/BotFather)에서 받은 봇 토큰
     - `ADMIN_ID`: 자신의 텔레그램(숫자) 유저 ID

    예시:
    ```json
    {
        "TOKEN": "YOUR_BOT_TOKEN",
        "ADMIN_ID": 123456789
    }
    ```

3. **봇 실행**
   ```bash
   python ban_bot.py
   ```

## 명령어

- `/stop` — 봇 일시정지 (관리자만)
- `/restart` — 봇 재시작 (관리자만)

## 추가 안내

- 강퇴 방식: 사용자를 곧바로 강퇴/언밴하여 재초대가 가능합니다.
- 오직 `ADMIN_ID`로 지정한 관리자만 제어 명령을 내릴 수 있습니다.  

---

# Telegram Auto-Kick Ban Bot

This is a simple Telegram bot that automatically bans any new human user who joins your group.  
Admins can pause (`/stop`) or resume (`/restart`) the bot with commands.

## Features

- Auto-kicks (bans & instantly unbans) every new human member upon joining.
- Bots are detected and NOT kicked.
- Only the specified admin (by ID) can control the bot's pause/resume.
- Includes easy setup with a configuration file.

## Requirements

- Python 3.8+
- Telegram bot token (get from [@BotFather](https://t.me/BotFather))

### Required Python Packages
Install dependencies with:
```bash
pip install python-telegram-bot
```

## Setup

1. **Clone this repository** and enter the folder.

2. **Create your config file**
   - Copy `copy.config.json` and rename it to `config.json`.
   - Edit `config.json` and fill in your values:
     - `TOKEN`: your bot token from [@BotFather](https://t.me/BotFather)
     - `ADMIN_ID`: your Telegram numeric user ID

   Example:
   ```json
   {
       "TOKEN": "YOUR_BOT_TOKEN",
       "ADMIN_ID": 123456789
   }
   ```

3. **Run the bot**
   ```bash
   python ban_bot.py
   ```

## Commands

- `/stop` — Pause the bot (admin only).  
- `/restart` — Resume the bot (admin only).

## Notes

- The bot auto-bans (and instantly unbans) new users so they can be invited again.  
- Only ADMIN_ID can control pause/restart. Other commands/messages are ignored.