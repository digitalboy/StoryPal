# 返回数据要求

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "故事结构 Schema",
  "type": "object",
  "properties": {
    "storyId": {
      "type": "integer",
      "description": "故事的唯一标识符。例如：123",
      "examples": [123, 456]
    },
    "storyName": {
      "type": "string",
      "description": "故事的标题或名称。例如：小红帽",
      "examples": ["小红帽", "三只小猪"]
    },
    "storyLevel": {
      "type": "integer",
      "description": "故事的难度级别，用整数表示。例如：1表示简单，3表示困难。",
      "examples": [1, 2, 3]
    },
    "paragraphs": {
      "type": "array",
      "description": "故事段落的数组。",
      "items": {
        "type": "object",
        "properties": {
          "sequenceOrder": {
            "type": "integer",
            "description": "段落在故事中的序列编号，保证顺序正确。",
            "examples": [1, 2, 3]
          },
          "text": {
            "type": "string",
            "description": "段落的文本内容。例如：从前，有一个小女孩叫小红帽。",
            "examples": ["从前，有一个小女孩叫小红帽。", "他们高兴地生活在一起。"]
          },
          "image": {
            "type": ["string", "null"],
            "format": "uri",
            "description": "与段落关联的图片URL。允许为空。例如：http://example.com/redhat.jpg，或 null。",
            "examples": ["http://example.com/redhat.jpg", null]
          }
        },
        "required": [
          "sequenceOrder",
          "text"
        ]
      }
    }
  },
  "required": [
    "storyId",
    "storyName",
    "storyLevel",
    "paragraphs"
  ]
}
```

## 数据样例

```json
{
  "storyId": 1001,
  "storyName": "小红帽",
  "storyLevel": 100,
  "paragraphs": [
    {
      "sequenceOrder": 1,
      "text": "从前，有一个可爱的小女孩，名叫小红帽。",
      "image": "http://example.com/redhat1.jpg"
    },
    {
      "sequenceOrder": 2,
      "text": "有一天，妈妈让她给生病的外婆送去一些食物。",
      "image": "http://example.com/redhat2.jpg"
    },
    {
      "sequenceOrder": 3,
      "text": "在森林里，小红帽遇到了大灰狼。",
      "image": "http://example.com/redhat3.jpg"
    },
    {
      "sequenceOrder": 4,
      "text": "大灰狼先一步跑到了外婆家，并把外婆藏了起来。",
      "image": "http://example.com/redhat4.jpg"
    },
        {
      "sequenceOrder": 5,
      "text": "小红帽来到了外婆家，发现外婆的样子有些奇怪。",
      "image": null
    },
    {
      "sequenceOrder": 6,
      "text": "最终，猎人赶来，救出了小红帽和外婆。",
      "image": "http://example.com/redhat5.jpg"
    }
  ]
}

```