# 数据模型

## 1. 概述

本文档定义了中文学习平台中使用的主要数据模型，包括词语数据和故事数据。所有数据均以 JSON 格式存储。

## 2. 词语数据 JSON Schema

### 描述

词语数据用于存储所有词语的信息，包括级别、词性等。

### JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "word_id": {
      "type": "string",
      "format": "uuid",
      "description": "词唯一ID，使用UUID"
    },
    "word": {
      "type": "string",
      "description": "词语"
    },
    "chaotong_level": {
      "type": "integer",
      "minimum": 1,
      "maximum": 853,
      "description": "超童级别"
    },
    "hsk_level": {
      "type": ["number", "null"],
      "description": "HSK级别，可以是浮点数或空值"
    },
    "part_of_speech": {
      "type": "string",
      "enum": [
        "N",
        "V",
        "ADJ",
        "ADV",
        "NUM",
        "QTY",
        "PRON",
        "AUX",
        "CONJ",
        "PHR",
        "INT",
        "PN",
        "IDIOM",
        "PREP"
      ],
      "description": "词性"
    }
  },
  "required": [
    "word_id",
    "word",
    "chaotong_level",
    "hsk_level",
    "part_of_speech"
  ]
}
```

### 示例数据

```json
{
  "word_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
  "word": "你好",
  "chaotong_level": 1,
  "hsk_level": 1,
  "part_of_speech": "PRON"
}
```

## 3. 场景数据 JSON Schema

### 描述

场景数据用于存储场景的信息，包括场景 ID、名称和描述。

### JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "scene_id": {
      "type": "string",
      "format": "uuid",
      "description": "场景唯一ID，使用UUID"
    },
    "name": {
      "type": "string",
      "description": "场景名称"
    },
    "description": {
      "type": "string",
      "description": "场景描述"
    }
  },
  "required": ["scene_id", "name", "description"]
}
```

### 示例数据

```json
{
  "scene_id": "f0e9d8c7-b6a5-4321-9876-543210fedcba",
  "name": "问路",
  "description": "学习如何用中文问路。"
}
```

## 4. 故事数据 JSON Schema

### 描述

故事数据用于存储生成的故事的信息，包括故事 ID、标题、内容、词汇级别、场景标签、生词率和重点词汇等。

### JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "story_id": {
      "type": "string",
      "format": "uuid",
      "description": "故事唯一ID，使用UUID"
    },
    "title": {
      "type": "string",
      "description": "故事标题"
    },
    "content": {
      "type": "string",
      "description": "故事内容"
    },
    "vocabulary_level": {
      "type": "integer",
      "minimum": 1,
      "maximum": 853,
      "description": "超童级别"
    },
    "scene": {
      "type": "string",
      "format": "uuid",
      "description": "场景ID，使用UUID"
    },
    "story_word_count": {
      "type": "integer",
      "description": "故事词数"
    },
    "new_word_rate": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "description": "实际生词率"
    },
    "new_words": {
      "type": "integer",
      "description": "实际生词数量"
    },
    "key_words": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "word": {
            "type": "string",
            "description": "重点词汇"
          },
          "pinyin": {
            "type": ["string", "null"],
            "description": "拼音"
          },
          "definition": {
            "type": ["string", "null"],
            "description": "释义"
          },
          "part_of_speech": {
            "type": "string",
            "enum": [
              "N",
              "V",
              "ADJ",
              "ADV",
              "NUM",
              "QTY",
              "PRON",
              "AUX",
              "CONJ",
              "PHR",
              "INT",
              "PN",
              "IDIOM",
              "PREP"
            ],
            "description": "词性"
          },
          "example": {
            "type": ["string", "null"],
            "description": "例句"
          }
        },
        "required": ["word"]
      },
      "description": "重点词汇列表"  //  去掉 **`pinyin`, `definition` 和 `example` 数据从 `words.json` 中获取**
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "生成时间, ISO 8601 格式"
    }
  },
  "required": [
    "story_id",
    "title",
    "content",
    "vocabulary_level",
    "scene",
    "story_word_count",
    "new_word_rate",
    "new_words",
    "key_words",
    "created_at"
  ]
}
```

### 示例数据

```json
{
  "story_id": "1a2b3c4d-5e6f-7890-1234-567890abcdef",
  "title": "小明问路",
  "content": "小明想去火车站，他问：“请问火车站怎么走？”一位阿姨说：“你一直往前走，然后左转就到了。”",
  "vocabulary_level": 35,
  "scene": "f0e9d8c7-b6a5-4321-9876-543210fedcba",
  "story_word_count": 40,
  "new_word_rate": 0.05,
  "new_words": 2,
  "key_words": [
    {
      "word": "火车站",
      "pinyin": "huǒ chē zhàn",
      "definition": " train station",
      "part_of_speech": "N",
      "example": "火车站很大。"
    }
  ],
  "created_at": "2025-01-10T10:00:00Z"
}
```

