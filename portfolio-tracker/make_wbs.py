import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 한글 폰트 설정 (Windows 맑은 고딕)
font_path = r'C:\Windows\Fonts\malgun.ttf'
fm.fontManager.addfont(font_path)
matplotlib.rc('font', family='Malgun Gothic')
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

# ── 색상 ──────────────────────────────────────────────────
NAVY    = '#1A237E'
INDIGO  = '#3F51B5'
BLUE    = '#1565C0'
ORANGE  = '#EF6C00'
AMBER   = '#FFB300'
GREEN   = '#2E7D32'
DONE    = '#1976D2'
ACTIVE  = '#F57C00'
PLANNED = '#B0BEC5'
ROW_A   = '#F5F5F5'
ROW_B   = '#FFFFFF'
HDR_BG  = '#E8EAF6'
WHITE   = '#FFFFFF'

# ── WBS 데이터 ────────────────────────────────────────────
# (wbs번호, 태스크명, 담당, 작업일, 완료%, 시작주차, 기간주차)
# 주차: 10=0, 11=1, 12=2, 13=3, 14=4, 15=5
rows = [
    # cat, wbs, task, owner, dur, pct, start_wk, span
    ('cat', '1',   '인증',                          '',        5,  100, 1, 1),
    ('sub', '1.1', '회원가입 화면',                 '',        1,  100, 1, 0.5),
    ('sub', '1.2', '로그인 화면',                   '',        1,  100, 1, 0.5),
    ('sub', '1.3', 'Firebase Auth 연동',            '',        2,  100, 1, 0.8),
    ('sub', '1.4', '자동 로그인',                   '',        1,  100, 1.8, 0.4),
    ('cat', '2',   '계좌 관리',                     '',        5,  100, 2, 1),
    ('sub', '2.1', '계좌 등록 화면',                '',        1,  100, 2, 0.4),
    ('sub', '2.2', '초기 잔액·통화 선택',           '',        1,  100, 2.4, 0.4),
    ('sub', '2.3', '입금·출금 기록 화면',           '',        2,  100, 2.8, 0.6),
    ('sub', '2.4', '잔액 자동 계산 로직',           '',        1,  100, 3.4, 0.4),
    ('cat', '3',   '포지션 관리',                   '',        7,  100, 2, 1),
    ('sub', '3.1', '포지션 생성 화면',              '',        2,  100, 2.5, 0.7),
    ('sub', '3.2', '포지션 정리 화면',              '',        1,  100, 3, 0.4),
    ('sub', '3.3', '수익률·손익 자동 계산',         '',        2,  100, 3.2, 0.7),
    ('sub', '3.4', '복기 메모 작성·조회',           '',        2,  100, 3.6, 0.6),
    ('cat', '4',   '시각화',                        '',        5,  100, 3, 1),
    ('sub', '4.1', '수익률 막대 차트',              '',        2,  100, 3, 0.7),
    ('sub', '4.2', '누적 손익 라인 차트',           '',        2,  100, 3.5, 0.7),
    ('sub', '4.3', '기간별 필터',                   '',        1,  100, 4, 0.4),
    ('cat', '5',   '대시보드',                      '',        3,  100, 4, 1),
    ('sub', '5.1', '자산 현황 요약 위젯',           '',        2,  100, 4, 0.7),
    ('sub', '5.2', '최근 포지션 목록',              '',        1,  100, 4.5, 0.4),
    ('cat', '6',   '문서·배포',                     '',        6,   40, 4, 2),
    ('sub', '6.1', 'architecture.md',               '',        1,  100, 4, 0.4),
    ('sub', '6.2', 'setup·deploy·testing 문서',     '',        2,   50, 4.4, 0.8),
    ('sub', '6.3', 'README 완비',                   '',        1,   30, 5, 0.4),
    ('sub', '6.4', '앱 빌드',                       '',        2,    0, 5, 0.7),
]

N = len(rows)
WEEKS = ['10주차', '11주차', '12주차', '13주차', '14주차', '15주차']
NW = len(WEEKS)

fig_w, fig_h = 18, 0.42 * N + 2.2
fig, ax = plt.subplots(figsize=(fig_w, fig_h))
ax.set_xlim(0, fig_w)
ax.set_ylim(0, fig_h)
ax.axis('off')

# ── 제목 ─────────────────────────────────────────────────
title_h = 0.7
ax.add_patch(mpatches.FancyBboxPatch(
    (0, fig_h - title_h), fig_w, title_h,
    boxstyle='square,pad=0', fc=NAVY, ec='none'))
ax.text(0.3, fig_h - title_h/2, 'Portfolio Tracker — WBS (Work Breakdown Structure)',
        va='center', ha='left', color=WHITE,
        fontsize=15, fontweight='bold')
ax.text(fig_w - 0.3, fig_h - title_h/2, 'Jooseonghyeon · 2026',
        va='center', ha='right', color='#9FA8DA', fontsize=10)

# ── 헤더 행 ──────────────────────────────────────────────
COL_WBS  = 0.3
COL_TASK = 0.9
COL_DUR  = 6.8
COL_PCT  = 7.5
GANTT_L  = 8.4
GANTT_W  = fig_w - GANTT_L - 0.3
cell_w   = GANTT_W / NW
row_h    = 0.42

hdr_y = fig_h - title_h - row_h
ax.add_patch(mpatches.FancyBboxPatch(
    (0, hdr_y), fig_w, row_h,
    boxstyle='square,pad=0', fc=INDIGO, ec='none'))

