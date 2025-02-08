# 代码开发规范

## 1. 概述

本文档定义了中文学习平台的代码开发规范，旨在确保代码的可读性、可维护性和一致性。

## 2. 代码规范

*   **遵循代码规范**: 遵循代码规范，例如 PEP 8，确保代码的可读性。
*   **测试驱动开发 (TDD)**： 鼓励开发人员使用测试驱动开发，先编写测试用例，再编写代码。
*   **代码审查**:  在代码提交之前，进行代码审查，确保代码质量。

## 3. 命名规范

*   **文件名**:  使用小写字母，单词之间使用下划线分隔，例如 `word_model.py`, `scene_service.py`。
    *   **代码首行**: 在每个文件的首行添加注释，注明文件路径，例如：`# app/utils/literacy_calculator.py`
*   **变量名**: 使用小写字母，单词之间使用下划线分隔，例如 `user_id`, `api_key`。
*   **函数名**:  使用小写字母，单词之间使用下划线分隔，例如 `get_user_info()`, `generate_story()`。
*   **类名**:  使用驼峰命名法，例如 `WordModel`, `StoryService`。
*   **常量**: 使用大写字母，单词之间使用下划线分隔，例如  `MAX_WORD_COUNT`, `DEFAULT_PAGE_SIZE`

## 4. 代码审查工具

*   可以使用代码审查工具，例如 `flake8`, `pylint` 等， 确保代码风格的一致性。

## 5. 代码注释

*   **必要注释**: 对复杂逻辑、核心算法和重要的业务逻辑添加详细的注释。
*   **清晰易懂**: 注释应该清晰易懂，避免使用含糊不清的描述。
*   **英文注释**:  尽量使用英文注释，方便团队成员理解。

## 6. 代码结构

*   **模块化设计**:  使用模块化设计，将代码分解为不同的模块，提高代码的可重用性和可维护性。
*   **职责分离**: 每个模块应该只负责一个特定的功能，避免出现 “上帝类”。
*   **避免重复代码**: 尽量避免出现重复代码，可以使用函数或者类来封装公共逻辑。

## 7. 错误处理

*   **使用异常**:  使用 `try...except` 语句来处理异常，确保程序不会因为异常而崩溃。
*   **日志记录**: 记录错误信息，方便调试。
*   **返回统一的错误格式**: API 返回的错误信息应该符合统一的格式，方便前端处理。

## 8. 代码示例

*   **文件名**:  `# app/utils/literacy_calculator.py`

    ```python
    # app/utils/literacy_calculator.py
    import re

    class LiteracyCalculator:
        def __init__(self, word_service):
            self.word_service = word_service

        def calculate_vocabulary_rate(self, text, target_level):
            # 代码
            pass
    ```

*   **变量名**:

    ```python
    user_id = "123456"
    api_key = "abcdefg"
    ```

*   **函数名**:

    ```python
    def get_user_info(user_id):
        pass

    def generate_story(scene_id, level):
        pass
    ```

*   **类名**:

    ```python
    class WordModel:
        pass

    class StoryService:
        pass
    ```

*   **常量**:

    ```python
    MAX_WORD_COUNT = 100
    DEFAULT_PAGE_SIZE = 10
    ```