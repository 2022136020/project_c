// Created: 2026-03-17
"use strict";

const canvas      = document.getElementById("drawCanvas");
const ctx         = canvas.getContext("2d");
const statusEl    = document.getElementById("status");
const resultDigit = document.getElementById("resultDigit");
const probGrid    = document.getElementById("probGrid");
const btnPredict  = document.getElementById("btnPredict");
const btnClear    = document.getElementById("btnClear");

const BRUSH_RADIUS = 12;
let isDrawing = false;

// ── 확률 바 초기 렌더링 ─────────────────────────────────────────────────

const probFills = [];
const probPcts  = [];

for (let i = 0; i < 10; i++) {
  const row = document.createElement("div");
  row.className = "prob-row";
  row.innerHTML = `
    <span class="prob-label">${i}</span>
    <div class="prob-bar-bg"><div class="prob-bar-fill" id="fill${i}"></div></div>
    <span class="prob-pct" id="pct${i}">-</span>
  `;
  probGrid.appendChild(row);
  probFills.push(document.getElementById(`fill${i}`));
  probPcts.push(document.getElementById(`pct${i}`));
}

// ── 캔버스 초기화 ───────────────────────────────────────────────────────

function clearCanvas() {
  ctx.fillStyle = "#ffffff";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  resultDigit.textContent = "?";
  probFills.forEach(f => f.style.width = "0%");
  probPcts.forEach(p => p.textContent = "-");
}
clearCanvas();

// ── 그리기 이벤트 ───────────────────────────────────────────────────────

function getPos(e) {
  const rect = canvas.getBoundingClientRect();
  const src  = e.touches ? e.touches[0] : e;
  return {
    x: (src.clientX - rect.left) * (canvas.width  / rect.width),
    y: (src.clientY - rect.top)  * (canvas.height / rect.height),
  };
}

function drawDot(x, y) {
  ctx.beginPath();
  ctx.arc(x, y, BRUSH_RADIUS, 0, Math.PI * 2);
  ctx.fillStyle = "#000000";
  ctx.fill();
}

canvas.addEventListener("mousedown",  e => { isDrawing = true;  drawDot(...Object.values(getPos(e))); });
canvas.addEventListener("mousemove",  e => { if (isDrawing) drawDot(...Object.values(getPos(e))); });
canvas.addEventListener("mouseup",    () => { isDrawing = false; });
canvas.addEventListener("mouseleave", () => { isDrawing = false; });

canvas.addEventListener("touchstart", e => { e.preventDefault(); isDrawing = true;  drawDot(...Object.values(getPos(e))); }, { passive: false });
canvas.addEventListener("touchmove",  e => { e.preventDefault(); if (isDrawing) drawDot(...Object.values(getPos(e))); }, { passive: false });
canvas.addEventListener("touchend",   () => { isDrawing = false; });

// ── 예측 요청 ───────────────────────────────────────────────────────────

async function predict() {
  const imageData = canvas.toDataURL("image/png");

  btnPredict.disabled = true;
  statusEl.textContent = "인식 중...";

  try {
    const res  = await fetch("/predict", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ image: imageData }),
    });
    const data = await res.json();

    resultDigit.textContent = data.prediction;
    data.probabilities.forEach((p, i) => {
      const pct = (p * 100).toFixed(1);
      probFills[i].style.width = pct + "%";
      probPcts[i].textContent  = pct + "%";
    });
    statusEl.textContent = "완료!";
  } catch (err) {
    statusEl.textContent = "오류: 서버에 연결할 수 없습니다.";
    console.error(err);
  } finally {
    btnPredict.disabled = false;
  }
}

btnPredict.addEventListener("click", predict);
btnClear.addEventListener("click",   clearCanvas);

// ── 서버 상태 확인 ──────────────────────────────────────────────────────

async function checkStatus() {
  try {
    const res  = await fetch("/status");
    const data = await res.json();
    statusEl.textContent = data.ready
      ? "준비 완료! 숫자를 그리고 [인식] 버튼을 누르세요."
      : "모델 학습 중... 잠시 기다려 주세요.";
    if (!data.ready) setTimeout(checkStatus, 3000);
  } catch {
    statusEl.textContent = "서버에 연결할 수 없습니다.";
  }
}
checkStatus();
