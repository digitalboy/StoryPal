

[TOC]
    
##### 简要描述

- 根据类型和ID查询内容接口

##### 请求URL
- `http://106.52.130.188:8889/content/getContentListById/${type}/${id}`
  
##### 请求方式
- GET

##### 参数

|参数名|必选|类型|说明|
|:----    |:---|:----- |-----   |
|type |是  |int |类型：1、2 。表示 ——>  1： en_release_materia（英文绘本） 2：cn_release_material（中文绘本） |
|id |是  |string | 文章类型对应的唯一id |

##### 返回示例

```
{
    "code": 200,
    "data": {
        "paragraphs": [
            {
                "image": "http://prod.prv.muyuhuajiaoyu.com/FoV2Ube57LzBqmmyIr1Zx2E6_sbM?e=1744733045&token=B5jLjXcLuFnEaLZLa9jcDyd0fFQEYTFy2sHHetgH:BBqRzckUJg0PqckqRnfjt3Mc5cg=",
                "sequenceOrder": 0,
                "text": "想跳舞的玉米"
            },
            {
                "image": "http://prod.prv.muyuhuajiaoyu.com/Fv7eUQimwVSXjnpvni-7xRTtn9ym?e=1744733045&token=B5jLjXcLuFnEaLZLa9jcDyd0fFQEYTFy2sHHetgH:NASo_z1SEZm1v5zJNKfMjaqFgr0=",
                "sequenceOrder": 1,
                "text": "夏夜，无风无雨，繁星满天，"
            },
            {
                "image": "http://prod.prv.muyuhuajiaoyu.com/Fv7eUQimwVSXjnpvni-7xRTtn9ym?e=1744733045&token=B5jLjXcLuFnEaLZLa9jcDyd0fFQEYTFy2sHHetgH:NASo_z1SEZm1v5zJNKfMjaqFgr0=",
                "sequenceOrder": 2,
                "text": "一个与众不同的小玉米探出头来。"
            },
            {
                "image": "http://prod.prv.muyuhuajiaoyu.com/Fv7eUQimwVSXjnpvni-7xRTtn9ym?e=1744733045&token=B5jLjXcLuFnEaLZLa9jcDyd0fFQEYTFy2sHHetgH:NASo_z1SEZm1v5zJNKfMjaqFgr0=",
                "sequenceOrder": 3,
                "text": "她想：我要是会跳舞该多好啊！"
            }
        ],
        "storyId": "5e738a9dfea180771d9a9bfc",
        "storyLevel": 171,
        "storyName": "想跳舞的玉米"
    },
    "msg": "成功"
}
```

##### 返回参数说明 

|参数名|类型|说明|
|:-----  |:-----|-----                           |
|data |object   |文章列表 |
|data.storyId |string   |文章唯一id |
|data.storyLevel |int   |文章等级 |
|data.storyName |string   |文章标题 |
|data.paragraphs |list   |段落列表 |
|data.paragraphs.[n].sequenceOrder |int   |段落序号 |
|data.paragraphs.[n].image |string   |段落相关图片 |
|data.paragraphs.[n].text |string   |段落内容 |


##### 备注
根据类型和id查询出指定的文章


