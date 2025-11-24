# 原始故事AI分词处理脚本

## 概述

`tools/tokenize_original_stories.py` 是一个专门用于处理原始故事的AI分词脚本，它会调用AI服务对数据库中的原始故事进行分词处理，并将结果（包括生词列表）保存回数据库。

## 文件路径

`C:\DavidCode\StroyPal\tools\tokenize_original_stories.py`

## 脚本功能

1. **触发后台分词处理**：启动对所有原始故事的AI分词和生词计算
2. **AI分词处理**：使用指定的AI服务（如Qwen、Gemini、DeepSeek）对故事内容进行分词
3. **生词率计算**：计算每个故事的生词率和生词列表
4. **数据库更新**：将处理结果更新到PostgreSQL数据库的`original_stories`表
5. **进度监控**：实时显示处理进度

## 命令行参数

### `--ai-service`
- **类型**: 字符串
- **默认值**: "qwen"
- **可选值**: "qwen", "gemini", "deepseek"
- **作用**: 指定用于分词的AI服务

### `--start-level`
- **类型**: 整数
- **默认值**: 无（处理所有级别）
- **作用**: 指定开始处理的级别，只处理等于或高于此级别的故事

### `--end-level`
- **类型**: 整数
- **默认值**: 无（处理所有级别）
- **作用**: 指定结束处理的级别，只处理等于或低于此级别的故事

### `--force-retokenize`
- **类型**: 布尔值标志
- **默认值**: False
- **作用**: 是否强制重新分词，即使故事已经有分词内容

### `--status-interval`
- **类型**: 整数
- **默认值**: 30秒
- **作用**: 进度更新的间隔时间（秒）

## 脚本详细流程

### 1. 初始化
- 设置Python路径，以便导入项目模块
- 导入必要的模块：
  - `argparse`：处理命令行参数
  - `app.services.original_story_service.OriginalStoryService`：核心服务
  - `app.utils.literacy_calculator.LiteracyCalculator`：生词率计算器
  - `app.services.word_service.WordService`：词汇服务

### 2. 参数解析
- 解析命令行参数
- 验证参数有效性
- 显示处理配置信息

### 3. 状态检查
- 检查是否有正在运行的处理任务
- 如果有任务在运行，阻止重复启动

### 4. 启动处理
- 创建 `OriginalStoryService` 实例
- 调用 `start_processing_stories` 方法：
  - 使用指定的AI服务
  - 根据指定的级别范围过滤故事
  - 根据 `force_retokenize` 参数决定是否重新处理

### 5. 进度监控
- 循环检查处理状态
- 每隔指定时间显示进度百分比
- 支持Ctrl+C中断监控但不中断后台处理

### 6. 完成处理
- 确认所有故事处理完毕
- 显示完成信息

## 后台处理机制

### 并发处理
- 使用 `ThreadPoolExecutor` 实现多线程并发处理
- 默认使用2个工作线程
- 支持背压机制，避免数据库负载过高

### 线程安全
- 每个线程创建独立的数据库会话
- 使用 `with_for_update=True` 确保数据一致性
- 异常处理和事务回滚

### 处理逻辑
1. **分词处理**：
   - 如果故事已分词且未启用强制重分词，跳过分词
   - 否则，使用AI服务的`tokenize_prompt.txt`模板生成分词提示
   - 调用AI服务获取分词结果

2. **生词计算**：
   - 使用 `LiteracyCalculator` 计算生词率
   - 计算生词列表（`unknown_words`字段）
   - 使用全词库模式进行计算

3. **数据更新**：
   - 更新以下字段：
     - `tokenized_content`: AI分词结果
     - `word_count`: 词数
     - `unknown_word_ratio`: 生词率
     - `unknown_words`: 生词列表数组

## 数据库字段更新

处理完成后，每个原始故事在数据库中会被更新以下字段：

- `tokenized_content`：分词结果，格式如 "你好(PHR)|，|你(PRON)|好(ADJ)|。"
- `word_count`：总词数
- `unknown_word_ratio`：生词率（浮点数，如0.15表示15%）
- `unknown_words`：生词详细信息数组，包含词、词性、级别等信息

## 使用示例

### 基础用法
```bash
python tools/tokenize_original_stories.py
```

### 指定AI服务
```bash
python tools/tokenize_original_stories.py --ai-service gemini
```

### 指定处理范围
```bash
python tools/tokenize_original_stories.py --start-level 1 --end-level 50
```

### 强制重新分词
```bash
python tools/tokenize_original_stories.py --force-retokenize
```

### 完整参数示例
```bash
python tools/tokenize_original_stories.py --ai-service qwen --start-level 1 --end-level 100 --force-retokenize --status-interval 10
```

## 错误处理
- 网络请求异常处理
- 数据库事务回滚
- 线程异常处理
- 状态同步保护

## 注意事项
- 脚本运行时会启动后台线程，即使停止监控，处理仍会继续
- 需要正确的API密钥配置
- 建议在非生产环境先进行测试
- 处理大量故事可能需要较长时间