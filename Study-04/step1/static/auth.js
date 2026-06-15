/* ===== auth.js — 모든 페이지 공유 인증 모듈 ===== */
const Auth = (() => {
  const TOKEN_KEY = 'auth_token';
  const USER_KEY  = 'auth_user';

  const getToken    = () => localStorage.getItem(TOKEN_KEY);
  const getUser     = () => { try { return JSON.parse(localStorage.getItem(USER_KEY) || 'null'); } catch { return null; } };
  const isLoggedIn  = () => !!getToken();

  const setSession  = (token, user) => {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  };
  const clearSession = () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  };

  /* JWT Authorization 헤더 포함 fetch */
  const apiFetch = async (url, opts = {}) => {
    const token = getToken();
    opts.headers = { ...(opts.headers || {}), 'Content-Type': 'application/json' };
    if (token) opts.headers['Authorization'] = `Bearer ${token}`;
    const res = await fetch(url, opts);
    if (res.status === 401) { clearSession(); updateNav(); }
    return res;
  };

  /* ── 네비게이션 DOM 주입 ── */
  const updateNav = () => {
    const nav = document.getElementById('auth-nav');
    if (!nav) return;
    const user = getUser();
    if (user) {
      nav.innerHTML = `
        <div class="auth-user-area">
          <span class="auth-nickname">👤 ${user.nickname}</span>
          <div class="auth-dropdown">
            <a href="/profile">내 레시피 모음</a>
            <a href="/profile">프로필 설정</a>
            <a href="#" id="logout-link">로그아웃</a>
          </div>
        </div>`;
      document.getElementById('logout-link').addEventListener('click', e => {
        e.preventDefault(); doLogout();
      });
    } else {
      nav.innerHTML = `
        <button class="auth-btn" onclick="Auth.showModal('login')">로그인</button>
        <button class="auth-btn primary" onclick="Auth.showModal('signup')">회원가입</button>`;
    }
  };

  /* ── 모달 ── */
  const injectModal = () => {
    if (document.getElementById('auth-modal')) return;
    const el = document.createElement('div');
    el.id = 'auth-modal';
    el.innerHTML = `
      <div class="auth-overlay" onclick="Auth.hideModal()"></div>
      <div class="auth-box">
        <button class="auth-close" onclick="Auth.hideModal()">✕</button>
        <div id="auth-modal-login">
          <h2>로그인</h2>
          <div class="auth-err" id="login-err"></div>
          <input class="auth-input" type="email" id="login-email" placeholder="이메일">
          <input class="auth-input" type="password" id="login-pw" placeholder="비밀번호">
          <button class="auth-submit" onclick="Auth._doLogin()">로그인</button>
          <p class="auth-switch">계정이 없으신가요? <a href="#" onclick="Auth.showModal('signup');return false">회원가입</a></p>
        </div>
        <div id="auth-modal-signup" style="display:none">
          <h2>회원가입</h2>
          <div class="auth-err" id="signup-err"></div>
          <input class="auth-input" type="text"     id="signup-nick"  placeholder="닉네임">
          <input class="auth-input" type="email"    id="signup-email" placeholder="이메일">
          <input class="auth-input" type="password" id="signup-pw"    placeholder="비밀번호 (8자+영문+숫자)">
          <button class="auth-submit" onclick="Auth._doSignup()">가입하기</button>
          <p class="auth-switch">이미 계정이 있으신가요? <a href="#" onclick="Auth.showModal('login');return false">로그인</a></p>
        </div>
      </div>`;
    document.body.appendChild(el);

    /* Enter 키 제출 */
    ['login-email','login-pw'].forEach(id => {
      document.getElementById(id).addEventListener('keydown', e => {
        if (e.key === 'Enter') Auth._doLogin();
      });
    });
    ['signup-nick','signup-email','signup-pw'].forEach(id => {
      document.getElementById(id).addEventListener('keydown', e => {
        if (e.key === 'Enter') Auth._doSignup();
      });
    });
  };

  const showModal = (mode = 'login') => {
    injectModal();
    document.getElementById('auth-modal').style.display = 'flex';
    document.getElementById('auth-modal-login').style.display  = mode === 'login'  ? '' : 'none';
    document.getElementById('auth-modal-signup').style.display = mode === 'signup' ? '' : 'none';
    document.getElementById('login-err').textContent  = '';
    document.getElementById('signup-err').textContent = '';
  };

  const hideModal = () => {
    const m = document.getElementById('auth-modal');
    if (m) m.style.display = 'none';
  };

  /* ── 인증 API ── */
  let _pendingAction = null;

  const _doLogin = async () => {
    const email = document.getElementById('login-email').value.trim();
    const pw    = document.getElementById('login-pw').value;
    const errEl = document.getElementById('login-err');
    errEl.textContent = '';
    try {
      const res  = await fetch('/api/auth/login', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({email, password: pw}),
      });
      const data = await res.json();
      if (!res.ok) { errEl.textContent = data.error || '로그인 실패'; return; }
      setSession(data.token, {email: data.email, nickname: data.nickname});
      hideModal();
      updateNav();
      if (_pendingAction) { _pendingAction(); _pendingAction = null; }
    } catch { errEl.textContent = '네트워크 오류'; }
  };

  const _doSignup = async () => {
    const nick  = document.getElementById('signup-nick').value.trim();
    const email = document.getElementById('signup-email').value.trim();
    const pw    = document.getElementById('signup-pw').value;
    const errEl = document.getElementById('signup-err');
    errEl.textContent = '';
    try {
      const res  = await fetch('/api/auth/signup', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({nickname: nick, email, password: pw}),
      });
      const data = await res.json();
      if (!res.ok) { errEl.textContent = data.error || '가입 실패'; return; }
      setSession(data.token, {email: data.email, nickname: data.nickname});
      hideModal();
      updateNav();
      if (_pendingAction) { _pendingAction(); _pendingAction = null; }
    } catch { errEl.textContent = '네트워크 오류'; }
  };

  const doLogout = async () => {
    await fetch('/api/auth/logout', {method:'POST'});
    clearSession();
    updateNav();
  };

  /* 로그인 필요 액션: 미로그인이면 모달 보여주고 로그인 후 재실행 */
  const requireAuth = (action) => {
    if (isLoggedIn()) { action(); }
    else { _pendingAction = action; showModal('login'); }
  };

  /* 초기화 */
  const init = () => {
    injectCSS();
    updateNav();
  };

  /* 동적 CSS */
  const injectCSS = () => {
    if (document.getElementById('auth-css')) return;
    const s = document.createElement('style');
    s.id = 'auth-css';
    s.textContent = `
      #auth-nav { display:flex; align-items:center; gap:8px; margin-left:auto; }
      .auth-btn {
        padding:7px 16px; border-radius:7px; border:1.5px solid #dfe6e9;
        background:#fff; font-size:.85rem; font-weight:600; cursor:pointer;
        transition:background .15s;
      }
      .auth-btn.primary { background:#2ecc71; color:#fff; border-color:#2ecc71; }
      .auth-btn.primary:hover { background:#27ae60; }
      .auth-btn:hover { background:#f5f6fa; }

      .auth-user-area { position:relative; }
      .auth-nickname {
        padding:7px 14px; border-radius:7px; background:#f5f6fa;
        font-size:.85rem; font-weight:600; cursor:pointer;
        display:inline-block;
      }
      .auth-nickname:hover + .auth-dropdown,
      .auth-dropdown:hover { display:block !important; }
      .auth-dropdown {
        display:none; position:absolute; right:0; top:110%;
        background:#fff; border:1.5px solid #dfe6e9;
        border-radius:8px; box-shadow:0 4px 20px rgba(0,0,0,.1);
        min-width:150px; z-index:999;
        padding:6px 0;
      }
      .auth-dropdown a {
        display:block; padding:9px 16px;
        font-size:.88rem; color:#2d3436; text-decoration:none;
      }
      .auth-dropdown a:hover { background:#f5f6fa; }

      #auth-modal {
        display:none; position:fixed; inset:0; z-index:1000;
        align-items:center; justify-content:center;
      }
      .auth-overlay { position:absolute; inset:0; background:rgba(0,0,0,.45); }
      .auth-box {
        position:relative; background:#fff; border-radius:14px;
        padding:36px 32px; width:380px; max-width:95vw;
        box-shadow:0 8px 40px rgba(0,0,0,.18);
      }
      .auth-close {
        position:absolute; top:14px; right:16px;
        background:none; border:none; font-size:1.2rem;
        cursor:pointer; color:#636e72;
      }
      .auth-box h2 { font-size:1.15rem; font-weight:700; margin-bottom:18px; }
      .auth-err { color:#e74c3c; font-size:.84rem; margin-bottom:10px; min-height:18px; }
      .auth-input {
        display:block; width:100%; padding:10px 12px;
        border:1.5px solid #dfe6e9; border-radius:8px;
        font-size:.92rem; margin-bottom:12px;
      }
      .auth-input:focus { outline:none; border-color:#2ecc71; }
      .auth-submit {
        width:100%; padding:11px; background:#2ecc71; color:#fff;
        border:none; border-radius:8px; font-size:.95rem;
        font-weight:700; cursor:pointer; margin-top:4px;
      }
      .auth-submit:hover { background:#27ae60; }
      .auth-switch { text-align:center; font-size:.83rem; color:#636e72; margin-top:14px; }
      .auth-switch a { color:#3498db; }
    `;
    document.head.appendChild(s);
  };

  return { init, showModal, hideModal, updateNav, isLoggedIn, getToken, getUser,
           apiFetch, requireAuth, doLogout, _doLogin, _doSignup };
})();

document.addEventListener('DOMContentLoaded', Auth.init);
