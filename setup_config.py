"""
AI错题本 - 初始化配置脚本
首次启动时运行，收集数据库和API配置信息
"""
import os
import json
import sqlite3

CONFIG_FILE = "data/config.json"
DB_INIT_SCRIPT = "data/init_db.sql"

def get_input(prompt, default=None):
    """获取用户输入，支持默认值"""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    else:
        return input(f"{prompt}: ").strip()

def main():
    print("=" * 60)
    print("AI错题本 - 首次启动配置")
    print("=" * 60)
    print()
    
    # 确保data目录存在
    os.makedirs("data", exist_ok=True)
    
    # 收集数据库配置
    print("请配置数据库连接信息:")
    db_host = get_input("数据库主机", "localhost")
    db_port = get_input("数据库端口", "3306")
    db_name = get_input("数据库名称", "mistake_book")
    db_user = get_input("数据库用户名", "root")
    db_password = get_input("数据库密码", "")
    
    # 收集API配置
    print("\n请配置OpenAI API信息:")
    api_base_url = get_input(
        "API Base URL", 
        "https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    api_key = get_input("API密钥", "sk-00000000")
    
    # 保存配置
    config = {
        "database": {
            "host": db_host,
            "port": db_port,
            "name": db_name,
            "user": db_user,
            "password": db_password
        },
        "api": {
            "base_url": api_base_url,
            "key": api_key
        }
    }
    
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    
    print(f"\n✓ 配置文件已保存到: {CONFIG_FILE}")
    
    # 创建数据库初始化脚本
    init_sql = """
-- AI错题本数据库初始化脚本
-- 注意：实际使用时需要根据配置的数据库类型调整语法

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

-- 插入默认管理员账户（密码需要哈希处理，这里仅作示例）
-- 实际应用中应该使用安全的密码哈希
INSERT OR IGNORE INTO users (username, password_hash, email) 
VALUES ('admin', 'admin123', 'admin@example.com');
"""
    
    with open(DB_INIT_SCRIPT, 'w', encoding='utf-8') as f:
        f.write(init_sql)
    
    print(f"✓ 数据库初始化脚本已保存到: {DB_INIT_SCRIPT}")
    print("\n" + "=" * 60)
    print("配置完成！")
    print("注意：当前配置使用SQLite作为默认数据库以确保开箱即用。")
    print("如需使用MySQL/PostgreSQL，请修改app.py中的数据库连接配置。")
    print("=" * 60)

if __name__ == "__main__":
    main()
