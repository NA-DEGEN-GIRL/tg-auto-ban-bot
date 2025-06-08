# Telegram 자동 강제퇴장 & 스팸 댓글 방지 봇

텔레그램 그룹/공지방(채널/토론방 등) 운영을 위한 강력한 자동화 봇입니다.

## 주요 기능

- **자동 강퇴:**  
  그룹에 새로 들어온 "사람" 멤버를 자동으로 강퇴(즉시 언밴하여 재초대 가능).  
  *봇 계정은 강퇴하지 않습니다.*

- **스팸 링크 댓글 완전 차단 및 추방 로직:**  
  - 사용자가 **해당 그룹/채널에서 첫 댓글**을 남길 때,
    - **만약 그 첫 댓글에 http 또는 https로 시작하는 링크가 포함되어 있다면**
      - 해당 유저는 **그룹(chat_id)과 공지방(NOTICE_CHAT_ID) 모두에서 즉시 강퇴**됩니다.
      - 해당 메시지는 즉시 삭제됩니다.
      - (첫댓글인데 링크가 없는 경우에는 환영 인사 메시지가 자동으로 전송됩니다.)
  - 이미 댓글을 한 번이라도 작성한 뒤에는,
    - **그 후에 작성하는 모든 댓글에서 http/https 링크 사용은 항상 금지(삭제)**됩니다.
    - **링크만 삭제**되고, 유저는 강퇴되지 않습니다.

- **첫 댓글 환영 메시지:**  
  링크가 포함되지 않은 첫 댓글이라면,  
  해당 사용자에게 "첫 댓글 환영" 메시지를 그룹에 자동으로 답글로 띄워줍니다.

- **강력한 확장성:**  
  공지방(채널) 뿐만 아니라 포워딩으로 연결된 토론방에서도 댓글 판별, 일괄 동작.

- **인증 및 권한 관리:**  
  관리자는 `/auth`, `/stop`, `/restart` 명령으로만 봇을 제어할 수 있습니다.  
  인증 상태가 파일로 저장되어, 재시작 때 별도 인증이 필요 없습니다.

---

## 필요 환경

