# 故事生成 API 说明

## 1. 接口描述

*   **接口名称：** 生成故事
*   **接口路径：** `/api/v1/stories/generate`
*   **请求方法：** POST
*   **Content-Type：** application/json
*   **身份验证：** 需要 API Key 认证 (Authorization: Bearer <API_KEY>)
*   **描述：**  该接口用于根据指定的参数， 使用 AI 模型生成中文故事。

## 2. 请求参数

```json
{
    "vocabulary_level": 58,       #  (必填) 词汇级别 (1-300)， 表示故事所针对的中文水平级别。
    "scene_id": "f0e9d8c7-b6a5-4321-9876-543210fedcbb", #  (必填) 场景 ID， UUID 格式。
    "story_word_count": 30,      #  (必填) 故事的词数。
    "new_word_rate": 0.1,         #  (必填) 故事的生词率 (0-1)。
    "key_word_ids": [            #  (可选) 故事中必须包含的重点词汇 ID 列表， UUID 格式。
        "6b302c64-8d4b-49af-bc89-8022bddfa878",
        "3dee9178-2f8a-41da-8683-a25e6563c678"
    ],
    "new_word_rate_tolerance": 0.1, #  (可选) 生词率容忍度。
    "story_word_count_tolerance": 10, #  (可选) 故事词数容忍度。
    "ai_service": "gemini",       #  (可选) 指定使用的 AI 服务， 默认为 "deepseek"， 可选 "gemini"。
    "multiplier": 1.2             #  (可选) 字数倍率，用于限制故事的最大字数， 默认为 1.2。
}
```

*   **参数说明：**

    *   `vocabulary_level`： 整数， 必填。  表示故事所针对的中文水平级别， 取值范围为 1 到 300。
    *   `scene_id`： 字符串， 必填。  场景 ID， 必须是有效的 UUID 格式。
    *   `story_word_count`： 整数， 必填。  故事的词数。
    *   `new_word_rate`： 浮点数， 必填。  故事的生词率， 取值范围为 0 到 1。
    *   `key_word_ids`： 字符串列表， 可选。  故事中必须包含的重点词汇 ID 列表， 列表中的每个元素都必须是有效的 UUID 格式。
    *   `new_word_rate_tolerance`： 浮点数， 可选。 生词率容忍度。
    *   `story_word_count_tolerance`： 整数， 可选。 故事词数容忍读。
    *   `ai_service`： 字符串， 可选。 指定使用的 AI 服务， 默认为 "deepseek"， 可选 "gemini"。
    *   `multiplier`： 数值型， 可选。  字数倍率，用于限制故事的最大字数， 默认为 1.2。 实际计算公式为 `max_word_count = int(known_word_count * multiplier)`，  其中 `known_word_count` 为指定 `vocabulary_level` 下的已知词汇数量。

*   **参数验证：**

    *   如果缺少必填参数， 返回 400 错误， 并提示缺少哪些参数。
    *   如果参数类型不正确， 返回 400 错误， 并提示参数类型错误。
    *   如果参数取值范围不正确， 返回 400 错误， 并提示参数取值范围错误。
    *   如果 `key_word_ids` 中的词汇 ID 不属于指定的 `vocabulary_level`， 返回 400 错误， 并提示哪些词汇 ID 不属于指定的词汇级别。
    *   如果 `multiplier` 的类型不是数值型， 返回 400 错误， 并提示 `multiplier` 必须是数值型。
    *   如果 `story_word_count` 超过了基于 `vocabulary_level` 和 `multiplier` 计算出的最大字数限制， 返回 400 错误， 并提示 "字数要求过多"。

## 3. 返回结果

