# API 文档

## 1. 概述

本文档描述了中文学习平台的 API 设计，包括故事生成、场景管理、词语查询、故事升级/降级等功能。所有 API 均遵循 RESTful 设计规范，数据格式为 JSON。

---

## 2. 基础信息

### 2.1 请求地址

- 开发环境：`https://dev.api.chinese-learning.com`
- 生产环境：`https://api.chinese-learning.com`

### 2.2 认证方式

- 所有 API 需通过 `API Key` 进行身份验证。
- `API Key` 从 `.env` 文件中读取。
- 请求头中需包含 `Authorization` 字段，值为 `Bearer <API_KEY>`。

### 2.3 响应格式

- 所有 API 返回的数据均为 JSON 格式。
- 通用响应结构：

  ```json
  {
    "code": "integer", // 状态码，200 表示成功
    "message": "string", // 返回信息
    "data": "object | null" // 返回的数据，成功时为 object，失败时为 null
  }
  ```

---

## 3. API 接口

### 3.1 故事生成 API

#### 描述

根据用户指定的参数生成符合要求的故事。

#### 请求

- **URL**: `/v1/stories/generate`
- **Method**: `POST`
- **Headers**:
  - `Authorization: Bearer <API_KEY>`
  - `Content-Type: application/json`
- **Body**:

  ```json
  {
    "vocabulary_level": "integer", // 目标词汇级别（1-100）
    "scene_id": "string", // 场景ID（UUID）
    "story_word_count": "integer", // 故事词数
    "new_word_rate": "float", // 目标生词率（0-1）
    "key_word_ids": ["string"], // 重点词汇ID列表（UUID），可选
    "new_word_rate_tolerance": "float", // 生词率容差值，可选
    "story_word_count_tolerance": "integer", // 故事字数容差值，可选
    "request_limit": "integer" // 请求频率限制，可选
  }
  ```

#### 响应

- **成功响应**（HTTP 200）：

  ```json
  {
    "code": 200,
    "message": "Story generated successfully",
    "data": {
      "story_id": "string", // 故事ID（UUID）
      "title": "string", // 故事标题
      "content": "string", // 故事内容
      "vocabulary_level": "integer", // 实际词汇级别
      "scene": "string", // 场景ID（UUID）
      "story_word_count": "integer", // 实际故事字数
      "new_word_rate": "float", // 实际生词率
      "new_words": "integer", // 实际生词数量
      "key_words": [
        // 重点词汇列表
        {
          "word": "string", // 重点词汇
          "pinyin": ["string", "null"], // 拼音
          "definition": ["string", "null"], // 释义
          "part_of_speech": "string", // 词性
          "example": ["string", "null"] // 例句
        }
      ],
      "created_at": "string" // 生成时间
    }
  }
  ```

- **错误响应**（HTTP 400）：

  ```json
  {
    "code": "integer", // 错误码，参考错误码章节
    "message": "string", // 错误信息
    "data": null
  }
  ```

---

### 3.2 场景管理 API

#### 3.2.1 创建场景

- **URL**: `/v1/scenes`
- **Method**: `POST`
- **Headers**:
  - `Authorization: Bearer <API_KEY>`
  - `Content-Type: application/json`
- **Body**:

  ```json
  {
    "name": "string", // 场景名称
    "description": "string" // 场景描述
  }
  ```

- **响应**:

  ```json
  {
    "code": 200,
    "message": "Scene created successfully",
    "data": {
      "scene_id": "string" // 新创建的场景ID（UUID）
    }
  }
  ```

  **示例**:

  - **请求**:

    ```bash
    curl -X POST https://api.chinese-learning.com/v1/scenes \
    -H "Authorization: Bearer <API_KEY>" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "问路",
        "description": "学习如何用中文问路。"
    }'
    ```

  - **响应**:

    ```json
    {
      "code": 200,
      "message": "Scene created successfully",
      "data": {
        "scene_id": "550e8400-e29b-41d4-a716-446655440000"
      }
    }
    ```

#### 3.2.2 获取场景

- **URL**: `/v1/scenes/{scene_id}`
- **Method**: `GET`
- **Headers**:
  - `Authorization: Bearer <API_KEY>`
- **响应**:

  ```json
  {
    "code": 200,
    "message": "Scene retrieved successfully",
    "data": {
      "scene_id": "string", // 场景ID（UUID）
      "name": "string", // 场景名称
      "description": "string" // 场景描述
    }
  }
  ```

  **示例**:

  - **请求**:

    ```bash
    curl -X GET https://api.chinese-learning.com/v1/scenes/550e8400-e29b-41d4-a716-446655440000 \
    -H "Authorization: Bearer <API_KEY>"
    ```

  - **响应**:

    ```json
    {
      "code": 200,
      "message": "Scene retrieved successfully",
      "data": {
        "scene_id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "问路",
        "description": "学习如何用中文问路。"
      }
    }
    ```

