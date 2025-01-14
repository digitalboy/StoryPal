好的，我理解了。你需要我更新 `development_steps.md` 文档，主要包括以下几个方面：

1.  **明确指出** `# app/utils/literacy_calculator.py` **中生字率计算逻辑已经独立，并只关注字符级别的已知字判断，不涉及词性标注和分词逻辑。**
2.  **根据最新的代码和讨论进行更新**
3.  **拆分文档**，使其更易于管理和阅读。

**文档拆分方案：**

我将把 `development_steps.md` 文档拆分为以下几个更小的文档：

*   `development_setup.md`:  包含开发前的准备工作，例如环境配置、代码仓库和项目结构。
*   `core_concepts.md`:  包含核心概念的定义，例如字词、级别、生字率、已知字和生字。
*   `literacy_calculation.md`:  专门描述生字率计算的核心算法、流程图和伪代码。
*   `multi_turn_dialogue.md`: 专门描述多轮对话策略。
*   `development_process.md`:  包含具体的开发步骤，例如模型层开发、服务层开发、API 层开发、错误处理、配置管理、日志记录、单元测试、集成测试、代码审查和持续集成。
*   `deployment.md`:  包含部署相关的步骤。
*  `coding_conventions.md`: 包含代码开发规范。

这样拆分后，每个文档都专注于一个特定的主题，更易于理解和维护。

**更新后的文档内容**

以下是更新后的各个文档内容，我将突出显示与生字率计算逻辑独立性相关的更改，以及其他修改。

**`development_setup.md`**

```markdown
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
5.  **安装 Docker**:  安装 Docker 用于部署项目。

### 2.2 代码仓库

1.  **创建代码仓库**: 在 GitHub 或其他代码托管平台上创建项目代码仓库。
2.  **克隆代码仓库**: 将代码仓库克隆到本地开发环境。

### 2.3 项目结构

```
StroyPal/
├── app/ # 应用程序代码
│ ├── init.py
│ ├── models/ # 数据模型
│ │ ├── init.py
│ │ ├── base_model.py
│ │ ├── word_model.py # 字词模型
│ │ ├── scene_model.py # 场景模型
│ │ └── story_model.py # 故事模型
│ ├── services/ # 业务逻辑服务
│ │ ├── init.py
│ │ ├── word_service.py # 字词服务
│ │ ├── scene_service.py # 场景服务
│ │ └── story_service.py # 故事服务
│ ├── utils/ # 工具函数
│ │ ├── init.py
│ │ ├── error_handling.py # 错误处理函数
│ │ ├── api_key_auth.py # API Key 认证
│ │ └── literacy_calculator.py # 生字率计算
│ ├── api/ # API 路由
│ │ ├── init.py
│ │ ├── word_api.py # 字词 API
│ │ ├── scene_api.py # 场景 API
│ │ └── story_api.py # 故事 API
│ ├── config.py # 项目配置
│ ├── prompts
│ │
│ └── data/ # 测试数据
│ ├── words.json # 字词数据
│ ├── scenes.json # 场景数据
│ └── story.json # 故事数据
├── tests/ # 测试代码
│ ├── init.py
│ ├── conftest.py
│ ├── models/ # 模型层测试
│ │ ├── test_word_model.py
│ │ ├── test_scene_model.py
│ │ └── test_story_model.py
│ ├── services/ # 服务层测试
│ │ ├── test_word_service.py
│ │ ├── test_scene_service.py
│ │ └── test_story_service.py
│ ├── utils/ # 工具函数测试
│ │ └── test_literacy_calculator.py # 生字率计算器测试
│ └── api/ # API 层测试
│ ├── test_word_api.py
│ ├── test_scene_api.py
│ └── test_story_api.py
├── docs/ # 项目文档
│ ├── api.md # API 文档
│ ├── data_models.md # 数据模型文档
│ ├── testing.md # 测试策略文档
│ ├── error_codes.md # 错误码文档
│ ├── development_setup.md # 开发准备文档
│ ├── core_concepts.md # 核心概念文档
│ ├── literacy_calculation.md # 生字率计算文档
│ ├── multi_turn_dialogue.md # 多轮对话策略文档
│ ├── development_process.md # 开发步骤文档
│ ├── deployment.md # 部署文档
│ ├── coding_conventions.md # 代码规范文档
│ └── prompt_engineering.md # 提示语工程文档
├── .env # 环境变量
├── requirements.txt # 依赖列表
├── README.md # 项目说明
├── docker-compose.yml # Docker Compose 文件
└── Dockerfile # Dockerfile 文件
```
