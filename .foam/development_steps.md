# 开发准备

## 1. 概述

本文档旨在为中文学习平台的开发提供详细的开发前准备指导，确保开发环境配置正确。

## 2. 开发前准备

### 2.1 环境配置

1.  **安装 Python 3.12**: 确保你的开发环境中安装了 Python 3.12 或更高版本。
2.  **安装依赖**: 使用 `pip` 安装项目所需的依赖包，例如 `Flask`, `pytest`, `requests`, `python-dotenv`, `Jinja2` 等。可以使用 `pip install -r requirements.txt` 安装所有依赖包。
3.  **配置虚拟环境**: 建议使用虚拟环境来管理项目依赖，避免不同项目之间的依赖冲突。例如使用 `venv`, 可以执行以下步骤创建和激活虚拟环境：

    ```bash
    python -m venv venv
    source venv/bin/activate  # On macOS and Linux
    # venv\Scripts\activate # On Windows
    ```

4.  **配置环境变量**: 创建 `.env` 文件，配置项目所需的敏感信息和可配置参数，例如 API Key、DeepSeek API Key、容差值等。具体请参考 `docs/config.md`。
5.  **安装 Docker**: 安装 Docker 用于部署项目。

### 2.2 代码仓库

1.  **创建代码仓库**: 在 GitHub 或其他代码托管平台上创建项目代码仓库。
2.  **克隆代码仓库**: 将代码仓库克隆到本地开发环境。

### 2.3 项目结构

StroyPal/
├── app/ # 应用程序代码
│   ├── \_\_init\_\_.py
│   ├── models/ # 数据模型
│   │   ├── \_\_init\_\_.py
│   │   ├── base\_model.py
│   │   ├── word\_model.py # **词语**模型
│   │   ├── scene\_model.py # 场景模型
│   │   └── story\_model.py # 故事模型
│   ├── services/ # 业务逻辑服务
│   │   ├── \_\_init\_\_.py
│   │   ├── word\_service.py # **词语**服务
│   │   ├── scene\_service.py # 场景服务
│   │   └── story\_service.py # 故事服务
│   ├── utils/ # 工具函数
│   │   ├── \_\_init\_\_.py
│   │   ├── error\_handling.py # 错误处理函数
│   │   ├── api\_key\_auth.py # API Key 认证
│   │   └── literacy\_calculator.py # **生词率**计算
│   ├── api/ # API 路由
│   │   ├── \_\_init\_\_.py
│   │   ├── word\_api.py # **词语** API
│   │   ├── scene\_api.py # 场景 API
│   │   └── story\_api.py # 故事 API
│   ├── config.py # 项目配置
│   ├── prompts
│   │       └── (存放prompt的目录)
│   └── data/ # 测试数据
│       ├── words.json # **词语**数据
│       ├── scenes.json # 场景数据
│       └── story.json # 故事数据
├── tests/ # 测试代码
│   ├── \_\_init\_\_.py
│   ├── conftest.py
│   ├── models/ # 模型层测试
│   │   ├── test\_word\_model.py
│   │   ├── test\_scene\_model.py
│   │   └── test\_story\_model.py
│   ├── services/ # 服务层测试
│   │   ├── test\_word\_service.py
│   │   ├── test\_scene\_service.py
│   │   └── test\_story\_service.py
│   ├── utils/ # 工具函数测试
│   │   └── test\_literacy\_calculator.py # **生词率**计算器测试
│   └── api/ # API 层测试
│       ├── test\_word\_api.py
│       ├── test\_scene\_api.py
│       └── test\_story\_api.py
├── docs/ # 项目文档
│   ├── api.md # API 文档
│   ├── data\_models.md # 数据模型文档
│   ├── testing.md # 测试策略文档
│   ├── error\_codes.md # 错误码文档
│   ├── development\_setup.md # 开发准备文档
│   ├── core\_concepts.md # 核心概念文档
│   ├── literacy\_calculation.md # **生词率**计算文档
│   ├── multi\_turn\_dialogue.md # 多轮对话策略文档
│   ├── development\_process.md # 开发步骤文档
│   ├── deployment.md # 部署文档
│   ├── coding\_conventions.md # 代码规范文档
│   └── prompt\_engineering.md # 提示语工程文档
├── .env # 环境变量
├── requirements.txt # 依赖列表
├── README.md # 项目说明
├── docker-compose.yml # Docker Compose 文件
└── Dockerfile # Dockerfile 文件