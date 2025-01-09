以下是基于上述产品需求文档规划的 **API 文档**，详细说明了 API 的设计、接口定义、请求参数、响应格式等内容。

---

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
- 请求头中需包含 `Authorization` 字段，值为 `Bearer <API_KEY>`。

### 2.3 响应格式
- 所有 API 返回的数据均为 JSON 格式。
- 通用响应结构：
  ```json
  {
    "code": "integer", // 状态码，200 表示成功
    "message": "string", // 返回信息
    "data": "object" // 返回的数据
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
    "word_count_tolerance": "integer", // 字数容差（默认±8）
    "new_char_rate": "float", // 目标生字率（0-1）
    "new_char_rate_tolerance": "float", // 生字率容差（默认±0.01）
    "key_word_ids": ["string"] // 重点词汇ID列表（UUID）
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
      "vocabulary_level": "integer", // 超童级别
      "scene": "string", // 场景ID（UUID）
      "word_count": "integer", // 故事字数
      "new_words": [
        {
          "word": "string", // 生词
          "pinyin": "string", // 拼音
          "definition": "string", // 释义
          "part_of_speech": "string", // 词性
          "example": "string" // 例句
        }
      ],
      "new_char_rate": "float", // 实际生字率
      "key_words": [
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
    "code": 400,
    "message": "Invalid parameters",
    "data": null
  }
  ```

---

### 3.2 场景管理 API
#### 3.2.1 获取场景列表
- **URL**: `/v1/scenes`
- **Method**: `GET`
- **Headers**:
  - `Authorization: Bearer <API_KEY>`
- **Query Parameters**:
  - `page`: 页码（默认1）
  - `page_size`: 每页数量（默认10）
- **响应**：
  ```json
  {
    "code": 200,
    "message": "Scenes retrieved successfully",
    "data": {
      "scenes": [
        {
          "scene_id": "string", // 场景ID（UUID）
          "name": "string", // 场景名称
          "description": "string", // 场景描述
          "created_at": "string" // 创建时间
        }
      ],
      "total": "integer" // 总场景数
    }
  }
  ```

