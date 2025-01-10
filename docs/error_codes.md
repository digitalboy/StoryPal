好的，这是更新后的 `error_codes.md` 文件内容：

```markdown
# 错误码说明

## 1. 概述

本文档描述了中文学习平台 API 返回的错误码。API 返回的错误码分为两部分：HTTP 状态码和扩展错误码。

## 2. HTTP 状态码

使用标准的 HTTP 状态码表示错误类别。

-   `200`: 成功
-   `400`: 请求参数错误
-   `401`: 未授权
-   `403`: 禁止访问
-   `404`: 资源未找到
-   `422`: 请求参数验证失败
-   `429`: 请求过多
-   `500`: 服务器内部错误

## 3. 扩展错误码

在 HTTP 状态码基础上，使用自定义的扩展错误码提供更详细的错误信息。

| 错误码 | 描述                           | 详细说明                                                              |
| ------ | ------------------------------ | --------------------------------------------------------------------- |
| 4001   | 缺少必填字段                   | 请求参数中缺少必要的字段。                                                |
| 4002   | 字段类型错误                   | 请求参数中的字段类型错误，例如期望整数但传入了字符串。                                |
| 4003   | 字段值超出范围                 | 请求参数中的字段值超出允许的范围，例如生字率大于 1 或小于 0。                                |
| 4011   | API Key 缺失                   | 请求头中缺少 `Authorization` 字段或 `API Key`。                                |
| 4012   | API Key 无效                   | 请求头中的 `API Key` 无效。                                               |
| 4031  | 无权限操作                    | 用户没有权限进行此操作。                                             |
| 4041   | 场景未找到                     | 请求的场景不存在。                                                  |
| 4042   | 字词未找到                     | 请求的字词不存在。                                                    |
| 4043   | 故事未找到                     | 请求的故事不存在。                                                    |
| 4221   | 生字率超出范围                 | 请求的生字率超出允许的范围 (0-1)。                                          |
| 4222   | 目标级别超出范围               | 请求的目标级别超出允许的范围 (1-100)。                                    |
| 4223  |  故事字数超出范围             |   请求的故事字数超出范围。                                               |
| 4291   | 请求过于频繁                 | 请求频率超出限制，需等待一段时间后重试。 |
| 5001   | 数据库连接失败                 | 连接数据库时发生错误。                                               |
| 5002   | 第三方服务调用失败             | 调用第三方服务时发生错误，例如 DeepSeek API 调用失败。                               |
| 5003   | 文件读取失败                  | 读取文件时发生错误，例如读取CSV文件失败。                                                  |
|5004   | 数据校验失败                   |   数据校验失败， 例如 Json Schema 验证失败。                                              |
|5005   |  未知错误             |  未知的服务器错误， 请联系管理员。                                                  |

## 4. 错误响应格式

所有 API 返回的数据均为 JSON 格式。

通用响应结构：

```json
{
  "code": "integer", // 错误码，参考上述错误码
  "message": "string", // 错误信息
  "data": "object | null" // 错误数据，一般为 null，可以用于返回更详细的错误信息
}
```

## 5. 错误处理最佳实践

1.  **明确的错误信息**：
    -   错误信息 (`message`) 应清晰、具体，帮助开发者快速定位问题。
    -   例如，`"Missing required field: 'vocabulary_level'"` 比 `"Invalid request"` 更有用。
2.  **错误码分类**：
    -   使用标准的 HTTP 状态码（如 400、401、404 等）表示错误类别。
    -   在 `code` 字段中提供更细粒度的错误码（如 `4001` 表示缺少字段，`4002` 表示字段类型错误）。
3. **详细的错误数据**：
     - 错误数据 (`data`) 字段中提供额外的错误上下文信息，例如：

        ```json
        {
          "code": 400,
          "message": "Validation failed",
          "data": {
            "errors": [
              {
                "field": "new_char_rate",
                "message": "Must be between 0 and 1"
              },
              {
                "field": "vocabulary_level",
                "message": "Must be an integer between 1 and 100"
              }
            ]
          }
        }
        ```
4.  **频率限制**：
    -   对于频率限制错误（429），在响应头中提供 `Retry-After` 字段，指示客户端何时可以重试。
5.  **日志记录**：
    -   服务器端应记录详细的错误日志，包括请求参数、用户信息和堆栈跟踪，便于排查问题。

## 6. 错误处理示例

在 `docs/api.md` 中有详细的错误处理示例。

```python
from flask import Flask, request, jsonify
from app.utils.error_handling import handle_error # 假设错误处理函数在 app/utils/error_handling.py 中

app = Flask(__name__)

@app.route('/v1/stories/generate', methods=['POST'])
def generate_story():
    try:
      data = request.get_json()
      if not data:
          return handle_error(4001, "Missing request body")

      vocabulary_level = data.get('vocabulary_level')
      scene_id = data.get('scene_id')
      word_count = data.get('word_count')
      new_char_rate = data.get('new_char_rate')
      key_word_ids = data.get('key_word_ids', [])

      if not vocabulary_level:
          return handle_error(4001, "Missing required field: 'vocabulary_level'")
      if not scene_id:
          return handle_error(4001, "Missing required field: 'scene_id'")
      if not word_count:
          return handle_error(4001, "Missing required field: 'word_count'")
      if not new_char_rate:
         return handle_error(4001, "Missing required field: 'new_char_rate'")

      if not isinstance(vocabulary_level, int):
          return handle_error(4002, "Invalid field type: 'vocabulary_level' must be an integer")
      if not isinstance(scene_id, str):
          return handle_error(4002, "Invalid field type: 'scene_id' must be a string")
      if not isinstance(word_count, int):
           return handle_error(4002, "Invalid field type: 'word_count' must be an integer")
      if not isinstance(new_char_rate, float):
          return handle_error(4002, "Invalid field type: 'new_char_rate' must be a float")

      if not 1 <= vocabulary_level <= 100:
            return handle_error(4222, "Validation failed: 'vocabulary_level' must be between 1 and 100")
      if not 0 <= new_char_rate <= 1:
            return handle_error(4221, "Validation failed: 'new_char_rate' must be between 0 and 1")

      # 调用 AI 服务生成故事
      # story_id = generate_story_from_deepseek(vocabulary_level, scene_id, word_count, new_char_rate, key_word_ids)
      story_id = "550e8400-e29b-41d4-a716-446655440002" # 示例，替换成实际的逻辑

      return jsonify({
              "code": 200,
              "message": "Story generated successfully",
             "data": {
              "story_id": story_id
                }
            })

    except Exception as e:
      return handle_error(5001, f"Internal server error: {str(e)}")


if __name__ == '__ "Story generated successfully",
             "data": {
              "story_id": story_id
                }
            })

    except Exception as e:
      return handle_error(5001, f"Internal server error: {str(e)}")


if __name__ == '__main__':
    app.run(debug=True)

```


