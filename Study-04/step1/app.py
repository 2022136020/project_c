"""
냉장고 재료 인식 & 레시피 추천 앱
Step 1: 이미지 분석 (Gemma vision)
Step 2: 레시피 생성 (Qwen text)
Step 3: 사용자 인증 / 프로필 / 레시피 저장
"""
import base64
import hashlib
import io
import json
import os
import re
import time
from datetime import timedelta, datetime

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, send_file
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity, verify_jwt_in_request,
)
from flask_sqlalchemy import SQLAlchemy
from PIL import Image
from sqlalchemy import or_

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# ── 앱 설정 ────────────────────────────────────────────────
BASE_DIR = os.path.dirname(__file__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH']      = 10 * 1024 * 1024
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY']          = os.getenv('JWT_SECRET_KEY', 'dev-fallback-secret')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)

db     = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt    = JWTManager(app)

OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_URL     = 'https://openrouter.ai/api/v1/chat/completions'
THUMBNAIL_DIR      = os.path.join(BASE_DIR, 'static', 'thumbnails')

# ── 모델 목록 ──────────────────────────────────────────────
VISION_MODELS = [
    'google/gemma-3-27b-it:free',
    'google/gemma-3-12b-it:free',
    'google/gemma-3-4b-it:free',
]
RECIPE_MODELS = [
    'qwen/qwen3.6-plus:free',
    'qwen/qwen3-coder:free',
    'qwen/qwen3-next-80b-a3b-instruct:free',
    'google/gemma-3-27b-it:free',
    'google/gemma-3-4b-it:free',
]

# ── DB 모델 ────────────────────────────────────────────────
class User(db.Model):
    __tablename__ = 'users'
    id         = db.Column(db.Integer, primary_key=True)
    email      = db.Column(db.Text, unique=True, nullable=False)
    password   = db.Column(db.Text, nullable=False)
    nickname   = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    profile   = db.relationship('UserProfile',     back_populates='user', uselist=False, cascade='all, delete-orphan')
    recipes   = db.relationship('SavedRecipe',     back_populates='user', cascade='all, delete-orphan')
    histories = db.relationship('AnalysisHistory', back_populates='user', cascade='all, delete-orphan')


class UserProfile(db.Model):
    __tablename__ = 'user_profiles'
    user_id              = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    default_servings     = db.Column(db.Integer, default=2)
    dietary              = db.Column(db.Text, default='[]')
    preferred_categories = db.Column(db.Text, default='[]')
    allergies            = db.Column(db.Text, default='[]')
    skill_level          = db.Column(db.Text, default='중급')

    user = db.relationship('User', back_populates='profile')


class SavedRecipe(db.Model):
    __tablename__ = 'saved_recipes'
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title      = db.Column(db.Text, nullable=False)
    content    = db.Column(db.Text, nullable=False)
    tags       = db.Column(db.Text, default='[]')
    memo       = db.Column(db.Text)
    rating     = db.Column(db.Integer)
    model_used = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='recipes')


class AnalysisHistory(db.Model):
    __tablename__ = 'analysis_history'
    id             = db.Column(db.Integer, primary_key=True)
    user_id        = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    thumbnail_path = db.Column(db.Text)
    ingredients    = db.Column(db.Text)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='histories')

# ── JWT 헬퍼 ───────────────────────────────────────────────
def current_uid() -> int:
    return int(get_jwt_identity())


def optional_uid():
    try:
        verify_jwt_in_request(optional=True)
        uid = get_jwt_identity()
        return int(uid) if uid else None
    except Exception:
        return None

# ── 공통 유틸 ──────────────────────────────────────────────
class RateLimitError(Exception):
    pass


def extract_json_array(text: str):
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    text = re.sub(r'```(?:json)?', '', text).strip()
    start = text.find('[')
    end   = text.rfind(']')
    if start == -1 or end == -1:
        return None
    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return None


def _api_post(model: str, messages: list, max_tokens: int = 2048):
    return requests.post(
        OPENROUTER_URL,
        headers={'Authorization': f'Bearer {OPENROUTER_API_KEY}',
                 'Content-Type': 'application/json'},
        json={'model': model, 'messages': messages, 'max_tokens': max_tokens},
        timeout=90,
    )

# ── 캐시 ────────────────────────────────────────────────────
_recipe_cache: dict = {}
CACHE_TTL = 600


