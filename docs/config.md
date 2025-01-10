# 配置文档

## 1. 概述

本文档描述了中文学习平台项目中的配置管理，包括配置文件的结构、配置项的说明以及如何在代码中使用配置。本项目使用 `python-dotenv` 库加载 `.env` 文件中的环境变量，并使用 `app/config.py` 中的 `Config` 类来管理配置。

## 2. 配置文件

### 2.1 .env 文件

`.env` 文件用于存储项目的敏感信息和可配置参数，例如 API Key、DeepSeek API Key、容差值等。该文件不应提交到代码仓库，而是由每个开发者单独维护。

**示例 .env 文件内容**

```
API_KEY=your_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key
DEBUG=True
NEW_CHAR_RATE_TOLERANCE=0.1
WORD_COUNT_TOLERANCE=0.2
REQUEST_LIMIT=100
STORY_WORD_COUNT_TOLERANCE=20
# 其他配置项
```

### 2.2 app/config.py

`app/config.py` 文件定义了项目的所有配置项，并使用 `python-dotenv` 库加载 `.env` 文件中的环境变量。该文件中的值将作为配置项的默认值，实际配置值可以通过 API 请求参数进行动态设置。

**示例 app/config.py 文件内容**

```python
# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()  # 加载 .env 文件

class Config:
    # 获取 API Key
    API_KEY = os.getenv("API_KEY")
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    # 如果是开发环境，可以设置 DEBUG = True
    DEBUG = os.getenv("DEBUG", False) == "True"

    # 生字率容差值
    NEW_CHAR_RATE_TOLERANCE = float(os.getenv("NEW_CHAR_RATE_TOLERANCE", 0.1))
    # 字数容差值
    WORD_COUNT_TOLERANCE = float(os.getenv("WORD_COUNT_TOLERANCE", 0.2))
    # API 请求频率限制
    REQUEST_LIMIT = int(os.getenv("REQUEST_LIMIT", 100))

    # 故事字数容差值
    STORY_WORD_COUNT_TOLERANCE = int(os.getenv("STORY_WORD_COUNT_TOLERANCE", 20))
    
    # 加载词汇数据的路径
    WORDS_FILE_PATH = os.getenv("WORDS_FILE_PATH", "app/data/words.json")
    SCENES_FILE_PATH = os.getenv("SCENES_FILE_PATH", "app/data/scenes.json")


def get_api_key_from_config():
    return Config.API_KEY
```

## 3. 配置项说明

| 配置项                       | 类型      | 描述                                                                      | 默认值    |
| ---------------------------- | --------- | ------------------------------------------------------------------------ | --------- |
| `API_KEY`                    | `string`  | API 认证使用的 API Key，从 `.env` 文件读取, 请求头中需包含 `Authorization` 字段，值为 `Bearer <API_KEY>`                                | 无         |
| `DEEPSEEK_API_KEY`             | `string`  | 调用 DeepSeek API 使用的 API Key，从 `.env` 文件读取                           | 无         |
| `DEBUG`                      | `boolean` | 是否启用调试模式，从 `.env` 文件读取，`True` 或者 `False`                     | `False`   |
| `NEW_CHAR_RATE_TOLERANCE`      | `float`   | 生字率容差值，用于判断生成的生字率是否符合要求，可在 API 请求参数中动态设置 | `0.1`     |
| `WORD_COUNT_TOLERANCE`      | `float` | 字数容差值，用于判断生成的字数是否符合要求，可在 API 请求参数中动态设置 | `0.2`    |
| `REQUEST_LIMIT`                | `integer`| API 请求频率限制，可在 API 请求参数中动态设置                      | `100`     |
| `STORY_WORD_COUNT_TOLERANCE`       | `integer` | 故事字数容差值，用正负值表示，例如 +20 或者 -20,  可在 API 请求参数中动态设置     | `20`  |
| `WORDS_FILE_PATH`            | `string`  | 词汇数据的文件路径，用于加载字词数据                                      | `app/data/words.json`  |
| `SCENES_FILE_PATH`            | `string`  | 场景数据的文件路径，用于加载场景数据                                      |  `app/data/scenes.json` |

