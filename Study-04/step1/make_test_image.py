"""테스트용 냉장고 이미지를 생성합니다."""
from PIL import Image, ImageDraw, ImageFont
import os

W, H = 640, 480
bg = Image.new("RGB", (W, H), (245, 245, 250))
draw = ImageDraw.Draw(bg)

# 냉장고 외곽
draw.rectangle([10, 10, W-10, H-10], outline=(150, 150, 160), width=3)
draw.rectangle([10, 10, W-10, 30], fill=(180, 180, 190))
draw.text((20, 14), "REFRIGERATOR", fill=(50, 50, 60))

items = [
    # (x, y, w, h, color, label_ko, label_en)
    (30,  50,  90, 120, (255, 120,  50), "당근",   "Carrots x3"),
    (140, 50,  90, 120, (80,  180,  80), "상추",   "Lettuce"),
    (250, 50,  90, 120, (255, 220,  50), "계란",   "Eggs x6"),
    (360, 50,  90, 120, (240,  60,  60), "토마토", "Tomatoes x4"),
    (470, 50,  90, 120, (200, 200, 255), "우유",   "Milk 1L"),

    (30,  200, 90, 100, (255, 200,  80), "치즈",   "Cheese"),
    (140, 200, 90, 100, (200, 230, 200), "두부",   "Tofu"),
    (250, 200, 90, 100, (255, 160, 100), "소시지", "Sausage"),
    (360, 200, 90, 100, (180, 220, 255), "요거트", "Yogurt"),
    (470, 200, 90, 100, (240, 200, 200), "돼지고기","Pork 200g"),

    (30,  330, 90,  80, (200, 255, 200), "오이",   "Cucumber x2"),
    (140, 330, 90,  80, (100, 180, 100), "시금치", "Spinach"),
    (250, 330, 90,  80, (255, 240, 150), "양파",   "Onion x2"),
    (360, 330, 90,  80, (180, 140, 100), "마늘",   "Garlic"),
    (470, 330, 90,  80, (150, 200, 255), "간장",   "Soy sauce"),
]

try:
    font_sm = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 13)
    font_en = ImageFont.truetype("C:/Windows/Fonts/arial.ttf",  11)
except Exception:
    font_sm = ImageFont.load_default()
    font_en = font_sm

for (x, y, w, h, color, label_ko, label_en) in items:
    draw.rectangle([x, y, x+w, y+h], fill=color, outline=(100, 100, 110), width=1)
    draw.text((x+4, y+4),  label_ko, fill=(30, 30, 30),  font=font_sm)
    draw.text((x+4, y+22), label_en, fill=(60, 60, 60),  font=font_en)

out = os.path.join(os.path.dirname(__file__), "test_fridge.jpg")
bg.save(out, "JPEG", quality=90)
print(f"테스트 이미지 저장: {out}")