def _cache_key(ingredients, options):
    raw = json.dumps(sorted([i['name'] for i in ingredients]) + [options], sort_keys=True)
    return hashlib.md5(raw.encode()).hexdigest()


def _cache_get(key):
    e = _recipe_cache.get(key)
    return e[1] if e and time.time() - e[0] < CACHE_TTL else None


def _cache_set(key, val):
    _recipe_cache[key] = (time.time(), val)

# ── Step 1: 이미지 분석 ────────────────────────────────────
VISION_PROMPT = (
    'You are a kitchen assistant. Analyze the fridge image and list all visible food ingredients. '
    'Return ONLY a JSON array of objects with keys: '
    'name (Korean), quantity (string), category (one of: 채소,육류,유제품,조미료,과일,음료,기타). '
    'No explanation, no markdown. Raw JSON array only. '
    'Example: [{"name":"당근","quantity":"2개","category":"채소"}]'
)


def resize_and_encode(file_bytes: bytes):
    img = Image.open(io.BytesIO(file_bytes)).convert('RGB')
    img.thumbnail((1024, 1024), Image.LANCZOS)
    full_buf = io.BytesIO()
    img.save(full_buf, format='JPEG', quality=85)
    thumb = img.copy()
    thumb.thumbnail((200, 150), Image.LANCZOS)
    thumb_buf = io.BytesIO()
    thumb.save(thumb_buf, format='JPEG', quality=75)
    return base64.b64encode(full_buf.getvalue()).decode('utf-8'), thumb_buf.getvalue()


def call_vision_api(b64_image: str):
    messages = [{'role': 'user', 'content': [
        {'type': 'image_url', 'image_url': {'url': f'data:image/jpeg;base64,{b64_image}'}},
        {'type': 'text', 'text': VISION_PROMPT},
    ]}]
    last_status = 500
    for model in VISION_MODELS:
        resp = _api_post(model, messages, 1024)
        last_status = resp.status_code
        if resp.status_code == 200:
            return model, resp.json()['choices'][0]['message']['content']
        if resp.status_code not in (429, 503, 404):
            break
    if last_status == 429:
        raise RateLimitError()
    raise RuntimeError(f'Vision API error {last_status}')

# ── Step 2: 레시피 생성 ────────────────────────────────────
def build_recipe_prompt(ingredients, options):
    ing_names  = ', '.join(i['name'] for i in ingredients)
    count      = options.get('count', 2)
    servings   = options.get('servings', 2)
    max_time   = options.get('max_time', 30)
    dietary    = options.get('dietary', 'none')
    difficulty = options.get('difficulty', '보통')
    allergies  = options.get('allergies', [])
    diet_map   = {'none': '없음', 'vegetarian': '채식', 'gluten-free': '글루텐프리', 'dairy-free': '유제품 제외'}
    allergy_clause = f'Exclude allergens: {", ".join(allergies)}' if allergies else ''

    return (
        f'You are a professional Korean home-cooking chef.\n'
        f'Available fridge ingredients: {ing_names}\n\n'
        f'Constraints:\n'
        f'- Recipes to generate: {count}\n'
        f'- Servings: {servings} people\n'
        f'- Max cooking time: {max_time if max_time else "unlimited"} minutes\n'
        f'- Dietary restriction: {diet_map.get(dietary, "없음")}\n'
        f'- Difficulty: {difficulty}\n'
        f'{allergy_clause}\n\n'
        f'Return ONLY a valid JSON array, no markdown, no explanation.\n'
        f'Each element: {{"title":"제목","description":"2문장 설명",'
        f'"difficulty":"쉬움|보통|어려움","cook_time":20,"servings":{servings},'
        f'"ingredients":[{{"name":"재료","amount":"양"}}],'
        f'"steps":["단계1","단계2"],'
        f'"tips":["팁"],'
        f'"missing_ingredients":["없는재료"]}}'
    )


def call_recipe_api(ingredients, options):
    messages = [{'role': 'user', 'content': build_recipe_prompt(ingredients, options)}]
    last_status = 500
    for model in RECIPE_MODELS:
        resp = _api_post(model, messages, 2048)
        last_status = resp.status_code
        if resp.status_code == 200:
            return model, resp.json()['choices'][0]['message']['content']
        if resp.status_code == 404:
            continue
        if resp.status_code not in (429, 503):
            break
    if last_status == 429:
        raise RateLimitError()
    raise RuntimeError(f'Recipe API error {last_status}')

