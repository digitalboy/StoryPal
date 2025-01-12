# 提示语工程

## 1. 概述

本文档描述了中文学习平台中使用的提示语 (prompt) 工程，包括提示语的设计原则、模板结构、动态生成方法、多轮对话策略以及最佳实践。提示语的设计直接影响 AI 生成的故事质量，因此至关重要。

## 2. 提示语设计原则

在设计提示语时，应遵循以下原则：

*   **清晰 (Clarity)**：提示语必须清晰明确，避免歧义。使用简洁的语言描述需求，让 AI 能够准确理解您的意图。
*   **具体 (Specificity)**：提示语应该包含具体的细节，例如故事的场景、目标词汇级别、故事字数、目标生字率和必须包含的重点词汇。
*   **简洁 (Brevity)**：提示语应该尽可能简洁，避免冗余的信息。不要给 AI 过多的限制，让 AI 有一定的创作空间。
*   **可控性 (Controllability)**：提示语应该能够控制 AI 生成的故事的风格和内容。例如，可以使用特定的词汇或句式来引导 AI 的创作方向。
*   **可扩展性 (Extensibility)**：提示语应该具有良好的可扩展性，方便后续添加新的需求。

## 3. 提示语模板结构

为了方便提示语的管理和维护，我们使用 Jinja2 模板引擎来动态生成提示语。为了实现多轮对话， 我们使用不同的模板。

### 3.1 初始提示语模板

```text
你是一个专业的中文故事生成器，你的目标是根据用户的中文水平，生成一个有趣、易懂的故事。

请注意以下要求：
1.  故事应该发生在：{scene_description}
2.  故事应该使用适合 {vocabulary_level} 级别的词汇， 目标生字率在 {new_char_rate} 左右。 请注意控制故事的生字率 (`new_char_rate`) 和 生字数量 (`new_char`)。
3.  故事的字数应该在 {word_count_min} 到 {word_count_max} 字之间。
4.  故事中必须包含以下重点词汇:
        {key_words}
5.  请以 JSON 格式返回生成的故事，包括 `title`，`content`, 和 `key_words` 字段。 JSON Schema 如下:
        {
           "type": "object",
           "properties": {
                "title": {"type": "string"},
                 "content": {"type": "string"},
                "key_words": {
                  "type": "array",
                  "items": {
                    "type": "object",
                    "properties": {
                        "word": {"type": "string"},
                        "pinyin": {"type": ["string", "null"]},
                       "definition": {"type": ["string", "null"]},
                      "part_of_speech": {"type": "string",  "enum": ["名词", "动词", "形容词", "副词", "语气词", "其他"]},
                      "example": {"type": ["string", "null"]}
                     },
                    "required": ["word"]
                    }
                   }
               },
             "required": ["title", "content", "key_words"]
        }
6. 请参考以下示例：

    **正确的示例**:
        ```json
        {
            "title": "小明的一天",
             "content": "小明喜欢跑步，他每天早上都会去公园跑步，他觉得很开心",
             "key_words": [
                {
                    "word": "喜欢",
                    "pinyin": null,
                    "definition": null,
                     "part_of_speech": "v",
                    "example": null
                  },
                  {
                    "word": "跑步",
                    "pinyin": null,
                    "definition": null,
                      "part_of_speech": "v",
                    "example": null
                }
                ]
        }
        ```
    **错误的示例**:
         ```json
        {
            "title": "错误的故事",
            "content": "This is a English story. not a Chinese story.  你好世界",
             "key_words": []
        }
        ```

请注意故事的流畅性和自然性，并确保符合以上所有要求。
```

### 3.2 提供已知词汇模板

```text
以下是一些已知词汇，你可以参考：
{known_words}
```

*   `{known_words}`:  JSON 格式的已知词汇列表。

### 3.3 最终指令模板

```text
请你根据以上需求，编写故事。
```

## 4. 动态生成提示语

使用 Jinja2 模板引擎动态生成提示语的步骤如下：

1.  **加载模板**: 从文件中加载提示语模板。

    ```python
    from jinja2 import Template

    def load_prompt_template(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            return Template(f.read())
    ```

2.  **准备数据**:  从 API 请求参数、`scene.json` 和 `word.json` 中获取数据。
3.  **渲染模板**: 将数据传递给 Jinja2 模板进行渲染。

    ```python
    def render_prompt(template, data):
         return template.render(data)
    ```

4.  **生成提示语**: 返回渲染后的提示语字符串。

    ```python
    template_path = "path/to/your/prompt_template.txt"
    template = load_prompt_template(template_path)

    data = {
        "scene_description": "一个关于日常生活的场景。",
        "vocabulary_level": 30,
        "word_count": 100,
        "new_char_rate": 0.2,
        "key_words": ["喜欢", "跑步"]
    }
    prompt = render_prompt(template, data)
    print(prompt)
    ```

## 5. 多轮对话策略

为了更好地引导 AI 生成故事，我们采用多轮对话策略。