- Python 3.8 이상
- 텔레그램 봇 토큰 ([@BotFather](https://t.me/BotFather)에서 발급)
- python-telegram-bot 패키지 (pip로 설치)

### 설치 방법

```bash
pip install python-telegram-bot
```

---

## 사용법

1. **저장소 클론 및 폴더 이동**

2. **설정파일 작성**
    - `copy.config.json`을 복사하여 `config.json`으로 파일명을 변경
    - 아래 값을 입력
      - `TOKEN`: [@BotFather](https://t.me/BotFather)에서 받은 봇 토큰
      - `ADMIN_ID`: 본인(관리자) 텔레그램 유저 ID(숫자)
      - `NOTICE_CHAT_ID`: 관리할 "공지방/채널"의 chat_id(예시: `-1001234567890`)

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
   - Telegram에서 ADMIN_ID 계정으로 `/auth` 명령을 봇에게 보내 인증을 완료하면, 자동 방어 기능이 개시됩니다.
   - 인증 이후 재시작 시에는 별도 인증이 필요 없습니다.

---

## 명령어

- `/auth`: 관리자 인증(최초 1회, 관리자만)
- `/stop`: 봇 일시 정지(관리자만)
- `/restart`: 봇 재가동(관리자만)

---

## 사용자 추방/환영 상세 규칙

- **최초 그룹 또는 채널 내 댓글이 http/https 링크를 포함하면**
    - 해당 사용자는 그룹(chat_id)과 공지방(NOTICE_CHAT_ID) 두 곳 모두에서 강퇴됩니다.
    - 해당 댓글(메시지)은 즉시 삭제됩니다.
    - 만약 첫 댓글이 '링크 없이' 순수한 텍스트라면,  
      환영 인사 메시지가 자동으로 그룹에 표시됩니다.
- **이미 한 번이라도 댓글을 작성한 유저는**
    - 이후 올리는 모든 댓글에서 http/https 링크는 즉시 삭제 처리됩니다(강퇴는 아님).
    - 일반 텍스트 또는 이미지/링크 없는 답글은 모두 허용됩니다.

---

## 자동 강퇴에 대한 추가 안내

- **자동 강퇴 후 사용자의 실제 상태:**  
  이 봇은 그룹에 새로 들어온 "사람" 멤버를 즉시 강퇴(추방)합니다. 이로 인해 그룹 인원에서 제외되지만,
  **강퇴 및 즉시 언밴되어 재초대가 가능하며**,  
  필요시 관리자가 직접 사용자를 다시 초대할 수 있습니다.

- **공지방-그룹 연동주의:**  
  텔레그램의 구조상, 사용자가 그룹에서 강퇴되었더라도  
  **공지방(채널)을 통한 "댓글" 작성은 여전히 가능합니다.**  
  (공지방/포워딩 구조의 토론방 연결방식 때문에 발생하는 현상임)

- **다시 초대하고 싶을 때:**  
  강퇴된 유저를 그룹 인원으로 복귀시키려면  
  관리자가 `/stop` 명령 등으로 봇을 일시정지시킨 뒤  
  직접 해당 사용자를 초대하면 재참여가 가능합니다.

---

## 기타 안내

- **반드시 봇을 공지방/토론방(그룹) 모두에 '관리자'로 등록해야**  
  봇의 메시지 삭제·강퇴 기능이 정상 작동합니다!
- writers.json, auth_status.json 등 데이터 파일은 봇 실행 폴더에 자동 관리됩니다.

---

# Telegram Auto-Kick & Anti Spam-Reply Bot

A robust and automatic moderation bot for Telegram groups/channels.

## Features

- **Auto-kick:**  
  Instantly bans (and unbans) every new human member for spam protection (re-invite allowed).  
  *Bots are not banned.*

- **Detailed anti-link-reply ban logic:**  
  - When a user posts their **first comment** in the group/channel:
    - If that **first message contains an http or https link**,  
      the user is immediately banned from **both the group (chat_id) and the notice channel (NOTICE_CHAT_ID)**.
      The offending message is deleted.
      If the first comment contains no link, a welcome message is sent.
  - For users who have commented before:
    - **Any future comment containing an http(s) link is always deleted** (but user is NOT kicked).

- **Welcome to first comment:**  
  If the first comment (reply) contains no link, a public welcome message is sent as reply.

- **Persistent admin authentication:**  
  Auth status is remembered via a json file, so no need to re-authenticate after restart.

- **Admin commands:**  
  `/auth` (one-time), `/stop`, `/restart` (admin only)

- **Works on channel (notice), discussion, and forwarding groups.**

## Requirements

- Python 3.8+
- Telegram bot token (get from [@BotFather](https://t.me/BotFather))
- python-telegram-bot package

### Install

```bash
pip install python-telegram-bot
```

## Setup

1. **Clone this repo and enter the folder.**

2. **Configure your settings:**
    - Copy `copy.config.json` to `config.json`.
    - Fill in:
        - `TOKEN`: your bot token
        - `ADMIN_ID`: your numeric Telegram user ID
        - `NOTICE_CHAT_ID`: your main notice channel's chat id (e.g. `-100xxxx`)

    Example:
    ```json
    {
        "TOKEN": "YOUR_BOT_TOKEN",
        "ADMIN_ID": 123456789,
        "NOTICE_CHAT_ID": -1002342342342
    }
    ```

3. **Run the bot**
   ```bash
   python ban_bot.py
   ```

4. **Authenticate (one-time):**
   Send `/auth` as ADMIN_ID to the bot in Telegram.
   After that, no further authentication is required.

## Commands

- `/auth` — Authenticate the bot (admin only, once)
- `/stop` — Pause the bot (admin only)
- `/restart` — Resume the bot (admin only)

---

## Moderation & Ban Details

- **If a user's very first comment in the group/channel contains an http/https link:**
    - The user is instantly banned from BOTH the group (`chat_id`) and the notice channel (`NOTICE_CHAT_ID`).
    - The spam message is deleted.
    - If the comment contains NO link, a public welcome message is sent.
- **For existing users (not first comment):**
    - Any reply (comment) containing http(s) links is always deleted (but the user is NOT banned).
    - Plain text/comments without links are always allowed.

---

## Additional Notes on Auto-Kicking

- **What really happens after an auto-kick?**  
  When a human user joins, the bot instantly bans (kicks out) and unbans the member.
  This means the user is removed from the current group, but
  **the user can be re-invited at any time** by an admin.

- **Commenting via notice channel:**  
  Even after being banned from the group,  
  **the user can still comment on notice/channel posts** via the original channel (Telegram design!).
  This is because Telegram's forwarding/discussion group integration allows this.

- **How to re-add banned users:**  
  To genuinely invite a banned user back to the group,  
  the admin can `/stop` (pause) the bot and then issue a new invitation.
  After re-inviting, the admin can `/restart` the bot to re-activate the protection.

---

## Notes

- For ban/delete actions to work, **add the bot as an admin both in your notice channel and the associated group!**
- All data and state (writers.json, auth_status.json) is handled automatically in the bot directory.