#### 3.2.3 更新场景

- **URL**: `/v1/scenes/{scene_id}`
- **Method**: `PUT`
- **Headers**:
  - `Authorization: Bearer <API_KEY>`
  - `Content-Type: application/json`
- **Body**:

  ```json
  {
    "name": "string", // 场景名称
    "description": "string" // 场景描述
  }
  ```

- **响应**:

  ```json
  {
    "code": 200,
    "message": "Scene updated successfully",
    "data": null
  }
  ```

**示例**: \* **请求**:

        ```bash
        curl -X PUT https://api.chinese-learning.com/v1/scenes/550e8400-e29b-41d4-a716-446655440000 \
        -H "Authorization: Bearer <API_KEY>" \
        -H "Content-Type: application/json" \
        -d '{
            "name": "新的问路",
            "description": "学习如何用中文问路 updated。"
        }'
        ```
    *   **响应**:

        ```json
        {
            "code": 200,
            "message": "Scene updated successfully",
            "data": null
         }
        ```

#### 3.2.4 删除场景

- **URL**: `/v1/scenes/{scene_id}`
- **Method**: `DELETE`
- **Headers**:
  - `Authorization: Bearer <API_KEY>`
- **响应**:

  ```json
  {
    "code": 200,
    "message": "Scene deleted successfully",
    "data": null
  }
  ```

  **示例**:

  - **请求**:
    ```bash
    curl -X DELETE https://api.chinese-learning.com/v1/scenes/550e8400-e29b-41d4-a716-446655440000 \
    -H "Authorization: Bearer <API_KEY>"
    ```
  - **响应**:

    ```json
    {
      "code": 200,
      "message": "Scene deleted successfully",
      "data": null
    }
    ```

---

### 3.3 词语查询 API

#### 描述

根据条件查询词语。

#### 请求

- **URL**: `/v1/words`
- **Method**: `GET`
- **Headers**:
  - `Authorization: Bearer <API_KEY>`
- **Query Parameters**:
  - `chaotong_level`: 超童级别（1-100），可选
  - `part_of_speech`: 词性，可选
  - `page`: 页码（默认 1），可选
  - `page_size`: 每页数量（默认 10），可选

#### 响应

```json
{
  "code": 200,
  "message": "Words retrieved successfully",
  "data": {
    "words": [
      {
        "word_id": "string", // 词ID（UUID）
        "word": "string", // 词
        "chaotong_level": "integer", // 超童级别
        "part_of_speech": "string", // 词性
        "hsk_level": "integer" // HSK级别
      }
    ],
    "total": "integer" // 总词数
  }
}
```

**示例**:

- **请求**:
  ```bash
  curl -X GET https://api.chinese-learning.com/v1/words \
  -H "Authorization: Bearer <API_KEY>" \
  -G \
  -d "level=1&part_of_speech=动词&page=1&page_size=2"
  ```
- **响应**:

  ```json
  {
    "code": 200,
    "message": "Words retrieved successfully",
    "data": {
      "words": [
        {
          "word_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
          "word": "你好",
          "chaotong_level": 1,
          "part_of_speech": "PRON",
          "hsk_level": 1
        },
        {
          "word_id": "a1b2c3d4-e5f6-7890-1234-567890abcde1",
          "word": "喜欢",
          "chaotong_level": 5,
          "part_of_speech": "v",
          "hsk_level": 2
        }
      ],
      "total": 2
    }
  }
```

---

### 3.4 故事升级/降级 API

#### 描述

对现有故事进行升级或降级。

#### 请求

- **URL**: `/v1/stories/{story_id}/adjust`
- **Method**: `POST`
- **Headers**:
  - `Authorization: Bearer <API_KEY>`
  - `Content-Type: application/json`
- **Body**:

  ```json
  {
    "target_level": "integer" // 目标级别（1-100）
  }
  ```

#### 响应

```json
{
  "code": 200,
  "message": "Story adjusted successfully",
  "data": {
    "story_id": "string", // 故事ID（UUID）
    "content": "string", // 更新后的故事内容
    "vocabulary_level": "integer", // 新的超童级别
    "new_word_rate": "float", // 新的生词率
    "new_words": "integer", // 新的生词数量
    "key_words": []
  }
}
```

**注意**: `key_words` 字段暂时不提供，返回空列表。

**示例**:

- **请求**:

  ```bash
  curl -X POST https://api.chinese-learning.com/v1/stories/550e8400-e29b-41d4-a716-446655440002/adjust \
  -H "Authorization: Bearer <API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
      "target_level": 50
  }'
  ```

