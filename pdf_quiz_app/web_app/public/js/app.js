'use strict';

/* ============================================================
   상태
   ============================================================ */
const state = {
  questions:     [],
  queue:         [],
  currentIndex:  0,
  selectedValue: null,
  results:       [],
  roundCount:    0,
  files:         [],
};

/* ============================================================
   DOM
   ============================================================ */
const $ = (id) => document.getElementById(id);

const dom = {
  uploadScreen:         $('upload-screen'),
  quizScreen:           $('quiz-screen'),
  resultScreen:         $('result-screen'),

  dropZone:             $('drop-zone'),
  fileInput:            $('file-input'),
  uploadBtn:            $('upload-btn'),
  fileNameDisplay:      $('file-name-display'),
  loadingOverlay:       $('loading-overlay'),
  errorBanner:          $('error-banner'),
  errorText:            $('error-text'),
  errorClose:           $('error-close'),
  themeToggle:          $('theme-toggle'),

  backToUpload:         $('back-to-upload'),
  questionCounter:      $('question-counter'),
  progressFill:         $('progress-fill'),
  progressContainer:    $('progress-bar-container'),
  questionBadge:        $('question-badge'),
  questionSource:       $('question-source'),
  questionText:         $('question-text'),
  choicesContainer:     $('choices-container'),
  choicesList:          $('choices-list'),
  shortAnswerContainer: $('short-answer-container'),
  shortAnswerInput:     $('short-answer-input'),
  tfContainer:          $('tf-container'),
  checkBtn:             $('check-btn'),
  feedbackArea:         $('feedback-area'),
  feedbackCard:         $('feedback-card'),
  feedbackIcon:         $('feedback-icon'),
  feedbackLabel:        $('feedback-label'),
  feedbackAnswer:       $('feedback-answer'),
  feedbackExplanation:  $('feedback-explanation'),
  nextBtn:              $('next-btn'),

  scoreNumber:    $('score-number'),
  scoreTotal:     $('score-total'),
  scoreRingFill:  $('score-ring-fill'),
  gradeMessage:   $('grade-message'),
  gradePercent:   $('grade-percent'),
  summaryList:    $('summary-list'),
  retryBtn:       $('retry-btn'),
  newUploadBtn:   $('new-upload-btn'),
};

/* ============================================================
   화면 전환
   ============================================================ */
function showScreen(targetId) {
  [dom.uploadScreen, dom.quizScreen, dom.resultScreen].forEach((s) => {
    if (s.id === targetId) {
      s.classList.remove('slide-out');
      s.classList.add('active');
    } else if (s.classList.contains('active')) {
      s.classList.add('slide-out');
      setTimeout(() => s.classList.remove('active', 'slide-out'), 300);
    }
  });
}

/* ============================================================
   테마
   ============================================================ */
(function initTheme() {
  const saved = localStorage.getItem('quiz-theme');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  if (saved === 'dark' || (!saved && prefersDark)) {
    document.documentElement.setAttribute('data-theme', 'dark');
  }
})();

dom.themeToggle.addEventListener('click', () => {
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  document.documentElement.setAttribute('data-theme', isDark ? 'light' : 'dark');
  localStorage.setItem('quiz-theme', isDark ? 'light' : 'dark');
  if (isDark) document.documentElement.removeAttribute('data-theme');
});

/* ============================================================
   에러 배너
   ============================================================ */
function showError(msg) {
  dom.errorText.textContent = msg;
  dom.errorBanner.hidden = false;
}

function hideError() {
  dom.errorBanner.hidden = true;
  dom.errorText.textContent = '';
}

dom.errorClose.addEventListener('click', hideError);

/* ============================================================
   파일 선택 / 드래그 앤 드롭
   ============================================================ */