for col, (label, x, w, ha) in enumerate([
    ('WBS',     COL_WBS,  0.55,  'center'),
    ('태스크',   COL_TASK, 5.7,   'left'),
    ('기간(일)', COL_DUR,  0.6,   'center'),
    ('완료%',   COL_PCT,  0.7,   'center'),
]):
    ax.text(x + w/2 if ha=='center' else x + 0.1,
            hdr_y + row_h/2, label,
            va='center', ha=ha, color=WHITE,
            fontsize=9, fontweight='bold')

# 주차 헤더 (두 페이즈 색)
phase_colors = [INDIGO]*3 + ['#6A1B9A']*3
for i, (wk, pc) in enumerate(zip(WEEKS, phase_colors)):
    cx = GANTT_L + i * cell_w
    ax.add_patch(mpatches.FancyBboxPatch(
        (cx, hdr_y), cell_w, row_h,
        boxstyle='square,pad=0', fc=pc, ec=WHITE, lw=0.5))
    ax.text(cx + cell_w/2, hdr_y + row_h/2, wk,
            va='center', ha='center', color=WHITE,
            fontsize=8.5, fontweight='bold')

# ── 데이터 행 ─────────────────────────────────────────────
for ri, row in enumerate(rows):
    kind, wbs, task, owner, dur, pct, sw, sp = row
    y = fig_h - title_h - row_h * (ri + 2)
    is_cat = kind == 'cat'

    bg = HDR_BG if is_cat else (ROW_A if ri % 2 == 0 else ROW_B)
    ax.add_patch(mpatches.FancyBboxPatch(
        (0, y), GANTT_L, row_h,
        boxstyle='square,pad=0', fc=bg, ec='#E0E0E0', lw=0.3))

    # WBS 번호
    ax.text(COL_WBS + 0.27, y + row_h/2, wbs,
            va='center', ha='center',
            color=NAVY if is_cat else '#424242',
            fontsize=8.5, fontweight='bold' if is_cat else 'normal')

    # 태스크명
    indent = 0 if is_cat else 0.25
    ax.text(COL_TASK + indent, y + row_h/2,
            ('▶ ' if is_cat else '· ') + task,
            va='center', ha='left',
            color=NAVY if is_cat else '#212121',
            fontsize=9 if is_cat else 8.5,
            fontweight='bold' if is_cat else 'normal')

    # 기간
    ax.text(COL_DUR + 0.3, y + row_h/2, str(dur),
            va='center', ha='center', color='#424242', fontsize=8.5)

    # 완료%
    pct_color = GREEN if pct == 100 else (ORANGE if pct > 0 else '#9E9E9E')
    ax.text(COL_PCT + 0.35, y + row_h/2, f'{pct}%',
            va='center', ha='center',
            color=pct_color, fontsize=8.5, fontweight='bold')

    # 간트 셀 배경
    for i in range(NW):
        cx = GANTT_L + i * cell_w
        cell_bg = HDR_BG if is_cat else (ROW_A if ri % 2 == 0 else ROW_B)
        ax.add_patch(mpatches.FancyBboxPatch(
            (cx, y), cell_w, row_h,
            boxstyle='square,pad=0', fc=cell_bg, ec='#E0E0E0', lw=0.3))

    # 간트 바
    if not is_cat:
        bar_x = GANTT_L + sw * cell_w
        bar_w = sp * cell_w
        bar_pad = row_h * 0.2
        bar_h = row_h - bar_pad * 2

        if pct == 100:
            bar_color = DONE
        elif pct > 0:
            bar_color = ACTIVE
        else:
            bar_color = PLANNED

        ax.add_patch(mpatches.FancyBboxPatch(
            (bar_x, y + bar_pad), bar_w, bar_h,
            boxstyle='round,pad=0.01', fc=bar_color, ec='none', alpha=0.9))

        # 진행 중이면 완료 부분 표시
        if 0 < pct < 100:
            done_w = bar_w * (pct / 100)
            ax.add_patch(mpatches.FancyBboxPatch(
                (bar_x, y + bar_pad), done_w, bar_h,
                boxstyle='round,pad=0.01', fc=DONE, ec='none', alpha=0.9))

    else:
        # 카테고리 행 전체 범위 표시 (얇은 선)
        bar_x = GANTT_L + sw * cell_w
        bar_w = sp * cell_w
        ax.add_patch(mpatches.FancyBboxPatch(
            (bar_x, y + row_h*0.42), bar_w, row_h*0.16,
            boxstyle='square,pad=0', fc=NAVY, ec='none', alpha=0.7))

# ── 범례 ─────────────────────────────────────────────────
legend_y = 0.08
patches = [
    mpatches.Patch(fc=DONE,    label='완료 (100%)'),
    mpatches.Patch(fc=ACTIVE,  label='진행 중'),
    mpatches.Patch(fc=PLANNED, label='예정'),
]
ax.legend(handles=patches, loc='lower right',
          bbox_to_anchor=(0.99, 0.01),
          fontsize=9, framealpha=0.9,
          ncol=3, handlelength=1.5)

# ── 하단 선 ──────────────────────────────────────────────
ax.axhline(y=0.3, color='#BDBDBD', lw=0.5)

plt.tight_layout(pad=0)
out = r'C:\project_c\portfolio-tracker\presentation\wbs.png'
plt.savefig(out, dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print(f'저장 완료: {out}')