```json
{
    "code": 200,
    "message": "Story generated successfully",
    "data": {
        "story_id": "17aeb8c4-ff7c-4bb7-9735-e71dbcbcfbfc",    # 故事 ID， UUID 格式。
        "title": "请问怎么走？",       # 故事标题。
        "content": "你好(PHR) |，|请问(V) |，|去(V) |火车站(N) |怎么(PRON) |走(V) |？|我(PRON) |不(ADV) |知道(V) |。|你(PRON) |可以(ADJ) |告诉(V) |我(PRON) |吗(AUX) |？|谢谢(PHR) |！|前面(N) |一直(ADV) |走(V) |，|然后(CONJ) |往(PREP) |左(N) |拐(V), |你(PRON) |会(V) |看见(V) |一个(NUM) |商店(N)。|**突然(ADV)** |，|你(PRON) |的(AUX) |朋友(N) |**离开(V)** |了(AUX) |。",  # 故事内容， 使用 "|" 分割词语， 使用 "()" 标注词性。
        "vocabulary_level": 100,    # 词汇级别。
        "scene_id": "f0e9d8c7-b6a5-4321-9876-543210fedcbb",   # 场景 ID。
        "scene_name": "问路",        # 场景名称。
        "word_count": 33,          # 故事的词数。
        "new_word_rate": 0.15151515151515152, # 故事的生词率。
        "key_words": [             # 故事中包含的重点词汇列表。
            {
                "part_of_speech": "ADV", # 词性。
                "word": "突然"      # 词语。
            },
            {
                "part_of_speech": "V",
                "word": "离开"
            }
        ],
        "unknown_words": [        # 故事中的生词列表。
            {
                "level": 133,      # 词汇级别， 如果词汇不存在于词汇表中， 则为 null。
                "pos": "CONJ",       # 词性。
                "word": "然后"        # 词语。
            },
            {
                "level": null,
                "pos": "V,",
                "word": "拐"
            }
        ],
        "created_at": "2025-03-04T04:30:03.712653+00:00"  # 故事创建时间。
    }
}
```

*   **返回结果说明：**

    *   `code`： 整数， 200 表示成功， 其他值表示失败。
    *   `message`： 字符串， 返回结果的描述信息。
    *   `data`： JSON 对象， 包含生成的故事内容， 字段说明见上表。

*   **错误码说明：**

    *   `400`： 请求参数错误。
    *   `401`： 未授权 (API Key 缺失或无效)。
    *   `500`： 服务器内部错误。

## 4. 示例

*   **请求示例：**

```json
{
    "vocabulary_level": 58,
    "scene_id": "f0e9d8c7-b6a5-4321-9876-543210fedcbb",
    "story_word_count": 30,
    "new_word_rate": 0.1,
    "key_word_ids": [
        "6b302c64-8d4b-49af-bc89-8022bddfa878",
        "3dee9178-2f8a-41da-8683-a25e6563c678"
    ],
    "new_word_rate_tolerance": 0.1,
    "story_word_count_tolerance": 10,
    "ai_service": "gemini",
    "multiplier": 1.2
}
```

*   **成功响应示例：**

```json
{
  "code": 200,
  "message": "Story generated successfully",
  "data": {
    "story_id": "17aeb8c4-ff7c-4bb7-9735-e71dbcbcfbfc",
    "title": "请问怎么走？",
    "content": "你好(PHR) |，|请问(V) |，|去(V) |火车站(N) |怎么(PRON) |走(V) |？|我(PRON) |不(ADV) |知道(V) |。|你(PRON) |可以(ADJ) |告诉(V) |我(PRON) |吗(AUX) |？|谢谢(PHR) |！|前面(N) |一直(ADV) |走(V) |，|然后(CONJ) |往(PREP) |左(N) |拐(V), |你(PRON) |会(V) |看见(V) |一个(NUM) |商店(N)。|**突然(ADV)** |，|你(PRON) |的(AUX) |朋友(N) |**离开(V)** |了(AUX) |。",
    "vocabulary_level": 100,
    "scene_id": "f0e9d8c7-b6a5-4321-9876-543210fedcbb",
    "scene_name": "问路",
    "word_count": 33,
    "new_word_rate": 0.15151515151515152,
    "key_words": [
      {
        "part_of_speech": "ADV",
        "word": "突然"
      },
      {
        "part_of_speech": "V",
        "word": "离开"
      }
    ],
    "unknown_words": [
      {
        "level": 133,
        "pos": "CONJ",
        "word": "然后"
      },
      {
        "level": null,
        "pos": "V,",
        "word": "拐"
      }
    ],
    "created_at": "2025-03-04T04:30:03.712653+00:00"
  }
}
```

*   **错误响应示例：**

```json
{
    "code": 400,
    "message": "Missing required field: 'vocabulary_level'",
    "data": null
}
```

```json
{
    "code": 400,
    "message": "Invalid field type: 'vocabulary_level' must be an integer",
    "data": null
}
```

```json
{
    "code": 400,
    "message": "字数要求过多",
    "data": null
}
```

## 5. 注意事项

*   请确保您的 API Key 是有效的。
*   请仔细阅读请求参数说明， 并按照要求传递参数。
*   如果遇到问题， 请查看错误码说明， 并根据错误信息进行排查。