- **响应**:
  `json
  {
      "code": 200,
      "message": "Story adjusted successfully",
      "data": {
          "story_id": "550e8400-e29b-41d4-a716-446655440002",
           "content": "更新后的故事内容，词汇难度升级。",
          "vocabulary_level": 50,
          "new_word_rate": 0.1,
          "new_words": 2,
          "key_words": []
      }
  }
    `

---

## 4. 错误码

详细错误码定义和错误处理最佳实践，请参考 [错误码说明文档](error_codes.md)。

---

## 5. 示例

### 5.1 生成故事

**请求**：

```bash
curl -X POST https://api.chinese-learning.com/v1/stories/generate \
-H "Authorization: Bearer <API_KEY>" \
-H "Content-Type: application/json" \
-d '{
  "vocabulary_level": 35,
  "scene_id": "550e8400-e29b-41d4-a716-446655440000",
  "story_word_count": 120,
  "new_word_rate": 0.02,
  "key_word_ids": ["550e8400-e29b-41d4-a716-446655440001"],
  "new_word_rate_tolerance": 0.1,
   "story_word_count_tolerance": 20,
    "request_limit": 100
}'
```

**响应**：

```json
{
  "code": 200,
  "message": "Story generated successfully",
  "data": {
    "story_id": "550e8400-e29b-41d4-a716-446655440002",
    "title": "小明的一天",
    "content": "小明喜欢跑步，他每天早上都会去公园跑步，他觉得很开心",
    "vocabulary_level": 30,
    "scene": "550e8400-e29b-41d4-a716-446655440000",
    "story_word_count": 13,
    "new_word_rate": 0.23,
    "new_words": 3,
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
    ],
    "created_at": "2025-01-10T14:00:00Z"
  }
}
```

## 6. 错误处理示例

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
      word_count = data.get('story_word_count')
      new_word_rate = data.get('new_word_rate')
      key_word_ids = data.get('key_word_ids', [])
       new_word_rate_tolerance = data.get('new_word_rate_tolerance')
      word_count_tolerance = data.get('word_count_tolerance')
      story_word_count_tolerance = data.get('story_word_count_tolerance')
       request_limit = data.get('request_limit')


      if not vocabulary_level:
          return handle_error(4001, "Missing required field: 'vocabulary_level'")
      if not scene_id:
          return handle_error(4001, "Missing required field: 'scene_id'")
      if not word_count:
          return handle_error(4001, "Missing required field: 'story_word_count'")
      if not new_word_rate:
         return handle_error(4001, "Missing required field: 'new_word_rate'")

      if not isinstance(vocabulary_level, int):
          return handle_error(4002, "Invalid field type: 'vocabulary_level' must be an integer")
      if not isinstance(scene_id, str):
          return handle_error(4002, "Invalid field type: 'scene_id' must be a string")
      if not isinstance(word_count, int):
           return handle_error(4002, "Invalid field type: 'story_word_count' must be an integer")
      if not isinstance(new_word_rate, float):
          return handle_error(4002, "Invalid field type: 'new_word_rate' must be a float")

      if not 1 <= vocabulary_level <= 100:
            return handle_error(4222, "Validation failed: 'vocabulary_level' must be between 1 and 100")
      if not 0 <= new_word_rate <= 1:
            return handle_error(4221, "Validation failed: 'new_word_rate' must be between 0 and 1")

       if new_word_rate_tolerance is not None and not isinstance(new_word_rate_tolerance, float):
            return handle_error(4002, "Invalid field type: 'new_word_rate_tolerance' must be a float")

       if word_count_tolerance is not None and not isinstance(word_count_tolerance, float):
            return handle_error(4002, "Invalid field type: 'word_count_tolerance' must be a float")
       if story_word_count_tolerance is not None and not isinstance(story_word_count_tolerance, int):
          return handle_error(4002, "Invalid field type: 'story_word_count_tolerance' must be a integer")

       if request_limit is not None and not isinstance(request_limit, int):
          return handle_error(4002, "Invalid field type: 'request_limit' must be a integer")

      # 重点词汇是否存在验证
      # 这里只是一个示例，假设函数check_key_word_exist() 会去数据库中验证
      if key_word_ids:
        for word_id in key_word_ids:
             if not check_key_word_exist(word_id):
                  return handle_error(5007, f"key word id {word_id} not exist")


      # 调用 AI 服务生成故事
      # story_id = generate_story_from_deepseek(vocabulary_level, scene_id, word_count, new_word_rate, key_word_ids)
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


if __name__ == '__main__':
    app.run(debug=True)
```
