# 数据模型与持久化分析

本文档旨在详细分析项目当前的数据模型设计、持久化机制以及它们在服务层中的应用。

## 1. 整体架构概述

项目目前采用了一种**基于内存模型和 JSON 文件存储**的轻量级架构。其核心思想如下：

1.  **模型定义**: 在 `app/models/` 目录下，通过 Python 类定义了应用的核心数据实体（如 `Word`, `Scene`, `Story`）。这些类不仅包含数据属性，还提供了序列化和反序列化的方法。
2.  **数据持久化**: 所有数据以 JSON 文件的形式存储在 `app/data/` 目录中。每个 JSON 文件对应一种数据模型，存储了该模型所有实例的列表。
3.  **数据加载**: 服务（Services）在应用启动时，会读取相应的 JSON 文件，将数据完整加载到内存中，并转换为对应的模型对象列表或字典。
4.  **业务操作**:
    - **读操作**: 如查询、过滤等，直接在内存中的对象列表上进行，速度非常快。
    - **写操作**: 如创建、更新、删除，首先修改内存中的对象列表，然后将整个列表**完整地**写回 JSON 文件，以实现数据持久化。

`JSONStorage` 工具类 (`app/utils/json_storage.py`) 封装了对 JSON 文件的读写操作，为服务层提供了统一的持久化接口。

**数据流**:
`API 层 -> 服务层 -> (内存模型操作) -> JSONStorage -> JSON 文件`

这种架构简单直接，适合项目初期快速迭代和原型验证。但其在性能、并发和数据一致性方面的局限性也十分明显，不适合生产环境的规模化应用。

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

### 3.1 `JSONStorage` (`app/utils/json_storage.py`)

这是一个通用的 JSON 文件读写工具，实现了基本的 CRUD 功能。

- **`_load()`**: 在初始化时调用，读取整个 JSON 文件到 `self.data` (一个字典列表)。它包含对文件不存在、文件为空或格式错误等情况的健壮性处理。
- **`_save()`**: 一个内部方法，使用 `json.dump()` 将 `self.data` 的全部内容写回文件。**这是当前架构的主要性能瓶颈**，因为任何微小的改动都会导致整个文件的重写。
- **`add(item)`**: 将一个新项（字典）追加到 `self.data` 列表，并立即调用 `_save()`。
- **`update(item_id, updated_item)`**: 遍历列表找到对应 ID 的项，替换它，然后调用 `_save()`。
- **`delete(item_id)`**: 遍历列表移除对应 ID 的项，然后调用 `_save()`。

### 3.2 数据文件 (`app/data/*.json`)

- `words.json`: 词汇表，数据量较大，目前是只读的。
- `scenes.json`: 场景列表，支持完整的 CRUD 操作。
- `stories.json`: 生成的故事历史记录，目前只支持追加（`add`）操作。

## 4. 服务层集成方式

服务层是连接 API 和数据模型的桥梁。

### 4.1 `WordService`

- **数据加载**: 在 `__init__` 方法中**直接读取** `words.json` 文件，而不是通过 `JSONStorage`。这与 `SceneService` 的实现方式不一致。
- **操作模式**: 将所有词汇加载到内存字典 `self.words` 中。所有查询、过滤操作（如 `get_words_below_level`）都是对这个内存字典进行的，因此速度很快。
- **写操作**: 目前 `WordService` **不提供**任何写操作的接口。

### 4.2 `SceneService`

- **数据加载**: 使用 `JSONStorage` 来加载 `scenes.json`，并将数据转换为 `SceneModel` 对象，存储在内存字典 `self.scenes` 中。
- **操作模式**: 提供了完整的 CRUD 接口（`create_scene`, `update_scene`, `delete_scene`）。每次写操作都会调用 `_save_scenes` 方法，通过 `JSONStorage` 将**所有场景数据**重新写入文件。

### 4.3 `StoryService`

- **数据加载**: 它不直接加载故事数据，而是依赖 `WordService` 和 `SceneService` 提供所需的基础数据（如已知词汇、场景信息）。
- **操作模式**: 核心方法 `generate_story` 和 `rewrite_story` 在完成业务逻辑后，会创建一个 `StoryModel` 实例。
- **数据写入**: 使用 `JSONStorage` 实例 (`self.story_storage`) 的 `add` 方法，将新生成的故事（转换为字典后）**追加**到 `stories.json` 文件中。

## 5. 结论与迁移建议

当前的数据模型和持久化架构清晰地反映了项目初期的设计目标：**简单、快速、易于实现**。它成功地支撑了核心业务逻辑的开发和验证。

然而，正如项目计划（`README.md`）和本次分析所揭示的，该架构存在明显的局限性，无法满足生产环境对**性能、数据一致性和可扩展性**的要求。

**迁移到 PostgreSQL 的建议：**

1.  **引入 ORM**: 推荐使用 `SQLAlchemy` 作为对象关系映射（ORM）工具。它能将 Python 模型类（如 `WordModel`, `SceneModel`）无缝映射到数据库表，从而避免编写大量的原生 SQL 语句。

2.  **重构模型**:

    - `BaseModel` 可以保留，但需要与 `SQLAlchemy` 的 `declarative_base` 结合，添加列（Column）定义和类型。
    - 需要定义模型之间的关系，例如 `StoryModel` 和 `SceneModel` 之间的多对一关系。

3.  **重构数据访问层**:

    - `JSONStorage` 将被废弃。
    - 需要创建一个新的数据库会话（Session）管理机制，来处理数据库的连接、事务和关闭。可以将其封装在一个新的工具类或使用 `Flask-SQLAlchemy` 扩展来简化管理。

4.  **重构服务层**:

    - `WordService`, `SceneService`, `StoryService` 的 `__init__` 方法不再需要从 JSON 文件加载全部数据。
    - 所有的数据操作（CRUD）都需要重写，将对内存列表的操作改为通过 SQLAlchemy Session 对数据库进行查询和操作。
      - 例如，`scene_service.get_all_scenes()` 将从 `self.scenes.values()` 变为 `db.session.query(SceneModel).all()`。
      - `scene_service.create_scene()` 将从 `self.scenes[scene.id] = scene` 和 `_save_scenes()` 变为 `db.session.add(scene)` 和 `db.session.commit()`。

5.  **数据迁移**: 需要编写一次性的迁移脚本，读取 `app/data/` 目录下的所有 JSON 文件，并使用新的 ORM 模型将数据插入到 PostgreSQL 数据库中。

总之，从 JSON 迁移到 PostgreSQL 是一次必要的架构升级。这将为平台未来的功能扩展（如更复杂的数据分析、用户系统等）和性能提升奠定坚实的基础。
