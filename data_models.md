# 数据模型与持久化分析

本文档旨在详细分析项目当前的数据模型设计、持久化机制以及它们在服务层中的应用。

## 1. 整体架构概述

项目目前采用了一种**基于 SQLAlchemy ORM 和 PostgreSQL 数据库**的现代化架构。其核心思想如下：

1.  **模型定义**: 在 `app/models/` 目录下，通过 SQLAlchemy ORM 类定义了应用的核心数据实体（如 `Word`, `Scene`, `Story`）。这些类不仅包含数据属性，还通过关系映射实现表间关联。
2.  **数据持久化**: 所有数据存储在 PostgreSQL 数据库中。每个模型类对应数据库中的一张表，通过 SQLAlchemy ORM 进行数据操作。
3.  **数据访问**: 服务（Services）通过 SQLAlchemy Session 与数据库交互，执行查询、更新等操作，无需将数据加载到内存中。
4.  **业务操作**:
    - **读操作**: 如查询、过滤等，通过 SQLAlchemy 查询接口直接从数据库获取。
    - **写操作**: 如创建、更新、删除，通过 SQLAlchemy Session 将变更持久化到数据库。

数据库连接通过 `app/database.py` 中的 `SessionLocal` 进行管理，为服务层提供了统一的持久化接口。

**数据流**:
`API 层 -> 服务层 -> (数据库操作) -> SQLAlchemy Session -> PostgreSQL 数据库`

这种架构具备生产环境所需的性能、并发和数据一致性能力，支持大规模应用。

## 2. 核心数据模型详解

所有模型都继承自 `BaseModel`，以获得统一的 ID 和时间戳处理能力。

### 2.1 `BaseModel` (`app/models/base_model.py`)

作为所有模型的基类，它提供了两个核心功能：

- **`id`**: 自动生成的 UUID (`uuid.uuid4()`)，作为每个实例的唯一标识。
- **`created_at`**: 自动生成的 UTC 时间戳 (ISO 8601 格式)，记录创建时间。
- **`to_dict()`**: 将模型实例序列化为字典，方便写入 JSON。
- **`from_dict()`**: 类方法，从字典创建模型实例，方便从 JSON 加载数据。

### 2.2 `WordModel` (`app/models/word_model.py`)

代表词汇表中的一个词。

- **核心属性**:
  - `word_id` (继承自 `id`): 词汇的唯一 ID。
  - `word`: 词语本身。
  - `chaotong_level`: 超童级别，表示难度。
  - `hsk_level`: HSK 级别。
  - `part_of_speech`: 词性（中文）。
- **特点**: `from_dict` 方法中包含了对 `chaotong_level` 的类型转换和异常处理逻辑。

### 2.3 `SceneModel` (`app/models/scene_model.py`)

代表一个故事场景。

- **核心属性**:
  - `scene_id` (继承自 `id`): 场景的唯一 ID。
  - `name`: 场景名称。
  - `description`: 场景描述。
- **特点**: `from_dict` 方法正确地将 JSON 数据中的 `scene_id` 字段映射到模型的 `id` 属性。

### 2.4 `StoryModel` (`app/models/story_model.py`)

代表一个生成的故事，是业务逻辑的核心产出。

- **核心属性**:
  - `story_id` (继承自 `id`): 故事的唯一 ID。
  - `title`: 故事标题。
  - `content`: 故事内容（已按格式处理）。
  - `vocabulary_level`: 故事的目标词汇级别。
  - `scene_id`: 关联的场景 ID。
  - `scene_name`: 关联的场景名称（冗余字段，便于直接使用）。
  - `word_count`: 故事的总词数。
  - `new_word_rate`: 故事的生词率。
  - `key_words`: 故事包含的重点词列表。
  - `unknown_words`: 故事中的生词列表。

## 3. 持久化层分析

### 3.1 SQLAlchemy ORM (`app/database.py`)

项目使用 SQLAlchemy 作为 ORM 工具，实现了与 PostgreSQL 数据库的交互。

