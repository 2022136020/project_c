import win32com.client
import os, sys

PPT_PATH   = os.path.abspath(r"C:\project_c\portfolio-tracker\presentation\portfolio-tracker-final.pptx")
VIDEO_PATH = os.path.abspath(r"C:\Users\주성현\Videos\발표영상\PortfolioTracker.mp4")

ppt = win32com.client.Dispatch("PowerPoint.Application")
ppt.Visible = True

prs = ppt.Presentations.Open(PPT_PATH)

# 슬라이드 22번 = 시연 영상 슬라이드 (1-indexed)
VIDEO_SLIDE = 22
slide = prs.Slides(VIDEO_SLIDE)

# 기존 도형 모두 제거
while slide.Shapes.Count > 0:
    slide.Shapes(1).Delete()

# 배경 검정
slide.Background.Fill.Solid()
slide.Background.Fill.ForeColor.RGB = 0x000000

# 슬라이드 크기
W = prs.PageSetup.SlideWidth
H = prs.PageSetup.SlideHeight

# PowerPoint 엔진으로 영상 임베드 (LinkToFile=False = 완전 임베드)
shape = slide.Shapes.AddMediaObject2(
    VIDEO_PATH,
    LinkToFile=False,
    SaveWithDocument=True,
    Left=0, Top=0, Width=W, Height=H
)

# 클릭 시 재생 설정
try:
    shape.AnimationSettings.PlaySettings.PlayOnEntry = False
    shape.AnimationSettings.PlaySettings.StopAfterSlides = 1
except Exception as e:
    print(f"재생 설정 스킵: {e}")

prs.Save()
prs.Close()
ppt.Quit()
print("done")
