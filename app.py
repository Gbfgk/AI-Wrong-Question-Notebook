"""
AI错题本 - 主应用
基于Flask + SQLite + OpenAI API
支持：用户管理、私密错题本、举一反三、错题解答
"""
import os
import json
import sqlite3
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, g
import hashlib
import webbrowser
import argparse
from threading import Timer

# 尝试导入OpenAI库
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()

# 配置
CONFIG_FILE = "data/config.json"
DB_FILE = "data/mistake_book.db"

def load_config():
    """加载配置文件"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def get_db():
    """获取数据库连接"""
    if 'db' not in g:
        g.db = sqlite3.connect(DB_FILE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    """关闭数据库连接"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """初始化数据库"""
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 创建表
    cursor.executescript("""
    -- 用户表
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(50) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        email VARCHAR(100),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP,
        is_active BOOLEAN DEFAULT 1
    );

    -- 错题表
    CREATE TABLE IF NOT EXISTS mistakes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        subject VARCHAR(50) NOT NULL,
        question_text TEXT NOT NULL,
        user_answer TEXT,
        correct_answer TEXT,
        error_reason TEXT,
        knowledge_points TEXT,
        difficulty_level INTEGER DEFAULT 1,
        source VARCHAR(200),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );

    -- 错题解答表（AI生成的解答）
    CREATE TABLE IF NOT EXISTS solutions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mistake_id INTEGER NOT NULL,
        solution_text TEXT NOT NULL,
        explanation TEXT,
        generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (mistake_id) REFERENCES mistakes(id) ON DELETE CASCADE
    );

    -- 举一反三练习题表
    CREATE TABLE IF NOT EXISTS similar_questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mistake_id INTEGER NOT NULL,
        question_text TEXT NOT NULL,
        answer TEXT,
        explanation TEXT,
        difficulty_level INTEGER DEFAULT 1,
        generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (mistake_id) REFERENCES mistakes(id) ON DELETE CASCADE
    );

    -- 创建索引
    CREATE INDEX IF NOT EXISTS idx_mistakes_user ON mistakes(user_id);
    CREATE INDEX IF NOT EXISTS idx_mistakes_subject ON mistakes(subject);
    CREATE INDEX IF NOT EXISTS idx_solutions_mistake ON solutions(mistake_id);
    CREATE INDEX IF NOT EXISTS idx_similar_mistake ON similar_questions(mistake_id);
    """)
    
    conn.commit()
    conn.close()

def hash_password(password):
    """密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()

