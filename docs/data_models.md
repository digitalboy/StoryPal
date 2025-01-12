好的，这是根据讨论结果更新后的 `data_models.md` 文档内容，主要添加了 `key_words` 字段的说明：

```markdown
# 数据模型

## 1. 概述

本文档定义了中文学习平台中使用的主要数据模型，包括字词数据和故事数据。所有数据均以 JSON 格式存储。

## 2. 字词数据 JSON Schema

### 描述

字词数据用于存储所有字词的信息，包括级别、词性、拼音、释义、例句等。

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
            "maximum": 100,
            "description": "超童级别"
        },
        "part_of_speech": {
            "type": "string",
            "enum": ["名词", "动词", "形容词", "副词", "语气词", "其他"],
            "description": "词性"
        },
       "hsk_level": {
            "type": "integer",
             "description": "HSK级别"
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
                    "part_of_speech": {
                         "type": "string",
                           "enum": ["名词", "动词", "形容词", "副词", "语气词", "其他"],
                         "description": "字在当前词语中的词性"
                        }
                    },
                "required": ["character"]
               },
            "description": "词语中包含的字列表"
        }
    },
    "required": ["word_id", "word", "chaotong_level", "part_of_speech", "hsk_level", "characters"]
}
```

### 示例数据

```json
{
    "word_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
    "word": "你好",
    "chaotong_level": 1,
    "part_of_speech": "其他",
     "hsk_level": 1,
    "characters": [
        {
            "character": "你",
             "part_of_speech": "PR"
         },
         {
             "character": "好",
            "part_of_speech": "ADJ"
        }
    ]
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

故事数据用于存储生成的故事的信息，包括故事ID、标题、内容、词汇级别、场景标签、生字率和重点词汇等。

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
    "new_char_rate": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "description": "实际生字率"
    },
     "new_char": {
        "type": "integer",
        "description": "实际生字数量"
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
            "enum": ["名词", "动词", "形容词", "副词", "语气词", "其他"],
             "description": "词性",
            },
          "example": {
            "type": ["string", "null"],
            "description": "例句"
          }
        },
        "required": ["word"]
      },
      "description": "重点词汇列表, **`pinyin`, `definition` 和 `example` 数据从 `words.json` 中获取**"
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "生成时间, ISO 8601 格式"
    }
  },
  "required": ["story_id", "title", "content", "vocabulary_level", "scene", "word_count", "new_char_rate", "new_char", "key_words", "created_at"]
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
  "new_char_rate": 0.05,
   "new_char": 2,
    "key_words": [
        {
            "word": "火车站",
            "pinyin": "huǒ chē zhàn",
            "definition": " train station",
             "part_of_speech": "名词",
             "example": "火车站很大。"
        }
    ],
           {
            "word": "火车站",
            "pinyin": "huǒ chē zhàn",
            "definition": " train station",
             "part_of_speech": "名词",
             "example": "火车站很大。"
        }
    ],

   "created_at": "2025-01-10T10:00:00Z"
}
```

