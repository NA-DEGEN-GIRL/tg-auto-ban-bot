# Telegram 자동 강제퇴장 & 스팸/욕설/도배 방지 봇

텔레그램 그룹/공지방(채널/토론방 등) 관리용으로 만든 자동화 필터 봇입니다.

## 주요 기능

- **자동 강퇴:**  
  새로 들어온 사용자(사람 멤버)는 자동으로 그룹에서 즉시 강퇴(언밴 포함, 재초대 가능).  
  *봇 계정은 강퇴하지 않음. `auto_kick` 설정으로 활성화/비활성화 가능*
- **스팸 링크, 홍보, 봇/claim 패턴 완벽 차단:**  
  - 첫 댓글에 http/https, 도메인, 하이퍼링크, 숨겨진 링크(`text_link`), `@xxxbot`, `claim` 등  
    "모든 형태의 홍보/스팸/봇 마케팅"이 있으면 즉시 강퇴 및 메시지 삭제.
  - 기존 유저의 스팸/링크 댓글은 해당 댓글만 즉시 삭제(강퇴 X).
- **욕설/특정 키워드(변형 포함) 필터:**  
  - BADWORDS 리스트에 등록된 단어(예: 시발, sex, 병신 등)가  
    '시a발', 's1e2x', '운12지'처럼 **중간에 4글자 내외까지 변형되어 들어가도** 모두 탐지 및 삭제.
- **도배/장문 차단:**  
  - 텍스트/캡션이 400자 이상인 메시지는 자동으로 삭제(글자수 조절 가능).
- **첫 댓글 환영 기능:**  
  - 링크·욕설·도배에 안 걸리는 첫 댓글일 경우 환영 메시지 자동 전송.
- **공지방/토론방 대응:**  
  채널, 포워딩된 토론방, discussion, 자동연동된 모든 텔레그램 채팅 지원.
- **관리자 명령 및 인증 영속:**  
  `/auth`(최초 1회), `/stop`, `/restart`  
  인증 상태는 파일로 자동 저장되어 재시작해도 인증이 유지됩니다.

---

## 설치 및 실행

1. **패키지 설치**
    ```bash
    pip install python-telegram-bot
    ```

2. **설정파일 준비**
    - `copy.config.json`을 `config.json`으로 복사 후 아래 형식으로 값 입력
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
    Telegram에서 관리자인 계정으로 `/auth` 명령을 1회 전송(이후 자동 인증).

---

## 명령어

- `/auth`: 최초 관리자 인증(관리자만, 1회)
- `/stop`: 봇 일시정지(관리자만)
- `/restart`: 봇 재시작(관리자만)

---

## 상세 동작 규칙

### 자동 강퇴 동작
- 새 유저는 그룹 입장 즉시(항목 활성화 시) 강퇴/언밴됩니다.
- 강퇴된 유저는 그룹원에선 제외되며, **공지방(채널) 원글에는 댓글을 달 수 있습니다.**
- 강퇴된 사용자를 다시 초대하려면 `/stop` 후 수동으로 초대, 이후 `/restart`로 재가동하세요.

### 스팸/광고/링크/특정 패턴 고급 필터링
- **첫 댓글:**  
  http/https, 도메인, 숨겨진 하이퍼링크, `@xxxbot`, `claim` 등  
  텔레그램의 'url', 'text_link' entity로 감지되는 **모든 링크성/스팸 패턴**이 포함된 경우  
    - 즉시 그룹/공지방에서 강퇴, 메시지는 삭제
  - 링크성 내용이 없다면 환영 메시지 전송 후 일반 유저로 처리
- **기존 유저:**  
  위 방식에 해당하는 내용이 포함된 댓글은 **즉시 삭제되나, 강퇴되지는 않음**

### 욕설/금칙어 필터
- BADWORDS 리스트의 단어(예: `["시발", "sex", ...]`)가  
  `시a발`, `ㅅ ㅂ`, `s1e2x`처럼 **중간 문자열/특수문자/숫자 등 변형**까지 감지해서 삭제
- BADWORDS_MAX_GAP 값 설정으로 글자 간 변형 허용 폭 조정

### 도배/장문 방지
- 텍스트/캡션 400자 이상인 메시지는 자동으로 삭제되고 "장문 도배 삭제" 알림 전송

---

## 코드 및 활용 주의사항

- 봇은 **공지방 및 토론방(그룹) 모두에 "관리자"** 권한으로 등록해야 삭제/강퇴가 정상 동작합니다.
- writers.json, auth_status.json 등 데이터 파일은 봇 폴더에 자동 관리됩니다.
- BADWORDS는 코드 내 상수/리스트로 수정하거나, config 등 외부 파일과 연동해도 좋습니다.
- 메시지 삭제가 여러 번 이뤄질 수 있으나(금칙어+링크+길이 등 동시 충족 시)  
  except으로 무시하므로 운영상 문제는 거의 없음.

---

## 예시로 걸러지는 패턴들

- http/https, `naver.com`, `abc123.site` (자동 도메인 링크)
- 하이퍼링크: `[구글](https://google.com)`, `[xx](kbs.com)`
- `@XXXXbot` (텔레그램 봇 홍보 계정)
- 도배 장문(400자 이상), 금칙어(변형 포함): `시12발`, `s--e!!x`, `運지` 등

---

## 영어 안내문(English Section)

# Telegram Auto-Kick & Spam/Profanity Moderation Bot

A robust automation and anti-spam/profanity bot for managing Telegram groups and notice channels.

## Features

- **Auto-kick:**  
  Kicks (and unbans) any new human (except bots). Optionally toggled with `auto_kick`.  
- **Comprehensive spam advert and link protection:**  
  - First comment: instant ban if containing http/https, domains, hidden hyperlinks ([text_link]), `@xxxbot`, certain "claim" keywords, etc.
  - Existing users: any such message is deleted but not banned.
- **Profanity/keyword detection:**  
  - Detects keywords (in `BADWORDS` list) robustly, even when split with up to N other chars (eg. `s.e.x`, `시12발`).
- **Flood/long message filter:**  
  - Any message/caption of 400 chars or more is deleted and reported.
- **Welcome message for first proper comment**
- **Supports notice channels, discussion groups, all types of Telegram chats.**
- **Persistent admin authentication:**  
  `/auth` (once), `/stop`, `/restart` (all states saved/reloaded automatically).

## Setup

1. `pip install python-telegram-bot`
2. Copy & edit `copy.config.json` to `config.json`:
    ```json
    {
        "TOKEN": "YOUR_BOT_TOKEN",
        "ADMIN_ID": 123456789,
        "NOTICE_CHAT_ID": -1001234567890
    }
    ```
3. Run `python ban_bot.py`
4. Authenticate once with `/auth` as admin user.

## Example patterns detected

- domain-only links (e.g., `google.com`)
- http/https links
- telegram bot promotion (`@XXXXbot`)
- hidden hyperlinks (`[abc](xyz.com)`)
- spam claim words
- profanity (even with extra chars)
- flood/very long messages

## Commands

- `/auth`: First-time admin authentication.
- `/stop`: Pause bot actions.
- `/restart`: Resume bot.

## Notes

- Bot must have admin authority in both channel & group/discussion.
- All state/writer/auth files are auto-managed in the bot directory.