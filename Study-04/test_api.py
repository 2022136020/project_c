import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}


def test_text(model: str, prompt: str) -> None:
    print(f"\n{'='*60}")
    print(f"[텍스트 생성] 모델: {model}")
    print(f"프롬프트: {prompt}")
    print("-" * 60)

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
    }
    for attempt in range(3):
        resp = requests.post(BASE_URL, headers=HEADERS, json=payload, timeout=60)
        if resp.status_code == 429:
            wait = 10 * (attempt + 1)
            print(f"Rate limit -- {wait}초 후 재시도... ({attempt+1}/3)")
            time.sleep(wait)
            continue
        resp.raise_for_status()
        break
    data = resp.json()
    content = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})
    print(f"응답:\n{content}")
    print(f"\n토큰 사용: 입력 {usage.get('prompt_tokens', '-')} / 출력 {usage.get('completion_tokens', '-')}")


def test_image(model: str, image_url: str, question: str) -> None:
    print(f"\n{'='*60}")
    print(f"[이미지 인식] 모델: {model}")
    print(f"이미지 URL: {image_url}")
    print(f"질문: {question}")
    print("-" * 60)

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": image_url}},
                    {"type": "text", "text": question},
                ],
            }
        ],
    }
    for attempt in range(3):
        resp = requests.post(BASE_URL, headers=HEADERS, json=payload, timeout=60)
        if resp.status_code == 429:
            wait = 10 * (attempt + 1)
            print(f"Rate limit -- {wait}초 후 재시도... ({attempt+1}/3)")
            time.sleep(wait)
            continue
        resp.raise_for_status()
        break
    data = resp.json()
    content = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})
    print(f"응답:\n{content}")
    print(f"\n토큰 사용: 입력 {usage.get('prompt_tokens', '-')} / 출력 {usage.get('completion_tokens', '-')}")


if __name__ == "__main__":
    print("OpenRouter API 테스트 시작")
    print(f"API 키 확인: {'OK (' + API_KEY[:12] + '...)' if API_KEY else 'NOT FOUND'}")

    # 1. 텍스트 생성 테스트
    # (qwen3.6-plus:free / qwen3-coder:free 모두 upstream rate-limited 상태 — 현재 응답 중인 대체 모델 사용)
    test_text(
        model="google/gemma-3-4b-it:free",
        prompt="파이썬으로 피보나치 수열을 구하는 가장 간단한 코드를 작성해줘. 한국어로 설명도 포함해.",
    )

    # 2. 이미지 인식 테스트 (공개 샘플 이미지)
    # (gemma-3-27b-it:free upstream rate-limited — 4b 버전으로 대체)
    test_image(
        model="google/gemma-3-4b-it:free",
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/280px-PNG_transparency_demonstration_1.png",
        question="이 이미지에 무엇이 보이나요? 한국어로 설명해주세요.",
    )

    print(f"\n{'='*60}")
    print("테스트 완료")
