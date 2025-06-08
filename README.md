# Telegram 자동 강제퇴장 & 스팸 댓글 방지 봇

텔레그램 그룹/공지방(채널/토론방 등) 관리용 자동화 봇입니다.

## 주요 기능

- **자동 강퇴:**  
  새로 들어온 사용자(사람)를 즉시 그룹에서 강퇴(언밴 포함, 재초대 가능). *봇 계정은 강퇴하지 않음*
- **스팸 링크 댓글 완벽 차단:**  
  - 첫 댓글에 http/https, 도메인, 하이퍼링크, 숨겨진 링크 등 "모든 형태의 링크"가 포함되면 즉시 강퇴.
  - 기존 댓글을 남긴 사용자가 링크를 포함한 댓글 작성 시 해당 댓글만 삭제(강퇴X).
- **첫 댓글 환영:**  
  링크 없는 첫 댓글에는 환영 메시지 자동 발송.
- **공지방/토론방 대응:**  
  채널, 포워딩된 토론방, discussion, 자동연동된 모든 채팅 지원.
- **권한 및 인증 영속:**  
  `/auth`(최초 1회), `/stop`, `/restart`  
  인증 상태는 자동 저장되어 재시작시 재인증 불필요.

---

## 설치 및 실행

1. **필수 패키지 설치**
    ```bash
    pip install python-telegram-bot
    ```

2. **설정파일 준비**
    `copy.config.json`을 `config.json`으로 복사 후 아래처럼 입력
    ```json
    {
        "TOKEN": "YOUR_BOT_TOKEN",
        "ADMIN_ID": 123456789,
        "NOTICE_CHAT_ID": -1001234567890
    }
    ```

3. **실행**
    ```bash
    python ban_bot.py
    ```

4. **초기 인증**
    Telegram에서 관리자인 계정으로 `/auth` 명령 전송(최초 1회).  
    인증 후에는 재시작해도 별도 인증 필요 없음.

---

## 명령어

- `/auth`: 최초 관리자 인증(관리자만)
- `/stop`: 봇 일시정지(관리자만)
- `/restart`: 봇 재시작(관리자만)

---

## 상세 동작 규칙

### 자동 강퇴 설명
- **그룹 입장 시:**  
  새로 들어온 사용자는 그룹/채널에서 바로 강퇴(즉시 언밴).  
  그룹원 수 유지 목적이며, 관리자가 직접 `/stop` 후 다시 초대 가능.
- **강퇴 후에도:**  
  사용자는 공지방(채널) 원글에 댓글을 달 수 있음(텔레그램 구조상),  
  이는 정상 동작으로 봇/텔레그램 한계임.

### 댓글/링크 필터링
- **첫 댓글:**  
  http/https, 도메인(예: naver.com), 숨겨진 하이퍼링크 등  
  텔레그램이 'url' 또는 'text_link' entity로 인식하는 **모든 링크**가 포함되어 있으면
    - 해당 유저는 그룹/공지방 모두에서 즉시 강퇴, 메시지는 삭제
    - 링크가 없다면 환영 메시지 발송 후 일반 유저로 기록
- **기존 유저:**  
  이후 모든 댓글에서 위 형태의 링크·도메인·숨겨진 하이퍼링크가 발견되면  
  해당 댓글만 삭제, 유저는 강퇴되지 않음

> **참고:**  
> "http로 시작하지 않아도 도메인(google.com 등)이나 숨겨진 하이퍼링크(마크다운/HTML)가  
> 있으면 텔레그램 엔티티 분석을 통해 모두 차단합니다."

---

## 기타 안내

- 봇이 **공지방 및 토론방(그룹) 모두의 "관리자"**여야 삭제·강퇴가 동작합니다.
- writers.json, auth_status.json 등 데이터 파일은 봇 폴더에 자동 저장/관리됩니다.

---

# Telegram Auto-Kick & Anti Spam-Reply Bot

A robust automation bot for Telegram groups and notice channels.

## Features

- **Auto-kick new users:**  
  Kicks any new user (except bots) from the group instantly (ban & unban for quick re-invite access).
- **Spam link detection/block:**  
  - *First comment:* If it contains any form of link (http/https, domain only, hidden hyperlinks [text_link], etc) — user is banned from both chat (`chat_id`) and channel (`NOTICE_CHAT_ID`), message is deleted.
  - *Existing users:* Any future comment with a link/domain/hyperlink is always deleted (but no ban).
- **Welcome first comment:**  
  If the first comment has no links, a welcome reply is sent.
- **Full support for notice/discussion/forward groups**
- **Persistent admin authentication/commands:**  
  `/auth` (once), `/stop`, `/restart`. Auth state saved to file.

---

## Installation & Usage

1. **Install python-telegram-bot**
    ```bash
    pip install python-telegram-bot
    ```

2. **Configure your config file**
    - Copy `copy.config.json` to `config.json` and edit as:
    ```json
    {
        "TOKEN": "YOUR_BOT_TOKEN",
        "ADMIN_ID": 123456789,
        "NOTICE_CHAT_ID": -1001234567890
    }
    ```

3. **Run**
    ```bash
    python ban_bot.py
    ```

4. **Initial authentication**
    Send `/auth` (as ADMIN_ID) to the bot once.  
    After the first time, restart does NOT require re-auth.

---

## Commands

- `/auth`: authenticate as admin (one-time, admin only)
- `/stop`: pause bot (admin only)
- `/restart`: resume bot (admin only)

---

## Operation details

### Auto-kick
- **On join:**  
  Any human joining is kicked from group & unbanned (can rejoin).  
  If you want to re-invite a kicked user, `/stop` the bot and invite manually; then `/restart`.

- **Note:**  
  Even a kicked user can still reply to notice/channel posts  
  (Telegram design; not a bug).

### Comment/link detection
- **First ever comment:**  
  Contains *any* type of link: http, domain (e.g. site.com), hidden hyperlink — user is banned and message deleted.  
  No link: welcome message sent and user is whitelisted.
- **Existing users:**  
  If a comment has *any* form of link (including non-http domains, hidden hyperlinks, etc), that message is deleted, but the user is NOT banned.

> **Tip:**  
> Domain-only, http-less links (naver.com, google.co.kr) and "hidden hyperlinks" ([label](site.com) style)  
> are detected and filtered, using Telegram message entities parsing.

---

## Notes

- The bot **must be admin** in both channel & group/discussion for ban/delete to work.
- Data files (`writers.json`, `auth_status.json` etc.) are managed in the bot's folder automatically.