function handleFiles(fileList) {
  const MAX_SIZE  = 50 * 1024 * 1024;
  const MAX_COUNT = 10;
  const files = Array.from(fileList);

  if (files.length === 0) return;

  if (files.some((f) => f.type !== 'application/pdf')) {
    showError('PDF 파일만 업로드할 수 있습니다.');
    return;
  }
  if (files.length > MAX_COUNT) {
    showError(`최대 ${MAX_COUNT}개 파일까지 선택 가능합니다.`);
    return;
  }
  const oversized = files.filter((f) => f.size > MAX_SIZE);
  if (oversized.length > 0) {
    showError(`파일 크기가 50MB를 초과합니다: ${oversized.map((f) => f.name).join(', ')}`);
    return;
  }

  hideError();
  state.files = files;

  if (files.length === 1) {
    dom.fileNameDisplay.textContent = `${files[0].name} (${(files[0].size / 1024 / 1024).toFixed(1)} MB)`;
  } else {
    const total = (files.reduce((s, f) => s + f.size, 0) / 1024 / 1024).toFixed(1);
    dom.fileNameDisplay.textContent = `${files.length}개 파일 선택됨 (총 ${total} MB)`;
  }
  dom.fileNameDisplay.classList.add('has-file');
  dom.dropZone.classList.add('has-file');
  dom.uploadBtn.disabled = false;
}

dom.fileInput.addEventListener('change', () => handleFiles(dom.fileInput.files));

dom.dropZone.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); dom.fileInput.click(); }
});
dom.dropZone.addEventListener('click', (e) => {
  if (e.target.tagName !== 'LABEL' && e.target.tagName !== 'INPUT') dom.fileInput.click();
});

['dragenter', 'dragover'].forEach((evt) => {
  dom.dropZone.addEventListener(evt, (e) => {
    e.preventDefault(); e.stopPropagation();
    dom.dropZone.classList.add('drag-over');
  });
});
['dragleave', 'dragend'].forEach((evt) => {
  dom.dropZone.addEventListener(evt, (e) => {
    e.preventDefault();
    dom.dropZone.classList.remove('drag-over');
  });
});
dom.dropZone.addEventListener('drop', (e) => {
  e.preventDefault(); e.stopPropagation();
  dom.dropZone.classList.remove('drag-over');
  if (e.dataTransfer.files.length > 0) handleFiles(e.dataTransfer.files);
});

document.addEventListener('dragover', (e) => e.preventDefault());
document.addEventListener('drop', (e) => e.preventDefault());

/* ============================================================
   업로드 및 문제 추출
   ============================================================ */
dom.uploadBtn.addEventListener('click', uploadAndExtract);

async function uploadAndExtract() {
  if (!state.files || state.files.length === 0) return;

  hideError();
  dom.loadingOverlay.hidden = false;
  dom.uploadBtn.disabled = true;

  try {
    const formData = new FormData();
    state.files.forEach((file) => formData.append('pdfs', file));

    const res = await fetch('/api/upload', { method: 'POST', body: formData });

    let data;
    try { data = await res.json(); } catch (_) { data = {}; }

    if (!res.ok) {
      throw new Error(data.error || `서버 오류 (${res.status})`);
    }
    if (!Array.isArray(data.questions) || data.questions.length === 0) {
      throw new Error('문제를 추출하지 못했습니다. 다른 PDF를 시도해 보세요.');
    }

    state.questions = data.questions;
    state.roundCount = 0;
    buildQueue();
    dom.loadingOverlay.hidden = true;
    startQuiz();

  } catch (err) {
    dom.loadingOverlay.hidden = true;
    dom.uploadBtn.disabled = false;
    showError(err.message || '알 수 없는 오류가 발생했습니다.');
  }
}

/* ============================================================
   큐 생성
   ============================================================ */
function buildQueue() {
  state.queue = [...state.questions].sort(() => Math.random() - 0.5);
  state.currentIndex = 0;
  state.results = [];
  state.roundCount++;
}

/* ============================================================
   퀴즈 시작 / 렌더링
   ============================================================ */
function startQuiz() {
  showScreen('quiz-screen');
  renderQuestion();
}