- **`engine`**: 通过 `create_engine` 创建与 PostgreSQL 数据库的连接。
- **`SessionLocal`**: 提供线程安全的数据库会话，用于执行 CRUD 操作。
- **`Base`**: 所有模型继承的基础类，提供统一的 ORM 功能。

### 3.2 数据库表结构

- `words` 表: 词汇表，包含 `id`, `word`, `chaotong_level`, `hsk_level`, `part_of_speech`, `created_at`, `updated_at` 等字段。
- `scenes` 表: 场景表，包含 `id`, `name`, `description`, `created_at`, `updated_at` 等字段。
- `stories` 表: 生成的故事表，包含 `id`, `title`, `content`, `vocabulary_level`, `scene_id`, `word_count`, `new_word_rate`, `key_words`, `unknown_words`, `created_at`, `updated_at` 等字段。

## 4. 服务层集成方式

服务层是连接 API 和数据库的桥梁。

### 4.1 `WordService`

- **数据访问**: 通过 SQLAlchemy Session 与数据库交互，无需将数据加载到内存。
- **操作模式**: 所有查询、过滤操作（如 `get_words_below_level`）都通过 SQLAlchemy 查询接口直接从数据库执行。
- **写操作**: `WordService` 提供完整的 CRUD 操作接口，通过 SQLAlchemy Session 持久化到数据库。

### 4.2 `SceneService`

- **数据访问**: 使用 SQLAlchemy Session 与数据库交互，无需将数据加载到内存。
- **操作模式**: 提供了完整的 CRUD 接口（`create_scene`, `update_scene`, `delete_scene`）。每次写操作都通过 SQLAlchemy Session 持久化到数据库。

### 4.3 `StoryService`

- **数据访问**: 通过 SQLAlchemy Session 与数据库交互，获取所需的词汇和场景数据。
- **操作模式**: 核心方法 `generate_story` 和 `rewrite_story` 在完成业务逻辑后，将 `StoryModel` 实例通过 SQLAlchemy Session 持久化到数据库。
- **数据写入**: 新生成的故事通过 SQLAlchemy Session 存储到 `stories` 表中。

## 5. 结论

当前的数据模型和持久化架构采用了现代化的 SQLAlchemy ORM 和 PostgreSQL 数据库技术，能够满足生产环境对**性能、数据一致性和可扩展性**的要求。

**架构优势：**

1.  **ORM 支持**: 使用 `SQLAlchemy` 作为对象关系映射（ORM）工具，将 Python 模型类（如 `WordModel`, `SceneModel`）无缝映射到数据库表，避免了编写大量的原生 SQL 语句。

2.  **模型关系**:

    - 所有模型继承自 `BaseModel`，与 `SQLAlchemy` 的 `declarative_base` 结合，具有统一的列定义和类型。
    - 模型之间定义了清晰的关系，例如 `StoryModel` 和 `SceneModel` 之间的多对一关系。

3.  **数据访问层**:

    - 通过 `app/database.py` 中的 `SessionLocal` 进行数据库会话管理，处理数据库的连接、事务和关闭。

4.  **服务层**:

    - `WordService`, `SceneService`, `StoryService` 不再需要从文件加载数据到内存。
    - 所有的数据操作（CRUD）通过 SQLAlchemy Session 对数据库进行查询和操作。
      - 例如，`scene_service.get_all_scenes()` 使用 `db.session.query(SceneModel).all()`。
      - `scene_service.create_scene()` 使用 `db.session.add(scene)` 和 `db.session.commit()`。

5.  **数据迁移**: 如需从 JSON 文件迁移数据，可编写脚本读取 `app/data/` 目录下的 JSON 文件，并使用 ORM 模型将数据插入到 PostgreSQL 数据库中。

总之，当前的 PostgreSQL 实现为平台提供了生产环境所需的性能和可扩展性，并为未来的功能扩展（如更复杂的数据分析、用户系统等）奠定了坚实的基础。
