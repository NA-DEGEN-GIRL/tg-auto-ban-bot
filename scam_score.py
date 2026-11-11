"""채널 새 구독자의 닉네임/username으로 스캐머 의심 점수를 매긴다 (API 호출 없는 순수 함수만).

단어는 세 등급으로 나눠 점수를 다르게 준다.
- strong: 사칭(support, admin, official ...) → 이것만으로 기준 점수 도달
- medium: 홍보/사기(airdrop, giveaway, signal ...)
- weak:   일반인도 많이 쓰는 단어(BTC, USDT ...) → 이것만으로는 절대 기준 점수에 못 미침
여기에 username 없음 / 프로필 사진 없음 / 무작위 username / 채널·관리자 사칭 신호를 더한다.

단어 목록과 기준 점수는 config.json의 "SCAM_SCORE" 키로 덮어쓸 수 있다 (ban_bot.load_scam_score_config 참고).
"""
import re
import unicodedata
from difflib import SequenceMatcher

DEFAULT_CONFIG = {
    "mode": "log",  # "log": 로그만 남김 / "ban": threshold 이상이면 영구 차단
    "threshold": 5,
    "strong": ["support", "admin", "administrator", "official", "manager", "helpdesk", "moderator",
               "customerservice", "고객센터", "관리자", "운영자", "운영팀", "공식"],
    "medium": ["airdrop", "giveaway", "signal", "signals", "invest", "investment", "profit", "vip",
               "pump", "forex", "recovery", "에어드랍", "리딩", "수익", "무료", "이벤트"],
    "weak": ["btc", "usdt", "eth", "crypto", "trader", "trading", "bitcoin", "코인"],
}

WEIGHTS = {
    "strong": 5,
    "medium": 3,
    "weak": 1,
    "impersonation": 5,
    "no_username": 2,
    "no_photo": 1,
    "random_username": 1,
}

# 라틴 문자처럼 생긴 키릴/그리스 문자 → 라틴 문자 (Ѕupport, Аdmin 같은 위장 대응)
HOMOGLYPHS = str.maketrans({
    "а": "a", "е": "e", "о": "o", "р": "p", "с": "c", "у": "y", "х": "x", "і": "i", "ј": "j",
    "ѕ": "s", "ԁ": "d", "ӏ": "l", "к": "k", "м": "m", "т": "t", "н": "h", "в": "b", "ԛ": "q",
    "ο": "o", "α": "a", "ρ": "p", "ν": "v", "τ": "t", "ι": "i", "κ": "k", "ε": "e", "υ": "u",
})
ZERO_WIDTH = re.compile(r"[​-‏⁠﻿­]")
NON_WORD = re.compile(r"[^0-9a-z가-힣]+")
HANGUL = re.compile(r"[가-힣]")


def normalize(text):
    """NFKC(전각/장식 문자 → 일반 문자) + 소문자 + 위장 문자 제거/치환"""
    text = unicodedata.normalize("NFKC", text or "")
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)  # CryptoAdmin → Crypto Admin
    text = ZERO_WIDTH.sub("", text).lower().translate(HOMOGLYPHS)
    return text


def leet_variants(text):
    """숫자/기호로 바꾼 철자 복원 (supp0rt, he1p, $upport). 1은 i/l 둘 다 시도"""
    base = text.translate(str.maketrans({"0": "o", "3": "e", "4": "a", "5": "s", "7": "t", "@": "a", "$": "s"}))
    return {base.replace("1", "i"), base.replace("1", "l")}


def tokens(text):
    """단어 단위로 자르고, 한 글자씩 띄운 연속(S U P P O R T)은 하나로 합친다"""
    out, run = [], []
    for t in NON_WORD.split(text):
        if not t:
            continue
        if len(t) == 1:
            run.append(t)
            continue
        if len(run) > 1:
            out.append("".join(run))
        run = []
        out.append(t)
    if len(run) > 1:
        out.append("".join(run))
    return out


def squash(text):
    return NON_WORD.sub("", text)


def is_random_username(username):
    """xk29fj3821 같은 무작위 username: 숫자 5개 이상이거나, 모음 없이 자음 6개 이상 연속"""
    u = (username or "").lower()
    return len(re.findall(r"\d", u)) >= 5 or bool(re.search(r"[bcdfghjklmnpqrstvwxz]{6,}", u))


def match_keywords(name, username, words, substring_in_username):
    """닉네임은 단어 단위로만, username은 (substring_in_username이면) 붙여쓴 것까지 매칭.
    한글 단어는 띄어쓰기 없이 붙여 쓰는 경우가 많아(코인고객센터) 닉네임에서도 포함 여부로 본다"""
    hits = set()
    name_n, user_n = normalize(name), normalize(username)
    for variant in leet_variants(name_n) | {name_n}:
        toks = set(tokens(variant))
        for w in words:
            wn = normalize(w)
            if wn in toks or (HANGUL.search(wn) and wn in squash(variant)):
                hits.add(w)
    for variant in leet_variants(user_n) | {user_n}:
        toks = set(tokens(variant))
        # 붙여쓴 username(cryptoadmin, officialxx)은 영문 덩어리의 앞/뒤에 붙은 경우만 인정 (badminton 오탐 방지)
        runs = re.findall(r"[a-z]+", variant)
        for w in words:
            wn = normalize(w)
            if wn in toks or (substring_in_username and len(wn) >= 4
                              and any(r.startswith(wn) or r.endswith(wn) or r.endswith(wn + "s") for r in runs)):
                hits.add(w)
    return hits


def impersonation_targets(name, username, channel_title, admins):
    """채널 이름을 포함하거나 관리자 이름/username과 거의 같으면 사칭으로 본다.
    admins: [(user_id, display_name, username), ...]"""
    me = squash(normalize(name)) + "|" + squash(normalize(username))
    hits = []
    title = squash(normalize(channel_title))
    if len(title) >= 4 and title in me:
        hits.append(f"채널명({channel_title})")
    for _, a_name, a_user in admins:
        for target in (a_name, a_user):
            t = squash(normalize(target))
            if len(t) < 4:
                continue
            for mine in (squash(normalize(name)), squash(normalize(username))):
                if mine and (t in mine or SequenceMatcher(None, t, mine).ratio() >= 0.85):
                    hits.append(f"관리자({target})")
                    break
    return sorted(set(hits))


def score_user(name, username, has_photo, channel_title, admins, cfg):
    """(점수, 사유 목록) 반환. has_photo가 None이면(조회 실패) 사진 신호는 건너뛴다"""
    score, reasons = 0, []
    for level, sub in (("strong", True), ("medium", True), ("weak", False)):
        hits = match_keywords(name, username, cfg.get(level, []), substring_in_username=sub)
        if hits:
            # 같은 등급 단어가 여러 개여도 한 번만 (BTC USDT ETH 나열로 점수 폭증 방지)
            score += WEIGHTS[level]
            reasons.append(f"{level}:{','.join(sorted(hits))}")
    imp = impersonation_targets(name, username, channel_title, admins)
    if imp:
        score += WEIGHTS["impersonation"]
        reasons.append("사칭:" + ",".join(imp))
    if not username:
        score += WEIGHTS["no_username"]
        reasons.append("username없음")
    elif is_random_username(username):
        score += WEIGHTS["random_username"]
        reasons.append("무작위username")
    if has_photo is False:
        score += WEIGHTS["no_photo"]
        reasons.append("사진없음")
    return score, reasons