function renderQuestion() {
  const q     = state.queue[state.currentIndex];
  const total = state.queue.length;
  const idx   = state.currentIndex;

  state.selectedValue = null;

  dom.questionCounter.textContent = `문제 ${idx + 1} / ${total}  (${state.roundCount}회차)`;

  const pct = Math.round((idx / total) * 100);
  dom.progressFill.style.width = `${pct}%`;
  dom.progressContainer.setAttribute('aria-valuenow', pct);

  dom.questionBadge.textContent = `Q${idx + 1}`;
  dom.questionText.textContent  = q.question;
  dom.questionSource.textContent = q.source || '';

  dom.feedbackArea.hidden = true;
  dom.checkBtn.disabled   = true;
  dom.checkBtn.hidden     = false;

  hideAllInputs();

  if (q.type === 'multiple_choice') renderChoices(q);
  else if (q.type === 'true_false') renderTrueFalse();
  else renderShortAnswer();

  const card = $('question-card');
  card.style.animation = 'none';
  requestAnimationFrame(() => {
    card.style.animation = '';
  });
}

function hideAllInputs() {
  dom.choicesContainer.hidden     = true;
  dom.shortAnswerContainer.hidden = true;
  dom.tfContainer.hidden          = true;
}

/* ── 객관식 ── */
const CIRCLE_NUMS = ['①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧'];

function renderChoices(q) {
  dom.choicesContainer.hidden = false;
  dom.choicesList.innerHTML   = '';

  (q.choices || []).forEach((choice, i) => {
    const li  = document.createElement('li');
    const btn = document.createElement('button');
    btn.className    = 'choice-btn';
    btn.dataset.value = String(i + 1);

    const numSpan  = document.createElement('span');
    numSpan.className   = 'choice-num';
    numSpan.textContent = CIRCLE_NUMS[i] || String(i + 1);
    numSpan.setAttribute('aria-hidden', 'true');

    const textSpan = document.createElement('span');
    textSpan.textContent = choice;

    btn.append(numSpan, textSpan);
    btn.setAttribute('aria-label', `${i + 1}번 선택지: ${choice}`);
    btn.addEventListener('click', () => selectChoice(btn, String(i + 1)));
    li.appendChild(btn);
    dom.choicesList.appendChild(li);
  });
}

function selectChoice(clickedBtn, value) {
  if (!dom.feedbackArea.hidden) return;
  dom.choicesList.querySelectorAll('.choice-btn').forEach((b) => b.classList.remove('selected'));
  clickedBtn.classList.add('selected');
  state.selectedValue = value;
  dom.checkBtn.disabled = false;
}

/* ── 주관식 ── */
function renderShortAnswer() {
  dom.shortAnswerContainer.hidden = false;
  dom.shortAnswerInput.value      = '';
  dom.shortAnswerInput.disabled   = false;
  dom.shortAnswerInput.focus();

  dom.shortAnswerInput.addEventListener('input', onShortAnswerInput);
  dom.shortAnswerInput.addEventListener('keydown', onShortAnswerKeydown);
}

function onShortAnswerInput() {
  const val = dom.shortAnswerInput.value.trim();
  state.selectedValue   = val;
  dom.checkBtn.disabled = val.length === 0;
}

function onShortAnswerKeydown(e) {
  if (e.key === 'Enter' && !dom.checkBtn.disabled) checkAnswer();
}

/* ── 참/거짓 ── */
function renderTrueFalse() {
  dom.tfContainer.hidden = false;
  dom.tfContainer.querySelectorAll('.tf-btn').forEach((btn) => {
    const clone = btn.cloneNode(true);
    btn.replaceWith(clone);
    clone.addEventListener('click', () => selectTF(clone, clone.dataset.value));
  });
}

function selectTF(clickedBtn, value) {
  if (!dom.feedbackArea.hidden) return;
  dom.tfContainer.querySelectorAll('.tf-btn').forEach((b) => b.classList.remove('selected'));
  clickedBtn.classList.add('selected');
  state.selectedValue   = value;
  dom.checkBtn.disabled = false;
}

/* ============================================================
   정답 확인
   ============================================================ */
dom.checkBtn.addEventListener('click', checkAnswer);

