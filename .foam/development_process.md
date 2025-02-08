# 开发步骤

## 1. 概述

本文档详细描述了中文学习平台的核心开发步骤，确保开发过程高效、规范且正确。

## 2. 开发步骤

### 2.1 需求分析

1.  **熟悉文档**: 仔细阅读产品需求文档 (PRD) 和 API 设计指南，明确每个 API 的功能、输入参数、输出格式和错误处理逻辑。
2.  **理解数据模型**: 仔细阅读数据模型文档，理解数据结构，字段类型，和取值范围。
3.  **分解任务**: 将 PRD 中的需求分解为可执行的开发任务。
4.  **制定计划**: 根据任务的优先级，制定开发计划。

### 2.2 模型层开发

1.  **创建模型**: 在 `app/models` 目录下创建数据模型文件，例如 `word.py`、`scene.py` 和 `story.py`。
2.  **定义属性**: 根据 `docs/data_models.md` 定义数据模型的属性。
3.  **定义方法**: 定义数据模型的 CRUD 操作方法。
4.  **添加单元测试**: 在 `tests/models` 目录下创建单元测试，验证数据模型的正确性。

### 2.3 服务层开发

1.  **创建服务**: 在 `app/services` 目录下创建业务逻辑服务文件，例如 `word_service.py`、`scene_service.py` 和 `story_service.py`。
2.  **实现业务逻辑**: 在服务层实现业务逻辑，例如故事的生成、**词语**的查询、场景的管理。
    - **注意**： **生词率的计算逻辑已独立在 `app/utils/literacy_calculator.py` 中， 服务层不需要关心生词率的计算细节。**
    - **核心的生词率计算算法应该使用 `app/utils/literacy_calculator.py` 中提供的 `calculate_literacy_rate` 方法。** **详细定义和计算方法见 [`生词与生词率.md`](生词与生词率.md)**。
    - **多轮对话**: 实现多轮对话的逻辑， 根据 `prompt_engineering.md` 中定义的模板， 构建提示语。 **使用状态机管理对话流程，根据用户的反馈动态调整对话策略。**
      - **状态机:** 使用一个简单的状态枚举来表示对话状态，例如 `INIT`, `PROVIDE_KNOWN_WORDS`, `FINAL_INSTRUCTION`, `FAILED`。
      - **对话策略：**
        1.  **`INIT` 状态**: 发送初始提示语模板。
        2.  **`PROVIDE_KNOWN_WORDS` 状态**: 根据 `vocabulary_level` 加载已知**词汇**，并添加到提示语中。
        3.  **`FINAL_INSTRUCTION` 状态**: 发送最终指令，并等待 AI 生成故事。
        4.  **`INIT` -> `PROVIDE_KNOWN_WORDS`**: 初始状态，发送初始提示语后，进入 `PROVIDE_KNOWN_WORDS` 状态。
        5.  **`PROVIDE_KNOWN_WORDS` -> `FINAL_INSTRUCTION`**: 提供已知**词汇**后，进入 `FINAL_INSTRUCTION` 状态。
        6.  **`FINAL_INSTRUCTION` -> `INIT`**: 如果故事生成后验证失败，回到 `INIT` 状态，重新生成故事。
        7.  **`FINAL_INSTRUCTION` -> `FAILED`**: 如果故事生成后，达到最大重试次数，进入 `FAILED` 状态。
      - **多轮对话控制:** 使用一个 `messages` 列表来管理对话的上下文，每次发送提示语时，将之前的对话历史也发送给 AI。
      - **用户反馈调整：** 在 `FINAL_INSTRUCTION` 状态收到 AI 的回复后，进行故事验证， 如果验证不通过， 重新回到 `INIT` 状态，重新生成故事。
    - **验证**: 实现故事的验证逻辑，包括**生词率**验证、重点**词汇**验证和**词**数验证。 计算 `new_char_rate` 和 `new_char`。
    - **实现通过 `key_word_ids` 从 `words.json` 中查找对应的 `word` 和相关信息 ( `pinyin`, `definition`, `example`)。**
3.  **调用模型层**: 服务层应调用模型层的方法来操作数据。
4.  **添加单元测试**: 在 `tests/services` 目录下创建单元测试，验证业务逻辑的正确性。

### 2.4 API 层开发

