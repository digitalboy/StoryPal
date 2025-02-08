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
-   `409`: 冲突
-   `422`: 请求参数验证失败
-   `429`: 请求过多
-   `500`: 服务器内部错误

## 3. 扩展错误码（取消）

- 改为详尽的错误描述

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

3.  **详细的错误数据**：
    -   错误数据 (`data`) 字段中提供额外的错误上下文信息，例如：

        ```json
        {
          "code": 400,
          "message": "Validation failed",
          "data": {
            "errors": [
              {
                "field": "new_word_rate",
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
6.  **使用 `handle_error` 函数**:
    *   在 API 层，应该使用 `app/utils/error_handling.py` 中提供的 `handle_error` 函数统一处理 API 的错误。
    *   示例:

        ```python
        from app.utils.error_handling import handle_error
        def generate_story():
            try:
                # your code
                pass
            except Exception as e:
                return handle_error(5001, f"Internal server error: {str(e)}")
        ```

## 6. 错误处理示例

在 `docs/api.md` 中有详细的错误处理示例。