# ── 인증 헬퍼 ──────────────────────────────────────────────
def validate_password(pw: str):
    if len(pw) < 8:
        return '비밀번호는 8자 이상이어야 합니다.'
    if not re.search(r'[A-Za-z]', pw):
        return '비밀번호에 영문자가 포함되어야 합니다.'
    if not re.search(r'\d', pw):
        return '비밀번호에 숫자가 포함되어야 합니다.'
    return None


def profile_dict(p: UserProfile) -> dict:
    return {
        'default_servings':     p.default_servings,
        'dietary':              json.loads(p.dietary or '[]'),
        'preferred_categories': json.loads(p.preferred_categories or '[]'),
        'allergies':            json.loads(p.allergies or '[]'),
        'skill_level':          p.skill_level,
    }


def recipe_dict(r: SavedRecipe) -> dict:
    return {
        'id':         r.id,
        'title':      r.title,
        'content':    json.loads(r.content),
        'tags':       json.loads(r.tags or '[]'),
        'memo':       r.memo,
        'rating':     r.rating,
        'model_used': r.model_used,
        'created_at': r.created_at.isoformat(),
    }

# ── 페이지 라우트 ──────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/recipe')
def recipe_page():
    return render_template('recipe.html')


@app.route('/profile')
def profile_page():
    return render_template('profile.html')

# ── API: 이미지 분석 ───────────────────────────────────────
@app.route('/api/analyze', methods=['POST'])
def analyze():
    if 'image' not in request.files:
        return jsonify({'error': 'no_image'}), 400
    file = request.files['image']
    if file.mimetype not in ('image/jpeg', 'image/png', 'image/webp'):
        return jsonify({'error': 'invalid_type'}), 400
    file_bytes = file.read()
    if len(file_bytes) > 10 * 1024 * 1024:
        return jsonify({'error': 'too_large'}), 400

    try:
        b64, thumb_bytes = resize_and_encode(file_bytes)
    except Exception as e:
        return jsonify({'error': 'image_processing', 'message': str(e)}), 500

    try:
        model_used, raw_text = call_vision_api(b64)
    except RateLimitError:
        return jsonify({'error': 'rate_limit', 'retry_after': 60}), 429
    except Exception as e:
        return jsonify({'error': 'analysis_failed', 'message': str(e)}), 500

    ingredients = extract_json_array(raw_text)

    user_id = optional_uid()
    if user_id and ingredients:
        thumb_name = f'{user_id}_{int(time.time())}.jpg'
        thumb_path = os.path.join(THUMBNAIL_DIR, thumb_name)
        with open(thumb_path, 'wb') as f2:
            f2.write(thumb_bytes)
        old = (AnalysisHistory.query.filter_by(user_id=user_id)
               .order_by(AnalysisHistory.created_at.asc()).all())
        while len(old) >= 10:
            entry = old.pop(0)
            if entry.thumbnail_path and os.path.exists(entry.thumbnail_path):
                os.remove(entry.thumbnail_path)
            db.session.delete(entry)
        db.session.add(AnalysisHistory(
            user_id=user_id,
            thumbnail_path=thumb_path,
            ingredients=json.dumps(ingredients, ensure_ascii=False),
        ))
        db.session.commit()

    return jsonify({'ingredients': ingredients, 'raw_text': raw_text, 'model': model_used})

# ── API: 레시피 생성 ───────────────────────────────────────
@app.route('/api/recipe', methods=['POST'])
def recipe():
    data        = request.get_json(force=True)
    ingredients = data.get('ingredients', [])
    options     = data.get('options', {})

    if not ingredients:
        return jsonify({'error': 'no_ingredients', 'message': '재료를 1개 이상 입력해 주세요.'}), 400

    user_id = optional_uid()
    if user_id and 'allergies' not in options:
        p = UserProfile.query.filter_by(user_id=user_id).first()
        if p:
            options['allergies'] = json.loads(p.allergies or '[]')

    key = _cache_key(ingredients, options)
    cached = _cache_get(key)
    if cached:
        cached['from_cache'] = True
        return jsonify(cached)

    try:
        model_used, raw_text = call_recipe_api(ingredients, options)
    except RateLimitError:
        return jsonify({'error': 'rate_limit', 'retry_after': 60}), 429
    except Exception as e:
        return jsonify({'error': 'recipe_failed', 'message': str(e)}), 500

    recipes = extract_json_array(raw_text)
    result  = {'recipes': recipes, 'raw_text': raw_text,
               'model_used': model_used, 'from_cache': False}
    if recipes:
        _cache_set(key, result)
    return jsonify(result)

