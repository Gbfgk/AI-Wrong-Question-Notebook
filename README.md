# AI错题本

基于 Python + Flask + SQLite + OpenAI API 的智能错题管理系统，采用 Google Material Design 设计风格。

## 功能特性

- **用户管理**: 注册、登录、个人资料管理
- **私密错题本**: 每个用户拥有独立的错题存储空间
- **错题解答**: 集成 AI 自动生成详细题目解析
- **举一反三**: 基于错题智能生成相似练习题
- **科目分类**: 支持多科目管理和筛选
- **搜索功能**: 快速查找题目和知识点
- **响应式设计**: 适配桌面和移动设备

## 技术栈

### 后端
- Python 3.x
- Flask (Web框架)
- SQLite (数据库)
- OpenAI API (AI服务)

### 前端
- HTML5 + CSS3 + JavaScript
- Materialize CSS (Google Material Design)
- Material Icons

## 快速开始

### 1. 安装依赖

```bash
pip install flask openai
```

### 2. 首次启动配置

运行配置脚本，输入数据库和API配置信息：

```bash
python setup_config.py
```

配置项包括：
- 数据库连接（主机、端口、名称、用户名、密码）
- API Base URL（默认：https://dashscope.aliyuncs.com/compatible-mode/v1）
- API密钥（sk-xxxxx）

### 3. 启动应用

```bash
python app.py
```

访问地址：http://localhost:5000

## 目录结构

```
/workspace
├── app.py                 # 主应用程序
├── setup_config.py        # 初始化配置脚本
├── templates/             # HTML模板
│   ├── base.html         # 基础模板
│   ├── index.html        # 首页
│   ├── login.html        # 登录页
│   ├── register.html     # 注册页
│   ├── dashboard.html    # 仪表盘
│   ├── mistakes.html     # 错题列表
│   ├── mistake_form.html # 添加/编辑错题
│   ├── mistake_detail.html # 错题详情
│   ├── profile.html      # 个人资料
│   └── settings.html     # 系统设置
├── static/               # 静态资源
│   ├── css/
│   │   └── style.css     # 自定义样式
│   └── js/
│       └── main.js       # JavaScript
└── data/                 # 数据文件
    ├── config.json       # 配置文件
    └── mistake_book.db   # SQLite数据库
```

## 使用说明

### 用户注册与登录

1. 访问首页，点击"免费注册"
2. 填写用户名、邮箱（可选）和密码
3. 注册成功后登录账户

### 添加错题

1. 登录后点击导航栏"添加错题"
2. 填写题目信息：
   - 科目（数学、语文、英语等）
   - 题目内容
   - 你的答案
   - 正确答案
   - 错误原因
   - 知识点
   - 难度等级
   - 题目来源

### AI智能解答

1. 在错题详情页点击"获取AI解答"
2. 系统将调用AI生成详细解析
3. 解答将自动保存到数据库

### 举一反三

1. 在错题详情页点击"生成练习题"
2. AI将基于原题生成3道相似练习题
3. 练习题包含答案和解析

## 配置说明

### 配置文件 (data/config.json)

```json
{
    "database": {
        "host": "localhost",
        "port": "3306",
        "name": "mistake_book",
        "user": "root",
        "password": ""
    },
    "api": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "key": "sk-xxxxxxxxxxxxxxxx"
    }
}
```

### API配置

默认使用阿里云通义千问API，也支持其他兼容OpenAI格式的服务：

- 阿里云通义千问：https://dashscope.aliyuncs.com/compatible-mode/v1
- OpenAI官方：https://api.openai.com/v1
- 其他兼容服务

## 数据库设计

### 主要数据表

- `users`: 用户信息表
- `mistakes`: 错题信息表
- `solutions`: AI解答表
- `similar_questions`: 举一反三练习题表

## 安全提示

1. 请妥善保管API密钥，不要泄露
2. 建议使用强密码
3. 生产环境请启用HTTPS
4. 定期备份数据库

## 开发计划

- [ ] 学习统计分析
- [ ] 错题导出功能
- [ ] 批量导入错题
- [ ] 错题分享功能
- [ ] 移动端APP
- [ ] 更多AI模型支持

## 许可证

MIT License

## 技术支持

如有问题或建议，欢迎提交Issue。
