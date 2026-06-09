"""
PPT → HTML 슬라이드쇼 변환기
PowerPoint COM을 이용해 각 슬라이드를 PNG로 내보낸 뒤
GitHub Pages용 HTML 파일로 묶습니다.

사용법:
  py make_html.py

출력:
  docs/slides/slide_01.png ... slide_NN.png
  docs/presentation.html
"""

import os
import glob
import subprocess

PPTX_PATH  = r"C:\project_c\portfolio-tracker\presentation\portfolio-tracker-final.pptx"
SLIDES_DIR = r"C:\project_c\portfolio-tracker\docs\slides"
HTML_PATH  = r"C:\project_c\portfolio-tracker\docs\presentation.html"

# ── 1. PowerPoint COM으로 슬라이드 PNG 내보내기 ──────────────────
def export_slides():
    os.makedirs(SLIDES_DIR, exist_ok=True)
    ps_script = f"""
$ppt = New-Object -ComObject PowerPoint.Application
$ppt.Visible = [Microsoft.Office.Core.MsoTriState]::msoTrue
$prs = $ppt.Presentations.Open("{PPTX_PATH}")
$prs.Export("{SLIDES_DIR}", "PNG", 1920, 1080)
$prs.Close()
$ppt.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($ppt) | Out-Null
"""
    result = subprocess.run(
        ["powershell", "-Command", ps_script],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print("PowerPoint 내보내기 실패:")
        print(result.stderr)
        return False
    print(f"슬라이드 PNG 저장 완료: {SLIDES_DIR}")
    return True

# ── 2. HTML 생성 ─────────────────────────────────────────────────
def make_html():
    pngs = sorted(glob.glob(os.path.join(SLIDES_DIR, "*.PNG")) +
                  glob.glob(os.path.join(SLIDES_DIR, "*.png")))
    if not pngs:
        print("PNG 파일이 없습니다. export_slides()를 먼저 실행하세요.")
        return

    slides_js = ",\n    ".join(
        f'"slides/{os.path.basename(p)}"' for p in pngs
    )
    total = len(pngs)

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Portfolio Tracker — 발표 슬라이드</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      background: #1a1a2e;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      font-family: 'Segoe UI', sans-serif;
    }}
    #slide-container {{
      width: min(90vw, 160vh);
      aspect-ratio: 16/9;
      position: relative;
      box-shadow: 0 8px 40px rgba(0,0,0,0.6);
    }}
    #slide-img {{
      width: 100%;
      height: 100%;
      object-fit: contain;
      display: block;
    }}
    #controls {{
      margin-top: 16px;
      display: flex;
      align-items: center;
      gap: 16px;
      color: #ccc;
    }}
    button {{
      background: #3f51b5;
      color: white;
      border: none;
      padding: 10px 24px;
      border-radius: 6px;
      font-size: 15px;
      cursor: pointer;
      transition: background 0.2s;
    }}
    button:hover {{ background: #5c6bc0; }}
    button:disabled {{ background: #444; cursor: default; }}
    #counter {{ font-size: 15px; min-width: 80px; text-align: center; }}
    #progress {{
      width: min(90vw, 160vh);
      height: 4px;
      background: #333;
      margin-top: 8px;
      border-radius: 2px;
      overflow: hidden;
    }}
    #progress-bar {{
      height: 100%;
      background: #3f51b5;
      transition: width 0.3s;
    }}
  </style>
</head>
<body>
  <div id="slide-container">
    <img id="slide-img" src="" alt="슬라이드">
  </div>
  <div id="progress"><div id="progress-bar"></div></div>
  <div id="controls">
    <button id="btn-prev" onclick="move(-1)">◀ 이전</button>
    <span id="counter"></span>
    <button id="btn-next" onclick="move(1)">다음 ▶</button>
  </div>

  <script>
    const slides = [
    {slides_js}
    ];
    const total = {total};
    let cur = 0;

    function render() {{
      document.getElementById('slide-img').src = slides[cur];
      document.getElementById('counter').textContent = (cur + 1) + ' / ' + total;
      document.getElementById('btn-prev').disabled = cur === 0;
      document.getElementById('btn-next').disabled = cur === total - 1;
      document.getElementById('progress-bar').style.width = ((cur + 1) / total * 100) + '%';
    }}

    function move(d) {{
      cur = Math.max(0, Math.min(total - 1, cur + d));
      render();
    }}

    document.addEventListener('keydown', e => {{
      if (e.key === 'ArrowRight' || e.key === ' ') move(1);
      if (e.key === 'ArrowLeft') move(-1);
    }});

    render();
  </script>
</body>
</html>"""

    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML 생성 완료: {HTML_PATH}")


# ── 실행 ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== PPT → HTML 변환 시작 ===")
    print(f"PPTX: {PPTX_PATH}")

    if not os.path.exists(PPTX_PATH):
        print(f"\n[오류] PPTX 파일이 없습니다.")
        print("먼저 'py make_ppt_final.py' 를 실행해서 PPT를 생성하세요.")
    else:
        ok = export_slides()
        if ok:
            make_html()
            print("\n완료! GitHub Pages 배포 방법:")
            print("  1. docs/slides/ 폴더와 docs/presentation.html 을 git add")
            print("  2. git commit & push")
            print("  3. GitHub Pages 설정에서 /docs 폴더 선택")
            print("  4. https://{username}.github.io/{repo}/presentation.html 접속")
