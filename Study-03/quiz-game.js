const SCORE_MAP = { '쉬움': 10, '보통': 15, '어려움': 20 };
const CATEGORIES = ['한국사', '과학', '지리', '일반상식'];

const state = {
  nickname: '',
  mode: 'all',
  questions: [],
  currentIndex: 0,
  score: 0,
  maxScore: 0,
  answers: [],
  currentChoices: [],
  currentAnswerIndex: -1,
};

function $(id) { return document.getElementById(id); }

function shuffleArray(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function calcGrade(ratio) {
  if (ratio >= 0.9) return 'S';
  if (ratio >= 0.7) return 'A';
  if (ratio >= 0.5) return 'B';
  if (ratio >= 0.3) return 'C';
  return 'D';
}

function showScreen(id) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  $(id).classList.add('active');
}

function buildQuestionSet(mode) {
  if (mode === 'all') {
    return CATEGORIES.flatMap(cat =>
      shuffleArray(QUIZ_DATA.filter(q => q.category === cat))
    );
  }
  return shuffleArray(QUIZ_DATA.filter(q => q.category === mode));
}

function prepareChoices(question) {
  const indices = shuffleArray([0, 1, 2, 3]);
  return {
    choices: indices.map(i => question.choices[i]),
    answerIndex: indices.indexOf(question.answer),
  };
}

function renderQuestion() {
  const q = state.questions[state.currentIndex];
  const total = state.questions.length;
  const { choices, answerIndex } = prepareChoices(q);
  state.currentChoices = choices;
  state.currentAnswerIndex = answerIndex;

  $('category-label').textContent = q.category;
  $('difficulty-label').textContent = q.difficulty;
  $('difficulty-label').className = `difficulty-badge diff-${q.difficulty}`;
  $('progress-text').textContent = `${state.currentIndex + 1} / ${total}`;
  $('progress-bar').style.width = `${(state.currentIndex / total) * 100}%`;
  $('score-display').textContent = `${state.score}점`;
  $('question-text').textContent = q.question;

  const choicesEl = $('choices-container');
  choicesEl.innerHTML = '';
  const labels = ['①', '②', '③', '④'];
  choices.forEach((choice, i) => {
    const btn = document.createElement('button');
    btn.className = 'choice-btn';
    btn.innerHTML = `<span class="choice-label">${labels[i]}</span><span>${choice}</span>`;
    btn.addEventListener('click', () => onChoiceClick(i));
    choicesEl.appendChild(btn);
  });

  $('feedback-area').className = 'feedback-area hidden';
  $('next-btn').classList.add('hidden');
}

function onChoiceClick(selectedIndex) {
  const q = state.questions[state.currentIndex];
  const isCorrect = selectedIndex === state.currentAnswerIndex;
  const earned = isCorrect ? SCORE_MAP[q.difficulty] : 0;
  if (isCorrect) state.score += earned;

  state.answers.push({ category: q.category, difficulty: q.difficulty, correct: isCorrect, earned });

  document.querySelectorAll('.choice-btn').forEach((btn, i) => {
    btn.disabled = true;
    if (i === state.currentAnswerIndex) btn.classList.add('correct');
    else if (i === selectedIndex) btn.classList.add('wrong');
  });

  const fb = $('feedback-area');
  fb.className = `feedback-area ${isCorrect ? 'feedback-correct' : 'feedback-wrong'}`;
  $('feedback-icon').textContent = isCorrect ? '✓' : '✗';
  $('feedback-title').textContent = isCorrect ? '정답입니다!' : '오답입니다.';
  $('feedback-score').textContent = isCorrect ? `+${earned}점` : '+0점';
  $('feedback-explanation').textContent = q.explanation;
  $('score-display').textContent = `${state.score}점`;
  $('next-btn').classList.remove('hidden');
}

function onNextClick() {
  state.currentIndex++;
  if (state.currentIndex >= state.questions.length) {
    showResult();
  } else {
    renderQuestion();
  }
}