def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('请先登录', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_ai_client():
    """获取AI客户端"""
    config = load_config()
    if not config or not OPENAI_AVAILABLE:
        return None
    
    api_config = config.get('api', {})
    base_url = api_config.get('base_url', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
    api_key = api_config.get('key', '')
    
    if not api_key or api_key == 'sk-00000000':
        return None
    
    try:
        client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )
        return client
    except Exception as e:
        print(f"AI客户端初始化失败：{e}")
        return None

def generate_ai_response(prompt, max_tokens=1000):
    """生成AI响应"""
    client = get_ai_client()
    if not client:
        return None
    
    try:
        response = client.chat.completions.create(
            model="qwen-plus",  # 使用通义千问模型
            messages=[
                {"role": "system", "content": "你是一位专业的教师助手，擅长解答学生问题并生成类似的练习题。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"AI生成失败：{e}")
        return None

# ==================== 路由 ====================

@app.route('/')
def index():
    """首页"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        email = request.form.get('email', '').strip()
        
        if not username or not password:
            flash('用户名和密码不能为空', 'danger')
            return render_template('register.html')
        
        db = get_db()
        cursor = db.cursor()
        
        # 检查用户名是否已存在
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            flash('用户名已存在', 'danger')
            return render_template('register.html')
        
        # 创建用户
        password_hash = hash_password(password)
        cursor.execute(
            "INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)",
            (username, password_hash, email)
        )
        db.commit()
        
        flash('注册成功，请登录', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('用户名和密码不能为空', 'danger')
            return render_template('login.html')
        
        db = get_db()
        cursor = db.cursor()
        
        password_hash = hash_password(password)
        cursor.execute(
            "SELECT id, username, email FROM users WHERE username = ? AND password_hash = ?",
            (username, password_hash)
        )
        user = cursor.fetchone()
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            
            # 更新最后登录时间
            cursor.execute(
                "UPDATE users SET last_login = ? WHERE id = ?",
                (datetime.now(), user['id'])
            )
            db.commit()
            
            flash('登录成功', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('用户名或密码错误', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """用户登出"""
    session.clear()
    flash('已退出登录', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """用户仪表盘"""
    db = get_db()
    cursor = db.cursor()
    
    # 统计信息
    cursor.execute("SELECT COUNT(*) as count FROM mistakes WHERE user_id = ?", (session['user_id'],))
    total_mistakes = cursor.fetchone()['count']
    
    cursor.execute("SELECT subject, COUNT(*) as count FROM mistakes WHERE user_id = ? GROUP BY subject", 
                   (session['user_id'],))
    subject_stats = cursor.fetchall()
    
    # 最近的错题
    cursor.execute("""
        SELECT m.*, s.solution_text 
        FROM mistakes m 
        LEFT JOIN solutions s ON m.id = s.mistake_id 
        WHERE m.user_id = ? 
        ORDER BY m.created_at DESC 
        LIMIT 5
    """, (session['user_id'],))
    recent_mistakes = cursor.fetchall()
    
    return render_template('dashboard.html', 
                         total_mistakes=total_mistakes,
                         subject_stats=subject_stats,
                         recent_mistakes=recent_mistakes)

@app.route('/mistakes')
@login_required
def mistakes_list():
    """错题列表"""
    db = get_db()
    cursor = db.cursor()
    
    subject = request.args.get('subject', '')
    search = request.args.get('search', '')
    
    query = "SELECT * FROM mistakes WHERE user_id = ?"
    params = [session['user_id']]
    
    if subject:
        query += " AND subject = ?"
        params.append(subject)
    
    if search:
        query += " AND (question_text LIKE ? OR knowledge_points LIKE ?)"
        search_term = f"%{search}%"
        params.extend([search_term, search_term])
    
    query += " ORDER BY created_at DESC"
    
    cursor.execute(query, params)
    mistakes = cursor.fetchall()
    
    # 获取所有科目
    cursor.execute("""
        SELECT DISTINCT subject FROM mistakes 
        WHERE user_id = ? 
        ORDER BY subject
    """, (session['user_id'],))
    subjects = [row['subject'] for row in cursor.fetchall()]
    
    return render_template('mistakes.html', mistakes=mistakes, subjects=subjects, 
                         current_subject=subject, search=search)

@app.route('/mistake/add', methods=['GET', 'POST'])
@login_required
def add_mistake():
    """添加错题"""
    if request.method == 'POST':
        subject = request.form.get('subject', '').strip()
        question_text = request.form.get('question_text', '').strip()
        user_answer = request.form.get('user_answer', '').strip()
        correct_answer = request.form.get('correct_answer', '').strip()
        error_reason = request.form.get('error_reason', '').strip()
        knowledge_points = request.form.get('knowledge_points', '').strip()
        difficulty_level = request.form.get('difficulty_level', 1, type=int)
        source = request.form.get('source', '').strip()
        
        if not subject or not question_text:
            flash('科目和题目内容不能为空', 'danger')
            return render_template('mistake_form.html')
        
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("""
            INSERT INTO mistakes (user_id, subject, question_text, user_answer, correct_answer, 
                                error_reason, knowledge_points, difficulty_level, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (session['user_id'], subject, question_text, user_answer, correct_answer,
              error_reason, knowledge_points, difficulty_level, source))
        
        db.commit()
        mistake_id = cursor.lastrowid
        
        flash('错题添加成功', 'success')
        return redirect(url_for('view_mistake', mistake_id=mistake_id))
    
    return render_template('mistake_form.html', mistake=None)

@app.route('/mistake/<int:mistake_id>')
@login_required
def view_mistake(mistake_id):
    """查看错题详情"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("""
        SELECT m.*, s.solution_text, s.explanation 
        FROM mistakes m 
        LEFT JOIN solutions s ON m.id = s.mistake_id 
        WHERE m.id = ? AND m.user_id = ?
    """, (mistake_id, session['user_id']))
    
    mistake = cursor.fetchone()
    
    if not mistake:
        flash('错题不存在', 'danger')
        return redirect(url_for('mistakes_list'))
    
    # 获取举一反三题目
    cursor.execute("""
        SELECT * FROM similar_questions 
        WHERE mistake_id = ? 
        ORDER BY generated_at DESC
    """, (mistake_id,))
    similar_questions = cursor.fetchall()
    
    return render_template('mistake_detail.html', mistake=mistake, 
                         similar_questions=similar_questions)

@app.route('/mistake/<int:mistake_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_mistake(mistake_id):
    """编辑错题"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("SELECT * FROM mistakes WHERE id = ? AND user_id = ?", 
                   (mistake_id, session['user_id']))
    mistake = cursor.fetchone()
    
    if not mistake:
        flash('错题不存在', 'danger')
        return redirect(url_for('mistakes_list'))
    
    if request.method == 'POST':
        subject = request.form.get('subject', '').strip()
        question_text = request.form.get('question_text', '').strip()
        user_answer = request.form.get('user_answer', '').strip()
        correct_answer = request.form.get('correct_answer', '').strip()
        error_reason = request.form.get('error_reason', '').strip()
        knowledge_points = request.form.get('knowledge_points', '').strip()
        difficulty_level = request.form.get('difficulty_level', 1, type=int)
        source = request.form.get('source', '').strip()
        
        if not subject or not question_text:
            flash('科目和题目内容不能为空', 'danger')
            return render_template('mistake_form.html', mistake=mistake)
        
        cursor.execute("""
            UPDATE mistakes 
            SET subject=?, question_text=?, user_answer=?, correct_answer=?, 
                error_reason=?, knowledge_points=?, difficulty_level=?, source=?,
                updated_at=?
            WHERE id=? AND user_id=?
        """, (subject, question_text, user_answer, correct_answer, error_reason,
              knowledge_points, difficulty_level, source, datetime.now(), 
              mistake_id, session['user_id']))
        
        db.commit()
        flash('错题更新成功', 'success')
        return redirect(url_for('view_mistake', mistake_id=mistake_id))
    
    return render_template('mistake_form.html', mistake=mistake)

@app.route('/mistake/<int:mistake_id>/delete', methods=['POST'])
@login_required
def delete_mistake(mistake_id):
    """删除错题"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("DELETE FROM mistakes WHERE id = ? AND user_id = ?", 
                   (mistake_id, session['user_id']))
    db.commit()
    
    flash('错题已删除', 'success')
    return redirect(url_for('mistakes_list'))

@app.route('/mistake/<int:mistake_id>/solve', methods=['POST'])
@login_required
def solve_mistake(mistake_id):
    """AI解答错题"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("SELECT * FROM mistakes WHERE id = ? AND user_id = ?", 
                   (mistake_id, session['user_id']))
    mistake = cursor.fetchone()
    
    if not mistake:
        return jsonify({'success': False, 'error': '错题不存在'}), 404
    
    # 构建提示词
    prompt = f"""
请为以下错题提供详细解答和分析：

科目：{mistake['subject']}
题目：{mistake['question_text']}
用户答案：{mistake['user_answer'] or '未作答'}
正确答案：{mistake['correct_answer'] or '未知'}
错误原因：{mistake['error_reason'] or '未填写'}
知识点：{mistake['knowledge_points'] or '未填写'}

请提供：
1. 详细的解题步骤
2. 关键知识点讲解
3. 易错点分析
"""
    
    solution_text = generate_ai_response(prompt)
    
    if solution_text:
        # 保存解答
        cursor.execute("""
            INSERT INTO solutions (mistake_id, solution_text, explanation)
            VALUES (?, ?, ?)
        """, (mistake_id, solution_text, "AI生成的详细解答"))
        db.commit()
        
        return jsonify({'success': True, 'solution': solution_text})
    else:
        return jsonify({'success': False, 'error': 'AI服务不可用，请检查配置'}), 500

@app.route('/mistake/<int:mistake_id>/similar', methods=['POST'])
@login_required
def generate_similar(mistake_id):
    """生成举一反三题目"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("SELECT * FROM mistakes WHERE id = ? AND user_id = ?", 
                   (mistake_id, session['user_id']))
    mistake = cursor.fetchone()
    
    if not mistake:
        return jsonify({'success': False, 'error': '错题不存在'}), 404
    
    # 构建提示词
    prompt = f"""
请基于以下错题生成3道类似的练习题（举一反三）：

科目：{mistake['subject']}
原题：{mistake['question_text']}
正确答案：{mistake['correct_answer'] or '未知'}
知识点：{mistake['knowledge_points'] or '未填写'}

要求：
1. 生成3道相似但不同的题目
2. 难度相当或略高
3. 每道题包含：题目、答案、简要解析
4. 按以下格式返回：

题目1：[题目内容]
答案1：[答案]
解析1：[解析]

题目2：[题目内容]
答案2：[答案]
解析2：[解析]

题目3：[题目内容]
答案3：[答案]
解析3：[解析]
"""
    
    response_text = generate_ai_response(prompt, max_tokens=1500)
    
    if response_text:
        # 解析响应并保存到数据库
        import re
        
        # 简单的解析逻辑
        questions = re.split(r'\n(?=题目\d+:)', response_text)
        count = 0
        
        for q in questions:
            if not q.strip():
                continue
            
            q_match = re.search(r'题目\d+:(.+?)(?=答案\d+:|$)', q, re.DOTALL)
            a_match = re.search(r'答案\d+:(.+?)(?=解析\d+:|$)', q, re.DOTALL)
            e_match = re.search(r'解析\d+:(.+?)$', q, re.DOTALL)
            
            if q_match:
                question_text = q_match.group(1).strip()
                answer = a_match.group(1).strip() if a_match else ''
                explanation = e_match.group(1).strip() if e_match else ''
                
                cursor.execute("""
                    INSERT INTO similar_questions (mistake_id, question_text, answer, explanation)
                    VALUES (?, ?, ?, ?)
                """, (mistake_id, question_text, answer, explanation))
                count += 1
        
        db.commit()
        
        return jsonify({'success': True, 'count': count, 'message': f'生成了{count}道练习题'})
    else:
        return jsonify({'success': False, 'error': 'AI服务不可用，请检查配置'}), 500

@app.route('/profile')
@login_required
def profile():
    """用户资料"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],))
    user = cursor.fetchone()
    
    return render_template('profile.html', user=user)

@app.route('/settings')
@login_required
def settings():
    """系统设置（仅管理员）"""
    config = load_config()
    return render_template('settings.html', config=config)

def open_browser():
    """延迟打开浏览器"""
    webbrowser.open('http://localhost:5000')

if __name__ == '__main__':
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='AI 错题本')
    parser.add_argument('--no-browser', action='store_true', help='不自动打开浏览器')
    args = parser.parse_args()
    
    init_db()
    
    print("=" * 60)
    print("AI 错题本启动中...")
    print("访问地址：http://localhost:5000")
    print("如果是首次启动，系统将引导您进行配置")
    if not args.no_browser:
        print("正在自动打开浏览器...")
        Timer(1.5, open_browser).start()  # 延迟1.5秒打开浏览器，等待服务启动
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
