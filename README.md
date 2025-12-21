# Telegram 자동 강제퇴장 & 스팸/욕설/도배 방지 봇

텔레그램 그룹/공지방(채널/토론방 등) 관리용으로 만든 자동화 필터 봇입니다.

---

## 주요 기능

### 메인 봇 (`ban_bot.py`)
- **자동 강퇴:**  
  새로 들어온 사용자(사람 멤버)는 자동으로 그룹에서 즉시 강퇴(언밴 포함, 재초대 가능).  
  *봇 계정은 강퇴하지 않음. `auto_kick` 설정으로 활성화/비활성화 가능*
- **러시아어(키릴 문자) 닉네임 자동 영구 차단:**  
  키릴 문자가 포함된 닉네임/유저네임 감지 시 영구 강퇴 (unban 없음)
- **스팸 링크, 홍보, 봇/claim 패턴 완벽 차단:**  
  - 첫 댓글에 http/https, 도메인, 하이퍼링크, 숨겨진 링크(`text_link`), `@xxxbot`, `claim` 등  
    "모든 형태의 홍보/스팸/봇 마케팅"이 있으면 즉시 강퇴 및 메시지 삭제.
  - 기존 유저의 스팸/링크 댓글은 해당 댓글만 즉시 삭제(강퇴 X).
- **욕설/특정 키워드(변형 포함) 필터:**  
  - BADWORDS 리스트에 등록된 단어가 변형되어 있어도 탐지 및 삭제.
- **도배/장문 차단:**  
  - 텍스트/캡션이 1000자 이상인 메시지는 자동으로 삭제.
- **첫 댓글 환영 기능:**  
  - 링크·욕설·도배에 안 걸리는 첫 댓글일 경우 환영 메시지 자동 전송.

### 구독자 목록 수집 (`get_subscribers.py`)
- **Telethon(Client API)을 이용한 채널 구독자 목록 수집**
- 다양한 검색 쿼리(키릴/라틴/숫자)로 최대한 많은 구독자 수집
- 러시아어 닉네임 자동 분류 및 JSON 저장

### 일괄 강퇴 (`ban_from_list.py`)
- **수집된 JSON 파일 기반 러시아인들 일괄 강퇴**
- Bot API를 이용하여 `cyrillic_users.json`에 있는 유저들을 자동 강퇴

---

## 파일 구조

```
ban_bot/
├── ban_bot.py           # 메인 봇 (실시간 감시/강퇴/필터)
├── get_subscribers.py   # 채널 구독자 목록 수집 (Telethon)
├── ban_from_list.py     # JSON 기반 일괄 강퇴
├── config.json          # 메인 봇 설정
├── .env                 # 구독자 수집/일괄 강퇴용 환경변수
├── requirements.in      # 패키지 목록
└── README.md
```

---

## 설치

```bash
# 패키지 설치
pip install -r requirements.in

# 또는 개별 설치
pip install python-telegram-bot python-dotenv telethon
```

---

## 설정

### 1. 메인 봇 설정 (`config.json`)

`copy.config.json`을 `config.json`으로 복사 후 수정:

```json
{
    "TOKEN": "YOUR_BOT_TOKEN",
    "ADMIN_ID": 123456789,
    "NOTICE_CHAT_ID": [-1001234567890]
}
```

| 키 | 설명 |
|---|---|
| `TOKEN` | BotFather에서 발급받은 봇 토큰 |
| `ADMIN_ID` | 관리자 텔레그램 ID (숫자) |
| `NOTICE_CHAT_ID` | 감시할 채널/그룹 ID 목록 (배열) |

### 2. 구독자 수집/일괄 강퇴 설정 (`.env`)

```env
# Telegram Client API (my.telegram.org에서 발급)
API_ID=12345678
API_HASH=your_api_hash_here

# 본인 전화번호 (국가코드 포함)
PHONE=+821012345678

# 채널 username (@없이) 또는 채널 ID
CHANNEL=your_channel_username

# Bot API (일괄 강퇴용)
BOT_TOKEN=your_bot_token_here
```

#### API_ID / API_HASH 발급 방법
1. https://my.telegram.org 접속
2. 전화번호로 로그인
3. **API development tools** 클릭
4. `api_id`와 `api_hash` 복사

---

## 사용법

### 1. 메인 봇 실행

```bash
python ban_bot.py
```

**최초 인증:** 텔레그램에서 관리자 계정으로 `/auth` 명령 전송

#### 명령어

| 명령어 | 설명 |
|--------|------|
| `/auth` | 최초 관리자 인증 (1회) |
| `/stop` | 봇 일시정지 |
| `/restart` | 봇 재시작 |

### 2. 채널 구독자 목록 수집

```bash
python get_subscribers.py
```

**첫 실행 시:** 콘솔에서 텔레그램 인증 코드 입력 필요

**출력 파일:**
- `all_subscribers.json` - 전체 구독자 목록
- `cyrillic_users.json` - 러시아어 닉네임 유저만

### 3. 일괄 강퇴 실행

```bash
python ban_from_list.py
```

`cyrillic_users.json`에 있는 유저들을 순차적으로 강퇴합니다.

---

## 동작 흐름

### 실시간 감시 (ban_bot.py)
```
새 유저 입장
    ↓
봇인가? → YES → 무시
    ↓ NO
러시아어 닉네임? → YES → 영구 강퇴
    ↓ NO
일반 강퇴 (재초대 가능)
```

### 일괄 강퇴 흐름
```
1. get_subscribers.py 실행 → cyrillic_users.json 생성
2. ban_from_list.py 실행 → JSON 기반 일괄 강퇴
```

---

## 주의사항

### 보안
- `.env`, `*.session`, `config.json`은 절대 공유 금지
- `.gitignore`에 아래 항목 추가 권장:
  ```gitignore
  .env
  *.session
  *.session-journal
  config.json
  all_subscribers.json
  cyrillic_users.json
  writers.json
  auth_status.json
  ```

### 권한
- 봇은 채널/그룹에서 **관리자** 권한 필요 (특히 "사용자 차단" 권한)
- `get_subscribers.py`는 **채널 관리자 계정**으로 로그인해야 구독자 조회 가능

### 제한사항
- 채널 구독자 목록은 API 제한으로 **100% 수집 불가** (최대 ~1000-2000명)
- 이후 새 가입자는 `ban_bot.py`의 실시간 감시로 차단

---

## 예시로 걸러지는 패턴들

- http/https, `naver.com`, `abc123.site` (자동 도메인 링크)
- 하이퍼링크: `[구글](https://google.com)`, `[xx](kbs.com)`
- `@XXXXbot` (텔레그램 봇 홍보 계정)
- 러시아어 닉네임: `Иван`, `Мария`, `Сергей`
- 도배 장문(1000자 이상)
- 금칙어(변형 포함): `시12발`, `s--e!!x` 등
