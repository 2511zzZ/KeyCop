# KeyCop 总体设计文档

## 1. 概述

KeyCop 是一个自动化工具，旨在通过以下步骤帮助开发者保护其 API 密钥：
1.  **搜索**：使用 GitHub Code Search API 搜索公开仓库中可能泄露的 API 密钥。
2.  **验证**：通过对服务提供商的无害化请求，验证找到的密钥是否有效。
3.  **通知**：如果密钥有效，自动在相关仓库中创建一个 Issue，通知所有者并提供修复建议。

项目将采用模块化设计，确保高内聚、低耦合，并易于扩展以支持新的密钥类型和服务。

## 2. 系统架构

系统由以下几个核心模块组成：

### 2.1. 配置模块 (`config.py`)

-   **职责**：集中管理所有配置信息。
-   **功能**：
    -   管理 KeyCop 自身的 GitHub API Token。
    -   定义要搜索的 API 密钥类型及其正则表达式模式。这将使添加新的密钥类型（如 `GEMINI_API_KEY`）变得简单，只需在配置中增加条目即可。
    -   存储数据库连接信息、日志级别等。

```python
# 示例配置结构
KEY_TYPES = {
    'OPENAI': {
        'pattern': 'sk-[a-zA-Z0-9]{48}',
        'search_query': '"OPENAI_API_KEY=sk-"',
        'verification_endpoint': 'https://api.openai.com/v1/models'
    },
    'GEMINI': {
        'pattern': '[a-zA-Z0-9_-]{38}',
        'search_query': '"GEMINI_API_KEY="',
        'verification_endpoint': '...'
    }
}
```

### 2.2. 数据库模块 (`db/models.py`)

-   **职责**：定义数据模型并处理所有数据库交互，用于持久化存储和进度跟踪。
-   **技术选型**：建议使用 SQLAlchemy + SQLite（或 PostgreSQL），方便进行数据查询和管理。
-   **数据模型**：
    -   `LeakedKey` 表：
        -   `id` (Primary Key)
        -   `repo_full_name` (e.g., 'owner/repo')
        -   `file_path`
        -   `line_number`
        -   `key_type` (e.g., 'OPENAI')
        -   `key_preview` (e.g., 'sk-xxxx')
        -   `status` (Enum: `FOUND`, `VERIFYING`, `VALID_ACTIVE`, `VALID_INACTIVE`, `NOTIFIED`, `ERROR`)
        -   `found_at` (Timestamp)
        -   `last_checked_at` (Timestamp)

### 2.7. 调度模块 (`scheduler.py`)

-   **职责**：实现定时执行扫描任务的功能。
-   **技术选型**：使用 `schedule` 库或 `APScheduler` 实现定时任务。
-   **功能**：
    -   支持配置扫描频率（如每天、每周）
    -   记录上次扫描时间
    -   自动触发增量扫描流程
    -   支持任务失败重试机制

### 2.3. 搜索模块 (`searcher.py`) - 新增增量扫描功能

-   **职责**：执行GitHub代码搜索，并将结果存入数据存储系统。
-   **功能**：
    -   根据 `config.py` 中的 `search_query` 构建搜索请求。
    -   处理 GitHub API 的分页和速率限制。
    -   解析搜索结果，提取仓库、文件、行号等信息。
    -   将新发现的潜在密钥以 `FOUND` 状态存入 `LeakedKey` 表，避免重复录入。
    -   **增量扫描**：
        1.  从 `processed_repos.json` 读取上次扫描时间和已处理仓库列表
        2.  在GitHub搜索时添加时间过滤条件（`pushed:>YYYY-MM-DD`）
        3.  对新搜索结果进行仓库去重，只处理新增仓库
        4.  更新 `processed_repos.json` 中的扫描时间和仓库列表

### 2.4. 验证模块 (`verifier.py`)

-   **职责**：验证数据库中 `FOUND` 状态的密钥是否有效。
-   **功能**：
    -   采用策略模式，为每种 `key_type` 实现一个验证器。
    -   `OpenAIVerifier`：向 OpenAI 的某个端点（如 `/v1/models`）发送一个轻量级请求，检查是否返回 200 OK。
    -   `GeminiVerifier`：实现对 Gemini 密钥的验证逻辑。
    -   根据验证结果更新数据库中密钥的 `status` (`VALID_ACTIVE` 或 `VALID_INACTIVE`)。

### 2.5. 通知模块 (`notifier.py`)

-   **职责**：为状态为 `VALID_ACTIVE` 的密钥创建 GitHub Issue。
-   **功能**：
    -   使用 GitHub API 在目标仓库中创建 Issue。
    -   使用预定义的模板生成 Issue 内容，清晰地说明问题、泄露位置和修复建议。
    -   创建 Issue 后，将数据库中对应密钥的 `status` 更新为 `NOTIFIED`。

### 2.6. 批处理与工作流 (`batch.py` & `cli.py`)

-   **职责**：协调所有模块，实现自动化工作流。
-   **功能**：
    -   `cli.py` 提供命令行接口，允许手动触发不同阶段的任务：
        -   `python -m keycop search`：启动搜索任务。
        -   `python -m keycop verify --limit=100`：验证 100 个密钥。
        -   `python -m keycop notify --limit=10`：发送 10 个通知。
    -   `batch.py` 包含核心工作流逻辑，例如：
        1.  从数据库中查询一批需要验证的密钥。
        2.  并发执行验证（使用 `asyncio` 或 `ThreadPoolExecutor`）。
        3.  更新数据库状态。
        4.  查询一批需要通知的已验证密钥，并执行通知。

## 3. 工作流程 - 更新为支持定时和增量扫描

1.  **初始化**：用户通过CLI配置定时任务：
    ```bash
    python -m keycop schedule --daily  # 配置每天执行一次
    ```
2.  **定时触发**：调度模块在设定时间自动启动扫描任务。
3.  **增量搜索**：`searcher`模块只搜索上次扫描后更新的仓库，避免重复处理。
4.  **验证**：`batch`模块从存储中获取`FOUND`状态的密钥，`verifier`并发验证它们，并更新状态。
5.  **通知**：`batch`模块获取`VALID_ACTIVE`状态的密钥，`notifier`为它们创建Issue，并更新状态为`NOTIFIED`。
6.  **状态更新**：完成后更新扫描历史和已处理仓库列表。