#### 3.2.2 创建场景
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
- **响应**：
  ```json
  {
    "code": 200,
    "message": "Scene created successfully",
    "data": {
      "scene_id": "string" // 新创建的场景ID（UUID）
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
- **响应**：
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
- **响应**：
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
  - `level`: 超童级别（1-100）
  - `part_of_speech`: 词性（如“名词”）
  - `page`: 页码（默认1）
  - `page_size`: 每页数量（默认10）
- **响应**：
  ```json
  {
    "code": 200,
    "message": "Words retrieved successfully",
    "data": {
      "words": [
        {
          "word_id": "string", // 词ID（UUID）
          "word": "string", // 词
          "pinyin": "string", // 拼音
          "definition": "string", // 释义
          "part_of_speech": "string", // 词性
          "chaotong_level": "integer", // 超童级别
          "example": "string" // 例句
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
- **响应**：
  ```json
  {
    "code": 200,
    "message": "Story adjusted successfully",
    "data": {
      "story_id": "string", // 故事ID（UUID）
      "content": "string", // 更新后的故事内容
      "vocabulary_level": "integer", // 新的超童级别
      "new_char_rate": "float", // 新的生字率
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

| 错误码 | 描述                           | 详细说明                                                                 |
| ------ | ------------------------------ | ------------------------------------------------------------------------ |
| 200    | 成功                           | 请求成功，返回的数据在 `data` 字段中。                                   |
| 400    | 请求参数错误                   | 请求参数不符合预期，具体原因见 `message` 字段。                          |
| 401    | 未授权                         | 请求未提供有效的 `API Key` 或 `API Key` 无效。                           |
| 403    | 禁止访问                       | 请求的资源无权访问，通常是因为权限不足。                                 |
| 404    | 资源未找到                     | 请求的资源（如场景、字词、故事）不存在。                                 |
| 422    | 请求参数验证失败               | 请求参数格式正确，但语义不符合要求（如生字率超出范围）。                 |
| 429    | 请求过多                       | 请求频率超出限制，需等待一段时间后重试。                                 |
| 500    | 服务器内部错误                 | 服务器处理请求时发生未知错误，需联系管理员。                             |

---

### 4.1 详细错误示例

#### 4.1.1 请求参数错误（400）
- **场景**：请求参数缺少必填字段或字段类型错误。
- **示例**：
  ```json
  {
    "code": 400,
    "message": "Missing required field: 'vocabulary_level'",
    "data": null
  }
  ```

#### 4.1.2 未授权（401）
- **场景**：请求头中未提供 `Authorization` 字段，或 `API Key` 无效。
- **示例**：
  ```json
  {
    "code": 401,
    "message": "Unauthorized: Invalid API Key",
    "data": null
  }
  ```

#### 4.1.3 禁止访问（403）
- **场景**：用户无权访问请求的资源。
- **示例**：
  ```json
  {
    "code": 403,
    "message": "Forbidden: You do not have permission to access this resource",
    "data": null
  }
  ```

#### 4.1.4 资源未找到（404）
- **场景**：请求的资源（如场景、字词、故事）不存在。
- **示例**：
  ```json
  {
    "code": 404,
    "message": "Resource not found: Scene with ID '550e8400-e29b-41d4-a716-446655440000' does not exist",
    "data": null
  }
  ```

#### 4.1.5 请求参数验证失败（422）
- **场景**：请求参数格式正确，但语义不符合要求。
- **示例**：
  ```json
  {
    "code": 422,
    "message": "Validation failed: 'new_char_rate' must be between 0 and 1",
    "data": null
  }
  ```

#### 4.1.6 请求过多（429）
- **场景**：请求频率超出限制。
- **示例**：
  ```json
  {
    "code": 429,
    "message": "Too many requests: Please try again in 60 seconds",
    "data": null
  }
  ```

#### 4.1.7 服务器内部错误（500）
- **场景**：服务器处理请求时发生未知错误。
- **示例**：
  ```json
  {
    "code": 500,
    "message": "Internal server error: An unexpected error occurred",
    "data": null
  }
  ```

---

### 4.2 错误处理最佳实践
1. **明确的错误信息**：
   - 错误信息 (`message`) 应清晰、具体，帮助开发者快速定位问题。
   - 例如，`"Missing required field: 'vocabulary_level'"` 比 `"Invalid request"` 更有用。

2. **错误码分类**：
   - 使用标准的 HTTP 状态码（如 400、401、404 等）表示错误类别。
   - 在 `code` 字段中提供更细粒度的错误码（如 `4001` 表示缺少字段，`4002` 表示字段类型错误）。

3. **错误数据 (`data`) 字段**：
   - 在 `data` 字段中提供额外的错误上下文信息，例如：
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

4. **频率限制**：
   - 对于频率限制错误（429），在响应头中提供 `Retry-After` 字段，指示客户端何时可以重试。

5. **日志记录**：
   - 服务器端应记录详细的错误日志，包括请求参数、用户信息和堆栈跟踪，便于排查问题。

---

### 4.3 错误码扩展
如果需要更细粒度的错误码，可以在 HTTP 状态码的基础上扩展自定义错误码。例如：

| 错误码 | 描述                           |
| ------ | ------------------------------ |
| 4001   | 缺少必填字段                   |
| 4002   | 字段类型错误                   |
| 4003   | 字段值超出范围                 |
| 4011   | API Key 缺失                   |
| 4012   | API Key 无效                   |
| 4041   | 场景未找到                     |
| 4042   | 字词未找到                     |
| 4043   | 故事未找到                     |
| 4221   | 生字率超出范围                 |
| 4222   | 目标级别超出范围               |
| 5001   | 数据库连接失败                 |
| 5002   | 第三方服务调用失败             |

---

### 4.4 示例：扩展错误码的响应
```json
{
  "code": 4001,
  "message": "Missing required field: 'vocabulary_level'",
  "data": {
    "errors": [
      {
        "field": "vocabulary_level",
        "message": "This field is required"
      }
    ]
  }
}
```
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
    "title": "问路的故事",
    "content": "有一天，小明想去公园...",
    "vocabulary_level": 35,
    "scene": "550e8400-e29b-41d4-a716-446655440000",
    "word_count": 118,
    "new_words": [
      {
        "word": "公园",
        "pinyin": "gōngyuán",
        "definition": "public park",
        "part_of_speech": "名词",
        "example": "我们去公园玩吧。"
      }
    ],
    "new_char_rate": 0.02,
    "key_words": [
      {
        "word": "问路",
        "pinyin": "wènlù",
        "definition": "ask for directions",
        "part_of_speech": "动词",
        "example": "他向路人问路。"
      }
    ],
    "created_at": "2023-10-01T12:00:00Z"
  }
}
```

---

以上是完整的 API 文档，涵盖了所有核心功能的接口设计。