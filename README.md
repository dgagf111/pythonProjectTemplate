# Python Project Template

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.112.2-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 🚀 项目简介

这是一个**企业级Python应用程序模板**，遵循现代Python开发最佳实践，提供了完整的微服务架构基础设施。项目采用标准化的包结构，集成了认证系统、缓存层、任务调度、监控告警等企业级特性。

## ✨ 核心特性

### 🏗️ 架构特性
- ✅ **标准化包结构**：遵循PEP 518，采用src/布局
- ✅ **模块化设计**：高内聚、低耦合的组件设计
- ✅ **统一管理**：配置、常量、工具类、异常处理统一管理
- ✅ **类型安全**：全面的类型提示支持
- ✅ **现代化工具链**：pyproject.toml、异步编程、依赖注入

### 🔧 技术特性
- 🌐 **FastAPI框架**：高性能异步Web框架，自动API文档
- 🗄️ **数据库支持**：SQLAlchemy 2.0 + MySQL，支持异步操作
- 🔐 **认证系统**：JWT令牌认证，密码安全加密
- 📦 **缓存系统**：Redis + 内存缓存，优雅降级
- ⏰ **任务调度**：APScheduler集成，支持cron/interval任务
- 📊 **监控系统**：Prometheus指标，系统资源监控
- 📝 **日志系统**：结构化日志，按时间分层存储
- 🐳 **容器化**：Docker支持，生产环境就绪

## 📁 项目结构

```
pythonProjectTemplate/
├── src/                              # 源代码目录（标准Python包结构）
│   └── pythonprojecttemplate/        # 主包目录
│       ├── core/                     # 核心模块（常量、工具类、异常）
│       ├── models/                   # 数据模型
│       ├── services/                 # 业务服务层
│       └── api/                      # API接口层
├── api/                              # API相关（兼容旧结构）
├── config/                           # 配置管理
├── cache/                            # 缓存服务
├── db/                               # 数据库相关
├── scheduler/                        # 任务调度
├── monitoring/                       # 监控服务
├── log/                              # 日志服务
├── utils/                            # 工具模块
├── modules/                          # 业务模块
├── tests/                            # 测试文件
├── docs/                             # 项目文档
│   ├── updates/                      # 更新记录
│   ├── guides/                       # 使用指南
│   ├── modules/                      # 模块文档
│   ├── database/                     # 数据库文档
│   └── legacy/                       # 历史文档
├── dependencies/                     # 依赖管理
│   ├── requirements.txt              # 统一依赖列表
│   ├── requirements-dev-only.txt     # 开发专用依赖
│   ├── install_dependencies.sh       # 智能安装脚本
│   └── DEPENDENCY_MANAGEMENT.md      # 依赖管理指南
├── pyproject.toml                    # 项目配置文件
├── main.py                           # 应用程序入口
└── README.md                         # 项目说明
```

📚 **详细架构说明**: 查看 [项目架构文档](docs/PROJECT_ARCHITECTURE.md)

## ⚙️ 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd pythonProjectTemplate

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或 .venv\Scripts\activate  # Windows

# 安装依赖
pip install -r dependencies/requirements.txt

# 额外安装开发工具（可选）
pip install -r dependencies/requirements-dev-only.txt

# 🚀 快速安装脚本 (推荐)
./dependencies/install_dependencies.sh dev

# 📖 详细依赖说明
# 查看完整的依赖管理指南: dependencies/DEPENDENCY_MANAGEMENT.md
```

### 2. 环境配置

```bash
# 复制环境变量文件
cp .env.example .env

# 编辑环境变量
vim .env
```

必需的环境变量：
```bash
# 数据库配置
MYSQL_USERNAME=your_username
MYSQL_PASSWORD=your_password
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=your_database

# Redis配置（可选）
REDIS_HOST=localhost
REDIS_PORT=6379

# API配置
SECRET_KEY=your-secret-key
API_VERSION=v1
```

### 3. 启动应用

```bash
# 开发模式
python main.py

# 或使用uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 访问服务

- **API文档**: http://localhost:8000/docs
- **Prometheus指标**: http://localhost:9966/metrics
- **健康检查**: http://localhost:8000/health

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
python tests/run_tests.py all

# 运行框架测试
python tests/run_tests.py framework

# 运行业务测试
python tests/run_tests.py business

# 使用pytest
pytest tests/ -v
```

### 测试覆盖率

```bash
pytest --cov=src tests/
```

## 🐳 Docker部署

### 单容器部署

```bash
# 构建镜像
docker build -t pythonprojecttemplate .

# 运行容器
docker run -d \
  --name app \
  -p 8000:8000 \
  -e MYSQL_HOST=host.docker.internal \
  -e MYSQL_USERNAME=root \
  -e MYSQL_PASSWORD=password \
  pythonprojecttemplate
```

### Docker Compose部署

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 停止服务
docker-compose down
```

## 📖 文档

- 📋 **[项目架构文档](docs/PROJECT_ARCHITECTURE.md)** - 详细的架构设计和组件说明
- 📝 **[更新记录](docs/updates/)** - 版本更新和功能变更记录
- 📖 **[使用指南](docs/guides/)** - 详细的使用说明和最佳实践
- 🔧 **[模块文档](docs/modules/)** - 各个模块的详细说明

## 🏗️ 核心模块

| 模块 | 描述 | 文档链接 |
|------|------|----------|
| **认证系统** | JWT令牌认证，用户管理 | [auth.md](docs/modules/auth.md) |
| **缓存系统** | Redis+内存缓存，优雅降级 | [cache.md](docs/modules/cache.md) |
| **数据库** | SQLAlchemy ORM，迁移管理 | [database.md](docs/modules/database.md) |
| **任务调度** | 定时任务，重试机制 | [scheduler.md](docs/modules/scheduler.md) |
| **监控系统** | Prometheus指标，资源监控 | [monitoring.md](docs/modules/monitoring.md) |
| **日志系统** | 结构化日志，分层存储 | [logging.md](docs/modules/logging.md) |

## 🔄 更新历史

- **v2.0.0** - [代码组织优化](docs/updates/002-code-organization-optimization.md)
  - 统一常量管理系统
  - 工具类体系重构
  - 异常处理层次化
  - 代码重复度减少80%+

- **v1.0.0** - [项目结构标准化](docs/updates/001-project-structure-standardization.md)
  - 标准Python包结构
  - pyproject.toml现代化配置
  - src/布局迁移
  - 依赖管理优化

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙋‍♂️ 支持

如有问题或建议，请：

- 📋 提交 [Issue](https://github.com/your-username/pythonProjectTemplate/issues)
- 💬 参与 [Discussions](https://github.com/your-username/pythonProjectTemplate/discussions)
- 📧 联系维护者

---

⭐ 如果这个项目对你有帮助，请给它一个星标！