# ── API: 인증 ──────────────────────────────────────────────
@app.route('/api/auth/signup', methods=['POST'])
def signup():
    data     = request.get_json(force=True)
    email    = (data.get('email') or '').strip().lower()
    password = data.get('password', '')
    nickname = (data.get('nickname') or '').strip() or email.split('@')[0]

    if not email or '@' not in email:
        return jsonify({'error': '올바른 이메일을 입력해 주세요.'}), 400
    err = validate_password(password)
    if err:
        return jsonify({'error': err}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'error': '이미 사용 중인 이메일입니다.'}), 409

    pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    user    = User(email=email, password=pw_hash, nickname=nickname)
    db.session.add(user)
    db.session.flush()
    db.session.add(UserProfile(user_id=user.id))
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({'token': token, 'nickname': nickname, 'email': email}), 201


@app.route('/api/auth/login', methods=['POST'])
def login():
    data     = request.get_json(force=True)
    email    = (data.get('email') or '').strip().lower()
    password = data.get('password', '')

    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({'error': '이메일 또는 비밀번호가 올바르지 않습니다.'}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({'token': token,
                    'nickname': user.nickname or user.email.split('@')[0],
                    'email': user.email})


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    return jsonify({'message': '로그아웃되었습니다.'})


@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def me():
    user = User.query.get(current_uid())
    if not user:
        return jsonify({'error': 'not_found'}), 404
    return jsonify({'id': user.id, 'email': user.email,
                    'nickname': user.nickname,
                    'created_at': user.created_at.isoformat()})


@app.route('/api/auth/account', methods=['DELETE'])
@jwt_required()
def delete_account():
    user = User.query.get(current_uid())
    if not user:
        return jsonify({'error': 'not_found'}), 404
    for h in user.histories:
        if h.thumbnail_path and os.path.exists(h.thumbnail_path):
            os.remove(h.thumbnail_path)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': '계정이 삭제되었습니다.'})

# ── API: 프로필 ────────────────────────────────────────────
@app.route('/api/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user = User.query.get(current_uid())
    if not user:
        return jsonify({'error': 'not_found'}), 404
    p = user.profile or UserProfile(user_id=user.id)
    return jsonify({'nickname': user.nickname, **profile_dict(p)})


@app.route('/api/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user = User.query.get(current_uid())
    if not user:
        return jsonify({'error': 'not_found'}), 404
    data = request.get_json(force=True)

    if 'nickname' in data:
        user.nickname = str(data['nickname'])[:20]

    p = user.profile
    if not p:
        p = UserProfile(user_id=user.id)
        db.session.add(p)

    if 'default_servings' in data:
        p.default_servings = max(1, min(6, int(data['default_servings'])))
    if 'dietary' in data:
        p.dietary = json.dumps(data['dietary'], ensure_ascii=False)
    if 'preferred_categories' in data:
        p.preferred_categories = json.dumps(data['preferred_categories'], ensure_ascii=False)
    if 'allergies' in data:
        p.allergies = json.dumps(data['allergies'], ensure_ascii=False)
    if 'skill_level' in data:
        p.skill_level = str(data['skill_level'])

    db.session.commit()
    return jsonify({'message': '프로필이 저장되었습니다.',
                    'nickname': user.nickname, **profile_dict(p)})

# ── API: 레시피 CRUD ───────────────────────────────────────
@app.route('/api/recipes/export', methods=['GET'])
@jwt_required()
def export_recipes():
    uid     = current_uid()
    recipes = SavedRecipe.query.filter_by(user_id=uid).all()
    data    = json.dumps([recipe_dict(r) for r in recipes],
                         ensure_ascii=False, indent=2)
    buf = io.BytesIO(data.encode('utf-8'))
    buf.seek(0)
    return send_file(buf, mimetype='application/json',
                     as_attachment=True, download_name='my_recipes.json')


@app.route('/api/recipes', methods=['GET'])
@jwt_required()
def list_recipes():
    uid  = current_uid()
    q    = request.args.get('q', '').strip()
    sort = request.args.get('sort', 'created_at')
    page = int(request.args.get('page', 1))
    per  = 20

    query = SavedRecipe.query.filter_by(user_id=uid)
    if q:
        query = query.filter(or_(
            SavedRecipe.title.ilike(f'%{q}%'),
            SavedRecipe.content.ilike(f'%{q}%'),
        ))
    order_map = {
        'created_at': SavedRecipe.created_at.desc(),
        'rating':     SavedRecipe.rating.desc(),
        'title':      SavedRecipe.title.asc(),
    }
    query = query.order_by(order_map.get(sort, SavedRecipe.created_at.desc()))

    total   = query.count()
    recipes = query.offset((page - 1) * per).limit(per).all()
    return jsonify({'recipes': [recipe_dict(r) for r in recipes],
                    'total': total, 'page': page, 'per_page': per})


@app.route('/api/recipes', methods=['POST'])
@jwt_required()
def save_recipe():
    uid         = current_uid()
    data        = request.get_json(force=True)
    recipe_data = data.get('recipe', {})
    model_used  = data.get('model_used', '')

    if not recipe_data or not recipe_data.get('title'):
        return jsonify({'error': '레시피 데이터가 없습니다.'}), 400

    title = recipe_data.get('title', '')
    if SavedRecipe.query.filter_by(user_id=uid, title=title).first():
        return jsonify({'error': '이미 저장된 레시피입니다.', 'duplicate': True}), 409

    tags = [i['name'] for i in recipe_data.get('ingredients', [])[:3]]
    if recipe_data.get('difficulty'):
        tags.append(recipe_data['difficulty'])

    r = SavedRecipe(
        user_id=uid,
        title=title,
        content=json.dumps(recipe_data, ensure_ascii=False),
        tags=json.dumps(tags, ensure_ascii=False),
        model_used=model_used,
    )
    db.session.add(r)
    db.session.commit()
    return jsonify(recipe_dict(r)), 201


@app.route('/api/recipes/<int:rid>', methods=['GET'])
@jwt_required()
def get_recipe(rid):
    r = SavedRecipe.query.filter_by(id=rid, user_id=current_uid()).first_or_404()
    return jsonify(recipe_dict(r))


@app.route('/api/recipes/<int:rid>', methods=['PUT'])
@jwt_required()
def update_recipe(rid):
    r    = SavedRecipe.query.filter_by(id=rid, user_id=current_uid()).first_or_404()
    data = request.get_json(force=True)
    if 'memo' in data:
        r.memo = str(data['memo'])[:500]
    if 'rating' in data and data['rating'] in range(1, 6):
        r.rating = int(data['rating'])
    db.session.commit()
    return jsonify(recipe_dict(r))


@app.route('/api/recipes/<int:rid>', methods=['DELETE'])
@jwt_required()
def delete_recipe(rid):
    r = SavedRecipe.query.filter_by(id=rid, user_id=current_uid()).first_or_404()
    db.session.delete(r)
    db.session.commit()
    return jsonify({'message': '삭제되었습니다.'})

# ── API: 분석 이력 ────────────────────────────────────────
@app.route('/api/history', methods=['GET'])
@jwt_required()
def get_history():
    uid     = current_uid()
    entries = (AnalysisHistory.query.filter_by(user_id=uid)
               .order_by(AnalysisHistory.created_at.desc()).limit(20).all())
    result = []
    for h in entries:
        thumb_url = None
        if h.thumbnail_path and os.path.exists(h.thumbnail_path):
            fname     = os.path.basename(h.thumbnail_path)
            thumb_url = f'/static/thumbnails/{fname}'
        result.append({
            'id':          h.id,
            'thumbnail':   thumb_url,
            'ingredients': json.loads(h.ingredients or '[]'),
            'created_at':  h.created_at.isoformat(),
        })
    return jsonify({'history': result})


@app.route('/api/history/<int:hid>', methods=['DELETE'])
@jwt_required()
def delete_history(hid):
    h = AnalysisHistory.query.filter_by(id=hid, user_id=current_uid()).first_or_404()
    if h.thumbnail_path and os.path.exists(h.thumbnail_path):
        os.remove(h.thumbnail_path)
    db.session.delete(h)
    db.session.commit()
    return jsonify({'message': '삭제되었습니다.'})

# ── 앱 시작 ────────────────────────────────────────────────
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    if not OPENROUTER_API_KEY:
        print('[ERROR] OPENROUTER_API_KEY 없음')
    else:
        print(f'[OK] API 키: {OPENROUTER_API_KEY[:12]}...')
    app.run(debug=True, port=5001)
