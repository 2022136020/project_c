"""Step 1(이미지 분석) → Step 2(레시피 생성) 통합 테스트"""
import json
import sys
import time
import requests

BASE = "http://localhost:5001"
IMG  = "test_fridge.jpg"
SEP  = "=" * 60


def hr(title=""):
    print(f"\n{SEP}")
    if title:
        print(f"  {title}")
        print(SEP)


# ── Step 1: 이미지 분석 ────────────────────────────────────
hr("STEP 1 — 냉장고 이미지 분석")
print(f"  이미지: {IMG}")
print(f"  엔드포인트: POST {BASE}/api/analyze\n")

def post_with_retry(url, *, files=None, json=None, timeout=120, max_wait=180):
    """429 시 retry_after 만큼 대기 후 재시도 (최대 max_wait초)."""
    for attempt in range(5):
        if files:
            # 파일 포인터 리셋
            for v in files.values():
                try: v[1].seek(0)
                except Exception: pass
            r = requests.post(url, files=files, timeout=timeout)
        else:
            r = requests.post(url, json=json, timeout=timeout)

        if r.status_code != 429:
            return r

        wait = min(r.json().get("retry_after", 60), max_wait)
        print(f"  ⏳ Rate limit — {wait}초 대기 중... (시도 {attempt+1}/5)")
        for s in range(wait, 0, -10):
            print(f"     남은 대기: {s}초", end="\r")
            time.sleep(min(10, s))
        print()
    return r  # 5회 모두 실패 시 마지막 응답 반환

t0 = time.time()
with open(IMG, "rb") as f:
    resp = post_with_retry(
        f"{BASE}/api/analyze",
        files={"image": ("test_fridge.jpg", f, "image/jpeg")},
    )
elapsed1 = time.time() - t0

print(f"  HTTP 상태: {resp.status_code}  ({elapsed1:.1f}초)")

if resp.status_code != 200:
    print(f"  [FAIL] 오류 응답: {resp.text[:300]}")
    sys.exit(1)

data1 = resp.json()
model1       = data1.get("model", "?")
ingredients  = data1.get("ingredients") or []
raw_text1    = data1.get("raw_text", "")

print(f"  사용 모델: {model1}")
print(f"  JSON 파싱: {'성공' if data1.get('ingredients') is not None else '실패 (원문 폴백)'}")
print()

if ingredients:
    from collections import defaultdict
    groups = defaultdict(list)
    for ing in ingredients:
        groups[ing.get("category", "기타")].append(ing)

    for cat, items in sorted(groups.items()):
        print(f"  [{cat}]")
        for it in items:
            print(f"    • {it['name']}  {it.get('quantity','')}")
    print(f"\n  ✅ 인식된 재료 총 {len(ingredients)}개")
else:
    print("  원문 응답 (JSON 파싱 실패):")
    print("  " + raw_text1[:400])

# ── Step 2: 레시피 생성 ────────────────────────────────────
hr("STEP 2 — 레시피 생성")

if not ingredients:
    # 파싱 실패 시 기본 재료로 테스트
    ingredients = [
        {"name": "당근",  "quantity": "2개",   "category": "채소"},
        {"name": "계란",  "quantity": "6개",   "category": "유제품"},
        {"name": "양파",  "quantity": "1개",   "category": "채소"},
        {"name": "돼지고기","quantity":"200g", "category": "육류"},
    ]
    print("  ⚠️  Step1 파싱 실패 → 기본 재료 4개로 대체")

options = {
    "count":      2,
    "servings":   2,
    "max_time":   30,
    "dietary":    "none",
    "difficulty": "보통",
}

print(f"  재료 {len(ingredients)}개 → 레시피 {options['count']}개 요청")
print(f"  인원: {options['servings']}명 / 최대 {options['max_time']}분 / 식이제한: 없음")
print(f"  엔드포인트: POST {BASE}/api/recipe\n")

t1 = time.time()
resp2 = post_with_retry(
    f"{BASE}/api/recipe",
    json={"ingredients": ingredients, "options": options},
)
elapsed2 = time.time() - t1

print(f"  HTTP 상태: {resp2.status_code}  ({elapsed2:.1f}초)")

if resp2.status_code != 200:
    print(f"  [FAIL] 오류: {resp2.text[:300]}")
    sys.exit(1)

data2   = resp2.json()
model2  = data2.get("model_used", "?")
recipes = data2.get("recipes") or []
cached  = data2.get("from_cache", False)

print(f"  사용 모델: {model2}")
print(f"  캐시 응답: {'예' if cached else '아니오'}")
print(f"  JSON 파싱: {'성공' if data2.get('recipes') is not None else '실패 (원문 폴백)'}")
print()

if recipes:
    for i, r in enumerate(recipes, 1):
        print(f"  ── 레시피 {i}: {r.get('title','?')} ──")
        print(f"     설명: {r.get('description','')}")
        print(f"     난이도: {r.get('difficulty','?')}  /  조리시간: {r.get('cook_time','?')}분  /  {r.get('servings','?')}인분")

        ings = r.get("ingredients", [])
        if ings:
            print(f"     재료 ({len(ings)}개):", ", ".join(x["name"] for x in ings[:6]),
                  "..." if len(ings) > 6 else "")

        steps = r.get("steps", [])
        print(f"     조리 단계: {len(steps)}단계")
        for j, s in enumerate(steps[:3], 1):
            print(f"       {j}. {s[:60]}{'...' if len(s)>60 else ''}")
        if len(steps) > 3:
            print(f"       ... 외 {len(steps)-3}단계")

        missing = r.get("missing_ingredients", [])
        if missing:
            print(f"     없는 재료: {', '.join(missing)}")
        print()
    print(f"  ✅ 레시피 {len(recipes)}개 생성 완료")
else:
    print("  원문 응답 (JSON 파싱 실패):")
    print("  " + (data2.get("raw_text") or "")[:500])

# ── 캐시 테스트 ────────────────────────────────────────────
hr("캐시 검증 — 동일 요청 재전송")
t2 = time.time()
resp3 = requests.post(
    f"{BASE}/api/recipe",
    json={"ingredients": ingredients, "options": options},
    timeout=10,
)
elapsed3 = time.time() - t2
d3 = resp3.json()
print(f"  HTTP 상태: {resp3.status_code}  ({elapsed3:.2f}초)")
print(f"  캐시 히트: {'✅ 예' if d3.get('from_cache') else '❌ 아니오'}")

# ── 최종 요약 ────────────────────────────────────────────────
hr("테스트 결과 요약")
print(f"  [Step 1] 이미지 분석    {'✅ 성공' if ingredients else '❌ 실패'}  ({elapsed1:.1f}초)  모델: {model1}")
print(f"  [Step 2] 레시피 생성    {'✅ 성공' if recipes else '❌ 실패'}  ({elapsed2:.1f}초)  모델: {model2}")
print(f"  [캐시]   재요청 속도    {elapsed3:.2f}초 ({'캐시 적중' if d3.get('from_cache') else '캐시 미스'})")
print()