*   **动态设置**: `NEW_CHAR_RATE_TOLERANCE`, `WORD_COUNT_TOLERANCE`, `REQUEST_LIMIT` 和 `STORY_WORD_COUNT_TOLERANCE` 配置项的值，可以在 API 请求参数中动态设置，`.env` 中的值仅作为默认值。 **在 API 层需要对这些配置项进行类型验证，确保数据类型和取值范围的正确性**。
*   `STORY_WORD_COUNT_TOLERANCE`:  使用正负值表示容差，例如如果 `STORY_WORD_COUNT_TOLERANCE`  为 `20`，   预期字数为 100,  那么故事字数范围就在 80 ~ 120之间。

## 4. 配置使用方法

### 4.1 加载配置

1.  **安装依赖**:  确保安装了 `python-dotenv` 库。

    ```bash
    pip install python-dotenv
    ```

2.  **加载 `.env` 文件**: 在 `app/config.py` 文件中使用 `load_dotenv()` 函数加载 `.env` 文件。

    ```python
    from dotenv import load_dotenv
    load_dotenv()
    ```

3.  **使用 `Config` 类**:  在代码中使用 `Config` 类的属性来获取配置项的值。

    ```python
    from app.config import Config

    api_key = Config.API_KEY
    deepseek_key = Config.DEEPSEEK_API_KEY
    debug = Config.DEBUG
    new_char_rate_tolerance = Config.NEW_CHAR_RATE_TOLERANCE
    word_count_tolerance = Config.WORD_COUNT_TOLERANCE
    request_limit = Config.REQUEST_LIMIT
    story_word_count_tolerance = Config.STORY_WORD_COUNT_TOLERANCE
    words_file_path = Config.WORDS_FILE_PATH
    scenes_file_path = Config.SCENES_FILE_PATH
    ```

### 4.2 自定义配置

1.  **添加新的环境变量**: 在 `.env` 文件中添加新的环境变量。
2.  **在 `Config` 类中添加属性**: 在 `app/config.py` 文件中的 `Config` 类中添加对应的属性。
3.  **在代码中使用新属性**: 在代码中使用 `Config` 类的属性来获取新的配置项的值。
4. **在 API 请求中动态设置**:
    *  `NEW_CHAR_RATE_TOLERANCE`, `WORD_COUNT_TOLERANCE`, `REQUEST_LIMIT` 和 `STORY_WORD_COUNT_TOLERANCE` 的值也可以通过 API 请求参数动态设置，API 请求参数的优先级高于 `.env` 文件中的值。

## 5. 配置更新

1.  **修改 `.env` 文件**: 修改 `.env` 文件中的配置项值。
2.  **重启应用程序**:  修改 `.env` 文件后，需要重启应用程序才能使新的配置生效。

## 6. 最佳实践

*   **不要将敏感信息提交到代码仓库**:  确保 `.env` 文件不被提交到代码仓库。
*   **为配置项添加默认值**:  在 `app/config.py` 文件中为配置项添加默认值，以便在缺少环境变量时提供默认值。
*   **使用类型转换**:  使用 `int()`, `float()`, `bool()` 等函数将环境变量转换为正确的类型。
*   **为配置项添加注释**:  在 `app/config.py` 文件中为配置项添加注释，方便其他开发人员理解。
*   **验证配置项**:  **在 API 层需要对 `NEW_CHAR_RATE_TOLERANCE`, `WORD_COUNT_TOLERANCE`, `REQUEST_LIMIT` 和 `STORY_WORD_COUNT_TOLERANCE`  进行类型验证，确保数据类型和取值范围的正确性。**

