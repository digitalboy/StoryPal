# 数据模型

## 1. 概述

本文档定义了中文学习平台中使用的主要数据模型，包括字词表、场景数据和故事数据。所有数据均以 JSON 格式存储。

## 2. 字词表 JSON Schema

### 描述

字词表用于存储所有字词的信息，包括级别、词性、拼音、释义、例句等。

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
        "description": "词"
    },
    "pinyin": {
        "type": "string",
        "description": "拼音"
    },
    "definition": {
        "type": "string",
        "description": "释义"
    },
    "part_of_speech": {
        "type": "string",
        "enum": ["名词", "动词", "形容词", "副词", "其他"],
        "description": "词性"
    },
    "chaotong_level": {
        "type": "integer",
        "minimum": 1,
        "maximum": 100,
        "description": "超童级别"
    },
    "characters": {
            "type": "array",
            "items": {
            "type": "object",
            "properties": {
                "character": {
                "type": "string",
                "description": "字"
                },
                "pinyin": {
                "type": "string",
                "description": "拼音"
                },
                "definition": {
                "type": "string",
                "description": "释义"
                }
            },
            "required": ["character", "pinyin", "definition"]
            },
            "description": "词中包含的字"
        },
    "example": {
        "type": "string",
        "description": "例句"
    },
    "created_at": {
        "type": "string",
        "format": "date-time",
         "description": "创建时间, ISO 8601 格式"
    },
    "updated_at": {
        "type": "string",
        "format": "date-time",
        "description": "更新时间, ISO 8601 格式"
    }
    },
    "required": ["word_id", "word", "pinyin", "definition", "part_of_speech", "chaotong_level"]
}
```

### 示例数据

```json
{
    "word_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
    "word": "你好",
    "pinyin": "nǐ hǎo",
    "definition": "你好",
    "part_of_speech": "其他",
    "chaotong_level": 1,
     "characters": [
        {
            "character": "你",
            "pinyin": "nǐ",
            "definition": "你"
         },
         {
             "character": "好",
             "pinyin": "hǎo",
            "definition": "好"
        }
    ],
    "example": "你好，世界！",
    "created_at": "2025-01-10T08:00:00Z",
    "updated_at": "2025-01-10T08:00:00Z"
}
```

## 3. 场景数据 JSON Schema

### 描述

场景数据用于存储场景的信息，包括场景ID、名称和描述。

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
    },
    "created_at": {
      "type": "string",
       "format": "date-time",
      "description": "创建时间, ISO 8601 格式"
    },
    "updated_at": {
      "type": "string",
       "format": "date-time",
      "description": "更新时间, ISO 8601 格式"
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
    "description": "学习如何用中文问路。",
    "created_at": "2025-01-10T09:00:00Z",
    "updated_at": "2025-01-10T09:00:00Z"
}
```

## 4. 故事数据 JSON Schema

### 描述

故事数据用于存储生成的故事的信息，包括故事ID、标题、内容、词汇级别、场景标签、生词列表、生字率和重点词汇等。

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
      "maximum": 100,
      "description": "超童级别"
    },
    "scene": {
      "type": "string",
      "format": "uuid",
      "description": "场景ID，使用UUID"
    },
    "word_count": {
      "type": "integer",
      "description": "故事字数"
    },
    "new_words": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "word": {
            "type": "string",
            "description": "生词"
          },
          "pinyin": {
            "type": "string",
            "description": "拼音"
          },
          "definition": {
            "type": "string",
            "description": "释义"
          },
          "part_of_speech": {
            "type": "string",
            "enum": ["名词", "动词", "形容词", "副词", "其他"],
            "description": "词性"
           },
          "example": {
            "type": "string",
            "description": "例句"
          }
        },
        "required": ["word", "pinyin", "definition"]
      },
      "description": "生词列表"
    },
    "new_char_rate": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "description": "实际生字率"
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
            "type": "string",
            "description": "拼音"
          },
          "definition": {
            "type": "string",
            "description": "释义"
          },
          "part_of_speech": {
            "type": "string",
            "enum": ["名词", "动词", "形容词", "副词", "其他"],
             "description": "词性"
            },
          "example": {
            "type": "string",
            "description": "例句"
          }
        },
        "required": ["word", "pinyin", "definition"]
      },
      "description": "重点词汇列表"
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "生成时间, ISO 8601 格式"
    }
  },
  "required": ["story_id", "content", "vocabulary_level", "scene"]
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
  "word_count": 40,
    "new_words": [
        {
            "word": "火车站",
            "pinyin": "huǒ chē zhàn",
            "definition": "train station",
             "part_of_speech": "名词",
             "example": "火车站很大。"

        },
         {
            "word": "一直",
            "pinyin": "yì zhí",
            "definition": "straight",
             "part_of_speech": "副词",
             "example": "你一直走。"
        },
         {
             "word": "左转",
             "pinyin": "zuǒ zhuǎn",
            "definition": "turn left",
            "part_of_speech": "动词",
             "example": "在下一个路口左转。"
        }
    ],
  "new_char_rate": 0.05,
    "key_words": [
        {
            "word": "火车站",
            "pinyin": "huǒ chē zhàn",
            "definition": "train station",
            "part_of_speech": "名词",
             "example": "火车站很大。"
        }
    ],
   "created_at": "2025-01-10T10:00:00Z"
}
```