1.  **创建 API 路由**: 在 `app/api` 目录下创建 API 路由文件，例如 `word_api.py`、`scene_api.py` 和 `story_api.py`。
2.  **定义 API 接口**: 根据 `docs/api.md` 定义 API 接口的路由、请求方法、请求参数和响应格式。
    - **API 框架细节**:
      - 使用 Flask Blueprints 来组织 API 路由。
      - 使用 `request` 对象获取请求参数。
      - 使用 `jsonify` 函数返回 JSON 响应。
      - 使用装饰器来处理 API 鉴权和错误处理。
    - **故事生成 API**:
      - **URL**: `/v1/stories/generate`
      - **Method**: `POST`
      - **请求参数**: `vocabulary_level` (integer, 必填), `scene_id` (string, 必填), `story_word_count` (integer, 必填), `new_word_rate` (float, 必填), `key_word_ids` (array of string, 可选), `new_char_rate_tolerance` (float, 可选), `word_count_tolerance` (float, 可选), `story_word_count_tolerance` (integer, 可选), `request_limit` (integer, 可选)。
      - **响应**: 返回生成的 `story_id`， 以及其他故事详情。
    - **词语**查询 API**:
      - **URL**: `/v1/words`
      - **Method**: `GET`
      - **请求参数**: `level` (integer, 可选), `part_of_speech` (string, 可选), `page` (integer, 默认 1, 可选), `page_size` (integer, 默认 10, 可选)。
    - **场景管理 API**:
      - **创建场景**:
      - **URL**: `/v1/scenes`
      - **Method**: `POST`
      - **请求参数**: `name` (string, 必填), `description` (string, 必填)。
      - **获取场景**:
        - **URL**: `/v1/scenes/{scene_id}`
        - **Method**: `GET`
      - **更新场景**:
        - **URL**: `/v1/scenes/{scene_id}`
        - **Method**: `PUT`
        - **请求参数**: `name` (string, 必填), `description` (string, 必填)。
      - **删除场景**:
        - **URL**: `/v1/scenes/{scene_id}`
        - **Method**: `DELETE`
    - **故事升级/降级 API**:
      _ **URL**: `/v1/stories/{story_id}/adjust`
      _ **Method**: `POST`
      _ **请求参数**: `target_level` (integer, 必填)
      _ **注意**: `key_words` 字段暂时不提供，返回空列表。
3.  **调用服务层**: API 层应调用服务层的方法来处理请求。
4.  **处理错误**: 使用 `app/utils/error_handling.py` 中提供的 `handle_error` 函数统一处理 API 的错误，确保错误码和错误信息与 API 设计指南一致。
5.  **数据验证**: 在 API 层， 需要对输入的数据进行验证，例如: `vocabulary_level` 的取值范围， `new_word_rate` 的取值范围， **词**数范围，以及 `NEW_CHAR_RATE_TOLERANCE`, `WORD_COUNT_TOLERANCE`, `REQUEST_LIMIT` 和 `STORY_WORD_COUNT_TOLERANCE` 的值，可以使用 JSON Schema 进行验证， 确保数据类型和格式的正确性。API 请求参数的优先级高于 `.env` 文件中的配置。 **在 API 层在 API 层对 `NEW_CHAR_RATE_TOLERANCE`、`WORD_COUNT_TOLERANCE`、`REQUEST_LIMIT` 和 `STORY_WORD_COUNT_TOLERANCE` 进行类型验证**
6.  **API 鉴权示例**:

    - 使用 `app/utils/api_key_auth.py` 中提供的 API Key 认证，并使用装饰器进行 API 鉴权。

    ```python
    from functools import wraps
    from flask import request, jsonify
    from app.utils.error_handling import handle_error
    from app.config import get_api_key_from_config # 假设这个函数从配置中读取 API Key

    def api_key_required(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            api_key = request.headers.get('Authorization')
            if not api_key or not api_key.startswith('Bearer '):
                return handle_error(4011, "API Key missing")
            api_key = api_key[7:] # Remove "Bearer " prefix
            if api_key != get_api_key_from_config():
                return handle_error(4012, "Invalid API Key")
            return func(*args, **kwargs)
        return wrapper
    ```

    在 API 路由中使用 `@api_key_required` 装饰器。

    ```python
    from flask import Blueprint
    from app.utils.api_key_auth import api_key_required # 假设 api_key_required 函数在 app/utils/api_key_auth.py 中

    story_api = Blueprint('story_api', __name__, url_prefix='/v1/stories')

    @story_api.route('/generate', methods=['POST'])
    @api_key_required
    def generate_story():
        # API 代码
        pass
    ```

7.  **添加集成测试**: 在 `tests/api` 目录下创建集成测试，验证 API 接口的正确性。

### 2.5 错误处理

1.  **使用 `handle_error` 函数**: 在 API 层使用 `handle_error` 函数统一处理 API 的错误。
2.  **定义错误码**: 在 `docs/error_codes.md` 文件中定义错误码，确保错误码的清晰和准确。
3.  **添加详细的错误信息**: 确保 API 返回的错误信息清晰、具体，方便定位问题。

### 2.6 配置管理

