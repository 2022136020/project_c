import os
import win32com.client
import shutil

PPT_PATH = os.path.abspath("portfolio-tracker.pptx")
OUT_DIR = os.path.abspath("../../docs")
IMG_DIR = os.path.join(OUT_DIR, "slides")

os.makedirs(IMG_DIR, exist_ok=True)

print("PowerPoint 열기...")
ppt_app = win32com.client.Dispatch("PowerPoint.Application")
ppt_app.Visible = True

presentation = ppt_app.Presentations.Open(PPT_PATH)
slide_count = presentation.Slides.Count
print(f"슬라이드 수: {slide_count}")

for i in range(1, slide_count + 1):
    img_path = os.path.join(IMG_DIR, f"slide_{i:02d}.png")
    presentation.Slides(i).Export(img_path, "PNG", 1920, 1080)
    print(f"  slide {i}/{slide_count} 저장 완료")

presentation.Close()
ppt_app.Quit()
print("변환 완료")

# HTML 생성
slides_html = ""
for i in range(1, slide_count + 1):
    display = "block" if i == 1 else "none"
    slides_html += f'  <img id="slide-{i}" class="slide" src="slides/slide_{i:02d}.png" style="display:{display}">\n'

html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Portfolio Tracker 발표자료</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ background: #1a1a1a; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; font-family: sans-serif; }}
    .slide {{ max-width: 100%; max-height: 80vh; border-radius: 4px; box-shadow: 0 8px 32px rgba(0,0,0,0.5); }}
    .controls {{ margin-top: 20px; display: flex; align-items: center; gap: 16px; }}
    button {{ background: #333; color: #fff; border: 1px solid #555; padding: 10px 24px; border-radius: 6px; cursor: pointer; font-size: 16px; }}
    button:hover {{ background: #444; }}
    button:disabled {{ opacity: 0.3; cursor: default; }}
    .counter {{ color: #aaa; font-size: 15px; min-width: 80px; text-align: center; }}
    .progress {{ position: fixed; top: 0; left: 0; height: 3px; background: #4a9eff; transition: width 0.2s; }}
  </style>
</head>
<body>
  <div class="progress" id="progress"></div>
{slides_html}
  <div class="controls">
    <button id="prev" onclick="move(-1)" disabled>&#9664; 이전</button>
    <span class="counter" id="counter">1 / {slide_count}</span>
    <button id="next" onclick="move(1)">다음 &#9654;</button>
  </div>

  <script>
    var current = 1;
    var total = {slide_count};

    function move(dir) {{
      document.getElementById('slide-' + current).style.display = 'none';
      current += dir;
      document.getElementById('slide-' + current).style.display = 'block';
      document.getElementById('counter').textContent = current + ' / ' + total;
      document.getElementById('prev').disabled = current === 1;
      document.getElementById('next').disabled = current === total;
      document.getElementById('progress').style.width = (current / total * 100) + '%';
    }}

    document.addEventListener('keydown', function(e) {{
      if ((e.key === 'ArrowRight' || e.key === 'ArrowDown') && current < total) move(1);
      if ((e.key === 'ArrowLeft' || e.key === 'ArrowUp') && current > 1) move(-1);
    }});

    document.getElementById('progress').style.width = (1 / total * 100) + '%';
  </script>
</body>
</html>"""

with open(os.path.join(OUT_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(html)

print(f"HTML 생성 완료: {OUT_DIR}/index.html")
