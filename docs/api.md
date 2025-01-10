好的，我将根据最新的 API 设计和数据模型更新 `api.md` 文件。以下是更新后的 `api.md` 内容：

```markdown
# API 文档

## 1. 概述

本文档描述了中文学习平台的 API 设计，包括故事生成、场景管理、字词查询、故事升级/降级等功能。所有 API 均遵循 RESTful 设计规范，数据格式为 JSON。

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
    "word_count": "integer", // 故事字数
    "new_char_rate": "float", // 目标生字率（0-1）
    "key_word_ids": ["string"] // 重点词汇ID列表（UUID），可选
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
      "word_count": "integer", // 实际故事字数
      "new_char_rate": "float", // 实际生字率
       "new_char": "integer", // 实际生字数量
      "key_words": [ // 重点词汇列表
        {
          "word": "string", // 重点词汇
          "pinyin": "string", // 拼音
          "definition": "string", // 释义
           "part_of_speech": "string", // 词性
          "example": "string" // 例句
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

#### 3.2.2 获取场景

-   **URL**: `/v1/scenes/{scene_id}`
-   **Method**: `GET`
-   **Headers**:
    -   `Authorization: Bearer <API_KEY>`
-   **响应**:

    ```json
    {
    "code": 200,
    "message": "Scene retrieved successfully",
    "data": {
        "scene_id": "string", // 场景ID（UUID）
        "name": "string", // 场景名称
        "description": "string", // 场景描述
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

---

### 3.3 字词查询 API

#### 描述

根据条件查询字词。

#### 请求

- **URL**: `/v1/words`
- **Method**: `GET`
- **Headers**:
  - `Authorization: Bearer <API_KEY>`
- **Query Parameters**:
  - `level`: 超童级别（1-100），可选
  - `part_of_speech`: 词性（如“名词”），可选
  - `page`: 页码（默认1），可选
  - `page_size`: 每页数量（默认10），可选

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
        "hsk_level": "integer", // HSK级别
        "characters": [ // 词中包含的字，以及字的词性，可选
            {
                "character": "string", // 字
                "part_of_speech": "string" // 字的词性
                }
         ]
        }
    ],
    "total": "integer" // 总词数
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
    "new_char_rate": "float", // 新的生字率
    "new_char": "integer", // 新的生字数量
    "key_words": [
      {
        "word": "string", // 重点词汇
        "pinyin": "string", // 拼音
        "definition": "string", // 释义
        "part_of_speech": "string", // 词性
        "example": "string" // 例句
      }
    ]
  }
}
```

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
  "word_count": 120,
  "new_char_rate": 0.02,
  "key_word_ids": ["550e8400-e29b-41d4-a716-446655440001"]
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
    "word_count": 13,
    "new_char_rate": 0.23,
    "new_char": 3,
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