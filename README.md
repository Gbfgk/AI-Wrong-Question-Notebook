# AI 错题本

基于 Python + SQLite + Flask + Google Material Design 的 AI 智能错题管理系统。

## 功能特点

- ✅ **用户管理**: 注册、登录、个人资料管理（密码 SHA256 加密）
- ✅ **私密错题本**: 每个用户独立的数据空间，支持科目分类、搜索筛选
- ✅ **错题解答**: 集成 OpenAI API 自动生成详细题目解析
- ✅ **举一反三**: 基于错题智能生成 3 道相似练习题
- ✅ **管理员系统**: 首次启动配置管理员账户，可管理系统设置
- ✅ **Google Material Design**: 现代化 UI 设计，响应式布局

## 技术栈

- **后端**: Python 3.10+、Flask、SQLite
- **前端**: HTML5、Materialize CSS、JavaScript
- **AI 服务**: OpenAI API 兼容接口（支持阿里云通义千问等）

## 快速开始

### 方法一：Docker Compose（推荐）

```bash
# 一键部署
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 访问地址：http://localhost:5000
```

首次访问会自动跳转到配置页面，需要设置：
- API Base URL（默认：https://dashscope.aliyuncs.com/compatible-mode/v1）
- API Key（您的 AI 服务密钥）
- 管理员用户名和密码

### 方法二：本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 启动应用
python app.py

# 访问地址：http://localhost:5000
```

### 方法三：打包为可执行文件

```bash
# 安装 PyInstaller
pip install pyinstaller

# 打包
python build.py

# 生成的可执行文件在 dist/ 目录
# 首次运行时会自动提示配置
```

## 项目结构

```
/workspace/
├── app.py                 # 主应用
├── build.py               # 打包脚本
├── Dockerfile             # Docker 镜像
├── docker-compose.yml     # Docker Compose 配置
├── requirements.txt       # 依赖清单
├── README.md              # 本文档
├── templates/             # HTML 模板
│   ├── base.html          # 基础布局
│   ├── index.html         # 首页
│   ├── login.html         # 登录
│   ├── register.html      # 注册
│   ├── setup.html         # 首次配置（新增）
│   ├── dashboard.html     # 仪表盘
│   ├── mistakes.html      # 错题列表
│   ├── mistake_form.html  # 添加/编辑
│   ├── mistake_detail.html# 详情页
│   ├── profile.html       # 个人资料
│   └── settings.html      # 系统设置
├── static/
│   ├── css/style.css      # 自定义样式
│   └── js/main.js         # 交互逻辑
└── data/
    ├── config.json        # API 配置（自动生成）
    └── mistake_book.db    # SQLite 数据库（自动生成）
```

## 使用说明

### 首次启动

1. 访问 http://localhost:5000
2. 自动跳转到配置页面
3. 填写以下信息：
   - **API Base URL**: AI 服务地址（默认使用阿里云通义千问）
   - **API Key**: 您的 API 密钥
   - **管理员用户名**: 创建管理员账户
   - **管理员密码**: 设置管理员密码
   - **管理员邮箱**: （可选）
4. 点击"完成配置并继续"
5. 使用管理员账户登录

### 普通用户

- 管理员可以在系统中创建普通用户，或开放注册
- 每个用户只能看到自己的错题
- 支持按科目筛选、关键词搜索

### AI 功能

- **错题解答**: 在错题详情页点击"AI 解答"按钮
- **举一反三**: 在错题详情页点击"生成练习题"按钮
- 需要有效的 API Key 才能使用 AI 功能

### 管理员功能

- 访问 `/settings` 页面更新 API 配置
- 查看所有统计信息
- 管理系统设置

## API 配置说明

### 阿里云通义千问（默认）

- **Base URL**: `https://dashscope.aliyuncs.com/compatible-mode/v1`
- **API Key**: 在阿里云控制台获取

### 其他兼容 OpenAI API 的服务

只要服务兼容 OpenAI API 格式，都可以使用：
- **Base URL**: 服务商提供的地址
- **API Key**: 对应服务的密钥

## 常见问题

### Q: 忘记管理员密码怎么办？

A: 删除 `data/mistake_book.db` 和 `data/config.json`，重新启动应用进行初始化配置。
注意：这会清空所有数据！

### Q: AI 功能无法使用？

A: 检查以下几点：
1. API Key 是否正确
2. Base URL 是否可访问
3. 是否有足够的 API 调用额度
4. 查看应用日志获取详细错误信息

### Q: 如何备份数据？

A: 只需备份 `data/` 目录：
```bash
cp -r data/ backup_data/
```

### Q: Docker 容器数据会丢失吗？

A: 不会。`docker-compose.yml` 中已配置卷映射，数据持久化在宿主机的 `./data` 目录。

## 开发模式

```bash
# 启用调试模式
export FLASK_DEBUG=1
python app.py

# 或使用环境变量
FLASK_DEBUG=1 python app.py
```

## License

MIT License

## 更新日志

### v2.0 (当前版本)
- ✅ 删除 setup_config.py，整合到 Web UI
- ✅ 添加管理员账户系统
- ✅ 首次启动通过 Web UI 配置
- ✅ 仅使用 SQLite，简化部署
- ✅ 添加 Docker Compose 一键部署
- ✅ 优化权限控制（admin_required 装饰器）

### v1.0
- 初始版本
- 基础错题管理功能
- AI 解答和举一反三
