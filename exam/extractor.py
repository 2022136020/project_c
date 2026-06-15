import os
import json
import re
import base64

import anthropic

def _make_client(api_key: str) -> anthropic.Anthropic:
    if not api_key or not api_key.startswith("sk-"):
        raise ValueError("올바른 Anthropic API 키를 입력해 주세요 (sk-ant-... 형식).")
    return anthropic.Anthropic(api_key=api_key)


PROMPT = """이 이미지는 학생이 답을 작성하고 채점된 시험지 사진입니다.

【무조건 무시할 것 — 학생/채점자가 추가한 모든 것】
- 연필·볼펜·색연필로 손으로 쓴 답안
- 채점 기호: O, X, /, ✓, 별표, 점수 숫자, 동그라미, 밑줄, 취소선
- 교사 메모·도장·스탬프

【추출 대상 — 인쇄된 원본만】
- 시험 제목, 과목, 날짜, 학년·반·이름 입력 필드 텍스트
- 지시사항 (※, ○ 주의 등)
- 문제 번호와 문제 본문
- 선택지 (①②③④⑤ 또는 ㄱㄴㄷ 등)
- [보기] <조건> 등 지문·조건 박스 내용
- 점수 배점
- 서술형 빈 답안 줄 (개수만 파악)
- 그림·표 위치는 "[그림]" "[표]" 텍스트로 대체

아래 JSON만 반환하세요 (설명·마크다운 없이 순수 JSON):
{
  "header": {
    "title": "시험 제목 (없으면 null)",
    "subject": "과목명 (없으면 null)",
    "info_line": "학년/반/이름/날짜 등 한 줄 (없으면 null)"
  },
  "instructions": "지시사항 전체 문자열 (없으면 null)",
  "items": [
    {
      "type": "question",
      "number": 1,
      "content": "문제 본문 텍스트",
      "sub_content": "추가 조건·지문 (없으면 null)",
      "options": ["① 보기1", "② 보기2"],
      "points": 5,
      "answer_lines": 0
    },
    {
      "type": "passage",
      "label": "[보기]",
      "content": "지문 내용"
    },
    {
      "type": "section_header",
      "content": "단원 제목 예: ▶ 1단원"
    }
  ]
}

type 값: "question" | "passage" | "section_header"
answer_lines: 객관식=0, 단답형=1, 서술형=줄수(2~6)
options: 선택지 없으면 []
"""


def _detect_mime(image_bytes: bytes) -> str:
    if image_bytes[:8] == b'\x89PNG\r\n\x1a\n':
        return "image/png"
    if image_bytes[:2] == b'\xff\xd8':
        return "image/jpeg"
    if image_bytes[:4] == b'RIFF' and image_bytes[8:12] == b'WEBP':
        return "image/webp"
    return "image/jpeg"


def extract_page(image_bytes: bytes, api_key: str) -> dict:
    """Send one exam paper image to Claude and return structured exam content."""
    client = _make_client(api_key)
    mime = _detect_mime(image_bytes)
    b64 = base64.standard_b64encode(image_bytes).decode()

    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": mime, "data": b64}},
                {"type": "text", "text": PROMPT},
            ],
        }],
    )

    raw = msg.content[0].text.strip()
    # Strip markdown code fences if model wraps output
    raw = re.sub(r"^```(?:json)?\s*\n?", "", raw, flags=re.MULTILINE)
    raw = re.sub(r"\n?```\s*$", "", raw, flags=re.MULTILINE)
    raw = raw.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        m = re.search(r"\{[\s\S]*\}", raw)
        if m:
            return json.loads(m.group())
        raise ValueError(f"Claude 응답을 JSON으로 파싱할 수 없습니다:\n{raw[:400]}")