1.  **第一轮对话 (初始提示语)**:
    *   使用 **初始提示语模板**，提供故事场景、目标词汇级别、字数范围、目标生字率、重点词汇等基本要求，并明确 AI 的角色和目标。
    *  明确要求 AI 返回 JSON 格式数据， 包括 `title`，`content`，和 `key_words`。
    *  **提示 AI 生成故事时，注意 `new_char_rate` 和 `new_char`。**

2.  **第二轮对话 (提供已知词汇)**:
    *   根据 `vocabulary_level` 加载已知词汇列表。
    *   如果已知词汇数量过多，可以选择分批次提供，或者只提供一定数量的示例。
    *   使用 **提供已知词汇模板**，将已知词汇列表添加到第二轮提示语中。
     *  在第二轮提示语中，如果重点词汇在已知词汇中， 可以适当调整重点词汇列表，确保故事包含一些新的挑战。

3.  **第三轮对话 (如果需要)**:
     *   **如果第二轮仍然提供太多的已知词汇， 可以进一步分割，分多轮提供**
     *  **根据第二轮的反馈**， 调整提示语， 例如：“请你注意，上轮提供的已知词汇不是所有都要使用， 只是供你参考。”

4.  **最终指令**:
    *   在最后一轮，给 AI 一个最终指令: `"请你根据以上需求，编写故事。"`
5.  **DeepSeek API 的使用**:
    *   **上下文管理**: 使用 `messages` 列表来管理对话上下文，在每轮对话后，将 AI 的回复添加到 `messages` 列表中。
    *   **调用 API**:  使用 `client.chat.completions.create` 函数调用 DeepSeek API。
6.  **故事验证**:
    *   在最后一轮对话后，使用我们之前的验证逻辑（包括生字率验证、重点词汇验证和字数验证）验证 AI 生成的故事。
7.  **JSON 写入**:
    *   如果验证通过， 构建符合规范的 JSON 响应， 添加 `new_char_rate` 和 `new_char`。
    *  **多轮对话的流程使用状态机进行管理， 根据用户的反馈动态调整对话策略**

     *   **状态机:**  使用一个简单的状态枚举来表示对话状态，例如 `INIT`, `PROVIDE_KNOWN_WORDS`, `FINAL_INSTRUCTION`。
        *   **对话策略：**
            1.  **`INIT` 状态**: 发送初始提示语模板。
            2.  **`PROVIDE_KNOWN_WORDS` 状态**:  根据 `vocabulary_level` 加载已知词汇，并添加到提示语中。
            3.  **`FINAL_INSTRUCTION` 状态**:  发送最终指令，并等待 AI 生成故事。
            4.  **状态转移**: 根据 AI 的回复和用户的反馈，进行状态转移。例如，在 `INIT` 状态收到回复后，转移到 `PROVIDE_KNOWN_WORDS` 状态。在 `PROVIDE_KNOWN_WORDS` 状态收到回复后，转移到 `FINAL_INSTRUCTION` 状态。
        *   **多轮对话控制:** 使用一个 `messages` 列表来管理对话的上下文，每次发送提示语时，将之前的对话历史也发送给 AI。
        *  **用户反馈调整：** 在 `FINAL_INSTRUCTION` 状态收到 AI 的回复后，进行故事验证， 如果验证不通过， 重新回到 `INIT` 状态，重新生成故事。

## 6. 最佳实践

### 6.1 控制故事风格

*   **添加风格引导**: 在提示语中添加一些风格引导，例如：
    *   “请用幽默风趣的语言生成故事。”
    *   “请用简洁明了的语言生成故事。”
    *   “请用生动形象的语言生成故事。”

### 6.2 控制故事内容

*   **添加主题引导**: 在提示语中添加一些主题引导，例如：
    *   “请生成一个关于友谊的故事。”
    *   “请生成一个关于旅行的故事。”
    *   “请生成一个关于学习的故事。”
*   **添加内容限制**: 可以添加一些内容限制， 例如：
    *   “故事中不能出现敏感内容”
    *   “故事的内容应该符合逻辑”
    *   “故事的结尾应该开放式”
    *   “故事应该包含悬念”

### 6.3 多次尝试与调整

*   **迭代优化**:  如果 AI 生成的故事不符合要求，可以尝试调整提示语，多次调用 AI 服务，直到生成的故事满足所有条件。
*   **记录每次尝试的提示语和生成的故事**: 方便后续分析和优化。

### 6.4 提示语的维护与管理

*   **模块化**:  将提示语模板存储在单独的文件中，方便维护和管理。
*   **版本控制**: 使用 Git 进行提示语模板的版本控制。
*   **动态配置**: 提示语的参数应该可以动态配置，例如：偏差范围，词汇级别等。
*   **根据用户反馈进行调整**:  根据用户反馈，不断优化提示语。

## 7. 总结

提示语工程是控制 AI 生成故事质量的关键。通过遵循清晰、具体、简洁和可控的设计原则，使用动态的模板引擎，多轮对话策略，**使用状态机管理对话流程**，并结合多次尝试和迭代优化，我们可以生成高质量的故事，满足用户的需求。