function checkAnswer() {
  const q = state.queue[state.currentIndex];
  if (state.selectedValue === null || state.selectedValue === undefined) return;

  const isCorrect = compareAnswers(String(state.selectedValue), String(q.answer), q.type);

  state.results.push({
    correct: isCorrect,
    userAnswer: state.selectedValue,
    question: q.question,
    correctAnswer: q.answer,
  });

  renderFeedback(isCorrect, q, state.selectedValue);
  disableInputs(isCorrect, q, state.selectedValue);
  dom.checkBtn.hidden = true;
}

function compareAnswers(userAns, correctAns, type) {
  const norm = (s) => String(s).trim().toLowerCase();

  if (type === 'true_false') {
    const tfMap = { o: 'true', x: 'false', '참': 'true', '거짓': 'false' };
    const map   = (v) => tfMap[norm(v)] ?? norm(v);
    return map(userAns) === map(correctAns);
  }

  return norm(userAns) === norm(correctAns);
}

function renderFeedback(isCorrect, q, userAnswer) {
  const noAnswer = !q.answer || q.answer.trim() === '';
  dom.feedbackCard.className    = `feedback-card ${isCorrect ? 'correct-feedback' : 'wrong-feedback'}`;
  dom.feedbackIcon.textContent  = noAnswer ? '❓' : (isCorrect ? '✅' : '❌');
  dom.feedbackLabel.textContent = noAnswer ? '정답 미등록' : (isCorrect ? '정답입니다!' : '오답입니다');

  if (!isCorrect && !noAnswer) {
    dom.feedbackAnswer.textContent = `정답: ${formatAnswer(q.answer, q)}`;
    dom.feedbackAnswer.hidden = false;
  } else {
    dom.feedbackAnswer.hidden = true;
  }

  if (q.explanation) {
    dom.feedbackExplanation.textContent = q.explanation;
    dom.feedbackExplanation.hidden = false;
  } else {
    dom.feedbackExplanation.hidden = true;
  }

  dom.feedbackArea.hidden = false;

  const isLast = state.currentIndex === state.queue.length - 1;
  dom.nextBtn.innerHTML = isLast
    ? `결과 보기 <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>`
    : `다음 문제 <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>`;

  dom.feedbackArea.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function formatAnswer(answer, q) {
  if (q.type === 'true_false') {
    const lower = String(answer).toLowerCase();
    if (lower === 'true')  return 'O (참)';
    if (lower === 'false') return 'X (거짓)';
    return answer;
  }
  if (q.type === 'multiple_choice' && q.choices) {
    const idx = parseInt(answer, 10) - 1;
    if (!isNaN(idx) && q.choices[idx]) {
      return `${CIRCLE_NUMS[idx] || answer} ${q.choices[idx]}`;
    }
  }
  return answer;
}

function disableInputs(isCorrect, q, userAnswer) {
  if (q.type === 'multiple_choice') {
    dom.choicesList.querySelectorAll('.choice-btn').forEach((btn) => {
      btn.disabled = true;
      if (btn.dataset.value === userAnswer) btn.classList.add(isCorrect ? 'correct' : 'wrong');
      if (!isCorrect && btn.dataset.value === String(q.answer)) btn.classList.add('correct');
    });
  } else if (q.type === 'short_answer') {
    dom.shortAnswerInput.disabled = true;
    dom.shortAnswerInput.removeEventListener('input', onShortAnswerInput);
    dom.shortAnswerInput.removeEventListener('keydown', onShortAnswerKeydown);
  } else if (q.type === 'true_false') {
    const correctVal = String(q.answer).toLowerCase() === 'true' ? 'true' : 'false';
    dom.tfContainer.querySelectorAll('.tf-btn').forEach((btn) => {
      btn.disabled = true;
      if (btn.dataset.value === userAnswer) btn.classList.add(isCorrect ? 'correct' : 'wrong');
      if (!isCorrect && btn.dataset.value === correctVal) btn.classList.add('correct');
    });
  }
}

/* ============================================================
   다음 문제 / 결과
   ============================================================ */
dom.nextBtn.addEventListener('click', () => {
  if (state.currentIndex === state.queue.length - 1) {
    showResults();
  } else {
    state.currentIndex++;
    renderQuestion();
    dom.quizScreen.scrollTo({ top: 0, behavior: 'smooth' });
  }
});

dom.backToUpload.addEventListener('click', () => {
  if (confirm('퀴즈를 중단하고 처음으로 돌아가시겠습니까?')) {
    resetUpload();
    showScreen('upload-screen');
  }
});

/* ============================================================
   결과 화면
   ============================================================ */
function showResults() {
  const total   = state.queue.length;
  const correct = state.results.filter((r) => r.correct).length;
  const pct     = total > 0 ? Math.round((correct / total) * 100) : 0;

  dom.progressFill.style.width = '100%';
  dom.progressContainer.setAttribute('aria-valuenow', 100);

  showScreen('result-screen');

  animateNumber(dom.scoreNumber, 0, correct, 800);
  dom.scoreTotal.textContent = total;

  const circumference = 2 * Math.PI * 52;
  const offset = circumference * (1 - pct / 100);
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      dom.scoreRingFill.style.strokeDasharray  = `${circumference}`;
      dom.scoreRingFill.style.strokeDashoffset = `${offset}`;
      dom.scoreRingFill.style.stroke = pct >= 70 ? 'var(--color-success)'
        : pct >= 50 ? 'var(--color-primary)' : 'var(--color-error)';
    });
  });

  const msg = pct >= 90 ? '완벽합니다! 🎉'
    : pct >= 70 ? '잘 하셨습니다! 👍'
    : pct >= 50 ? '조금 더 노력해보세요 💪'
    : '다시 한번 도전해보세요 📚';

  dom.gradeMessage.textContent = msg;
  dom.gradePercent.textContent = `정답률 ${pct}%`;
  dom.scoreNumber.style.color  = pct >= 70 ? 'var(--color-success)'
    : pct >= 50 ? 'var(--color-primary)' : 'var(--color-error)';

  renderSummary();
}