function showResult() {
  const ratio = state.maxScore > 0 ? state.score / state.maxScore : 0;
  const grade = calcGrade(ratio);
  const correctCount = state.answers.filter(a => a.correct).length;
  const total = state.questions.length;

  $('result-nickname').textContent = state.nickname;
  $('result-score').textContent = state.score;
  $('result-max-score').textContent = state.maxScore;
  $('result-correct').textContent = `${correctCount} / ${total}`;

  const gradeEl = $('result-grade');
  gradeEl.textContent = grade;
  gradeEl.className = `grade-badge grade-${grade}`;

  // Category breakdown
  const breakdown = $('category-breakdown');
  breakdown.innerHTML = '';
  CATEGORIES.forEach(cat => {
    const catAnswers = state.answers.filter(a => a.category === cat);
    if (catAnswers.length === 0) return;
    const correct = catAnswers.filter(a => a.correct).length;
    const catTotal = catAnswers.length;
    const pct = Math.round((correct / catTotal) * 100);
    breakdown.innerHTML += `
      <div class="breakdown-row">
        <span class="breakdown-cat">${cat}</span>
        <div class="breakdown-bar-wrap">
          <div class="breakdown-bar" style="width:${pct}%"></div>
        </div>
        <span class="breakdown-ratio">${correct}/${catTotal} (${pct}%)</span>
      </div>`;
  });

  saveRecord(grade);
  renderLeaderboard();
  showScreen('result-screen');
}

function saveRecord(grade) {
  const records = JSON.parse(localStorage.getItem('quiz_records') || '[]');
  records.push({
    nickname: state.nickname,
    score: state.score,
    maxScore: state.maxScore,
    grade,
    mode: state.mode === 'all' ? '전체' : state.mode,
    date: new Date().toLocaleString('ko-KR'),
    ts: Date.now(),
  });
  records.sort((a, b) => b.score - a.score || a.ts - b.ts);
  localStorage.setItem('quiz_records', JSON.stringify(records.slice(0, 50)));
}

function renderLeaderboard() {
  const records = JSON.parse(localStorage.getItem('quiz_records') || '[]');
  const tbody = $('leaderboard-body');
  tbody.innerHTML = '';
  if (records.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:var(--muted)">기록 없음</td></tr>';
    return;
  }
  records.slice(0, 10).forEach((r, i) => {
    const tr = document.createElement('tr');
    if (r.nickname === state.nickname && r.ts === records[i]?.ts) tr.classList.add('my-record');
    tr.innerHTML = `
      <td>${i + 1}</td>
      <td>${r.nickname}</td>
      <td><strong>${r.score}</strong> / ${r.maxScore}</td>
      <td><span class="grade-badge grade-${r.grade}">${r.grade}</span></td>
      <td>${r.mode}</td>
      <td>${r.date}</td>`;
    tbody.appendChild(tr);
  });
}

function startGame() {
  const nickname = $('nickname').value.trim();
  if (!nickname) {
    $('nickname').focus();
    $('nickname').classList.add('error');
    return;
  }
  $('nickname').classList.remove('error');

  if (state.mode !== 'all' && !CATEGORIES.includes(state.mode)) {
    alert('카테고리를 선택해 주세요.');
    return;
  }

  state.nickname = nickname;
  state.questions = buildQuestionSet(state.mode);
  state.currentIndex = 0;
  state.score = 0;
  state.answers = [];
  state.maxScore = state.questions.reduce((s, q) => s + SCORE_MAP[q.difficulty], 0);

  renderQuestion();
  showScreen('question-screen');
}

function resetGame() {
  state.mode = 'all';
  $('mode-all').classList.add('active');
  $('mode-category').classList.remove('active');
  $('category-select').classList.add('hidden');
  document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
  showScreen('start-screen');
}

document.addEventListener('DOMContentLoaded', () => {
  $('mode-all').addEventListener('click', () => {
    state.mode = 'all';
    $('mode-all').classList.add('active');
    $('mode-category').classList.remove('active');
    $('category-select').classList.add('hidden');
  });

  $('mode-category').addEventListener('click', () => {
    $('mode-category').classList.add('active');
    $('mode-all').classList.remove('active');
    $('category-select').classList.remove('hidden');
    state.mode = '';
  });

  document.querySelectorAll('.cat-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.mode = btn.dataset.category;
    });
  });

  $('start-btn').addEventListener('click', startGame);
  $('next-btn').addEventListener('click', onNextClick);
  $('restart-btn').addEventListener('click', resetGame);
  $('nickname').addEventListener('keydown', e => { if (e.key === 'Enter') startGame(); });

  $('mode-all').classList.add('active');
});