1.  **配置 `config.py`**: 在 `app/config.py` 文件中定义项目配置，并使用 `python-dotenv` 加载 `.env` 文件中的环境变量。 **请参考 `docs/config.md` 文件，了解如何配置和使用**。
2.  **在代码中使用配置**: 使用 `app/config.py` 中的配置项。
3.  **配置文件说明**:
    - `.env` 文件存储敏感信息，例如 API Key, DeepSeek API Key， 以及一些可配置的参数（**生词率**容差值，**词**数容差值, API 请求频率限制, **词**数容差值）。
    - `config.py` 文件加载 `.env` 中的环境变量，并使用 `Config` 类来获取配置参数。
    - **重要**: `NEW_CHAR_RATE_TOLERANCE`, `WORD_COUNT_TOLERANCE`, `REQUEST_LIMIT` 和 `STORY_WORD_COUNT_TOLERANCE` 的值也可以通过 API 请求参数动态设置， API 请求参数的优先级高于 `.env` 文件中的值。 详细信息请参考 `docs/config.md`
    - **在 API 层需要对 `NEW_CHAR_RATE_TOLERANCE`、`WORD_COUNT_TOLERANCE`、`REQUEST_LIMIT` 和 `STORY_WORD_COUNT_TOLERANCE` 进行类型验证**

### 2.7 日志记录

1.  **配置 `logging`**: 使用 Python 的 `logging` 模块配置日志记录。

    ```python
    # app/__init__.py
    import logging

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    ```

2.  **在代码中使用 `logging`**: 使用 `logging.info()`, `logging.error()`, `logging.debug()` 等函数记录日志。

    ```python
    import logging

    def generate_story():
        logging.info("Start generate story")
        try:
            # 代码逻辑
            logging.info("Story generated successfully")
            return
        except Exception as e:
            logging.error(f"Error while generating story {e}")
            raise e
    ```

### 2.8 单元测试

1.  **编写单元测试**: 为每个模块编写单元测试，确保代码的每个分支都被测试到。
    - **测试驱动开发 (TDD)**： 鼓励开发人员使用测试驱动开发，先编写测试用例，再编写代码。
2.  **单元测试应该重点测试核心代码**: 例如**生词率**计算，多轮对话的逻辑，API 鉴权， 和 API 参数验证。
3.  **运行单元测试**: 使用 `pytest` 运行单元测试，确保测试通过。
4.  **生成测试覆盖率报告**: 使用 `pytest-cov` 插件生成测试覆盖率报告。

    - 安装 `pytest-cov`:

      ```bash
      pip install pytest-cov
      ```

    - 运行测试并生成报告：

      ```bash
       pytest --cov=app --cov-report term-missing
      ```

      - `--cov=app`: 指定要测试的代码目录。
      - `--cov-report term-missing`: 在终端显示测试覆盖率报告，并显示未覆盖的代码行。

5.  **提高代码覆盖率**: 努力提高单元测试的代码覆盖率，确保代码的健壮性. **单元测试应该尽量覆盖核心代码**

### 2.9 集成测试

1.  **编写集成测试**: 为每个 API 接口编写集成测试，确保 API 接口的请求参数验证、业务逻辑处理和响应格式是否正确。
2.  **运行集成测试**: 使用测试客户端 (`Flask` 提供的 `test_client`) 来模拟 API 请求，确保测试通过。

### 2.10 代码审查

1.  **代码审查**: 在代码提交之前，进行代码审查，确保代码质量。
    - **代码规范**: 遵循代码规范，例如 PEP 8。
    - **命名规范**:
      - **文件名**: 使用小写字母，单词之间使用下划线分隔，例如 `word_model.py`, `scene_service.py`。
      - **变量名**: 使用小写字母，单词之间使用下划线分隔，例如 `user_id`, `api_key`。
      - **函数名**: 使用小写字母，单词之间使用下划线分隔，例如 `get_user_info()`, `generate_story()`。
      - **类名**: 使用驼峰命名法，例如 `WordModel`, `StoryService`。
      - **常量**: 使用大写字母，单词之间使用下划线分隔，例如 `MAX_WORD_COUNT`, `DEFAULT_PAGE_SIZE`
    - **代码审查工具**: 可以使用代码审查工具，例如 `flake8`, `pylint` 等， 确保代码风格的一致性。
2.  **修复缺陷**: 根据代码审查结果，修复代码中的缺陷。

### 2.11 持续集成

1.  **配置持续集成**: 将代码集成到持续集成平台（例如 GitHub Actions），每次提交代码都自动运行测试，确保代码质量。
2.  **及时修复问题**: 及时修复持续集成平台中发现的问题。
3.  **持续集成示例**: 可以使用 GitHub Actions 来实现持续集成， 例如:

    ```yaml
    name: CI

    on:
      push:
        branches: ["main"]
      pull_request:
        branches: ["main"]

    jobs:
      build:
        runs-on: ubuntu-latest

        steps:
          - uses: actions/checkout@v3
          - name: Set up Python 3.12
            uses: actions/setup-python@v4
            with:
              python-version: "3.12"
          - name: Install dependencies
            run: |
              python -m pip install --upgrade pip3
          - name: Set up Python 3.12
            uses: actions/setup-python@v4
            with:
              python-version: "3.12"
          - name: Install dependencies
            run: |
              python -m pip install --upgrade 
              pip install -r requirements.txt
          - name: Run tests
            run: |
              pytest
    ```