function animateNumber(el, from, to, duration) {
  const start  = performance.now();
  const update = (now) => {
    const progress = Math.min((now - start) / duration, 1);
    const eased    = 1 - Math.pow(1 - progress, 4);
    el.textContent = Math.round(from + (to - from) * eased);
    if (progress < 1) requestAnimationFrame(update);
    else el.textContent = to;
  };
  requestAnimationFrame(update);
}

function renderSummary() {
  dom.summaryList.innerHTML = '';
  state.results.forEach((r, i) => {
    const li = document.createElement('li');
    li.className = `summary-item ${r.correct ? 'correct-item' : 'wrong-item'}`;

    const numSpan = document.createElement('span');
    numSpan.className   = 'summary-num';
    numSpan.textContent = `Q${i + 1}`;

    const qSpan = document.createElement('span');
    qSpan.className   = 'summary-q';
    qSpan.textContent = r.question;
    qSpan.title       = r.question;

    const badge = document.createElement('span');
    badge.className = 'summary-badge';
    badge.setAttribute('aria-label', r.correct ? '정답' : '오답');
    badge.textContent = r.correct ? '✅' : '❌';

    li.append(numSpan, qSpan, badge);
    dom.summaryList.appendChild(li);
  });
}

/* ============================================================
   결과 화면 버튼
   ============================================================ */
dom.retryBtn.addEventListener('click', () => {
  buildQueue();
  dom.progressFill.style.width = '0%';
  showScreen('quiz-screen');
  renderQuestion();
});

dom.newUploadBtn.addEventListener('click', () => {
  resetAll();
  showScreen('upload-screen');
});

/* ============================================================
   리셋
   ============================================================ */
function resetUpload() {
  state.files = [];
  dom.fileInput.value = '';
  dom.fileNameDisplay.textContent = 'PDF 최대 10개 선택 가능 (각 50MB 이하)';
  dom.fileNameDisplay.classList.remove('has-file');
  dom.dropZone.classList.remove('has-file', 'drag-over');
  dom.uploadBtn.disabled = true;
  hideError();
}

function resetAll() {
  resetUpload();
  state.questions    = [];
  state.currentIndex = 0;
  state.results      = [];
  state.selectedValue = null;
  dom.scoreRingFill.style.strokeDashoffset = '327';
  dom.scoreRingFill.style.stroke = '';
  dom.progressFill.style.width   = '0%';
}
