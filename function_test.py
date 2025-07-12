import re
BADWORDS = ["김대중","운지","노짱","부엉이","노무","이기","무현","노무현"]
BADWORDS_MAX_GAP = 50
def message_contains_profanity(msg, badwords, max_gap=4):
    """
    - badwords: ['시발', 'sex', ...]
    - max_gap: 예를 들어 4면 's1e2x', '시12발'까지 허용
    """
    raw_text = msg
    cleaned_text = re.sub(r'[\s\r\n]+', '', raw_text).lower() 
    for bad in badwords:
        if len(bad) < 2:
            continue
        # 각각의 글자 사이에 .* (모든 문자 0개 이상 허용) 삽입
        pattern = ".*".join(map(re.escape, bad))
        print(f"검사패턴: {pattern}, 검사대상: {cleaned_text}")  
        # 예: '시발' → 시.*발, 'sex' → s.*e.*x, '운지' → 운.*지 ...
        if re.search(pattern, cleaned_text, re.IGNORECASE):
            print("탐지: ", bad)
            return True
    return False


print(message_contains_profanity('노무현만만세',BADWORDS,BADWORDS_MAX_GAP))