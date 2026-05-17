# 第 6 章 核心模块实现

本章用于课程报告中的“核心模块实现”部分，重点说明本项目如何通过 Python 编程实现文件扫描、哈希计算、基线管理、异常检测、风险评分、备份恢复、报告导出、命令行交互和 Web 可视化。本文不整段粘贴全部源码，而是选取关键函数片段进行分析，说明每个函数的输入、输出、核心逻辑以及它在风险检测或恢复验证中的作用。

本项目的核心代码均位于 `file_guard/` 目录下，主要依赖 Python 标准库完成检测逻辑，例如 `pathlib`、`hashlib`、`sqlite3`、`shutil`、`json`、`csv` 等。Flask 仅用于本地 Web 可视化界面，系统核心风险检测并未调用第三方安全工具。

---

## 6.1 文件扫描与 SHA-256 哈希计算模块

`scanner.py` 是系统的数据采集入口。该模块负责扫描 `demo_workspace/protected_files` 目录，获取文件相对路径、绝对路径、文件名、扩展名、文件大小、修改时间、SHA-256 哈希值和敏感等级。后续的基线建立、异常检测、风险评分和恢复验证都依赖该模块输出的文件快照。

### 6.1.1 `calculate_sha256` 函数

关键代码片段如下：

```python
def calculate_sha256(file_path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with file_path.open("rb") as file_obj:
        for chunk in iter(lambda: file_obj.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()
```

该函数的作用是计算指定文件的 SHA-256 哈希值。输入参数包括 `file_path` 和 `chunk_size`，其中 `file_path` 表示待计算哈希的文件路径，`chunk_size` 表示每次读取文件内容的块大小。函数输出结果是一个十六进制字符串，用于唯一表示当前文件内容状态。

系统使用 SHA-256 的原因是其碰撞概率极低，适合作为文件完整性验证的内容指纹。只要文件内容发生变化，即使只是一个字符被修改，其 SHA-256 结果也会发生明显变化。因此，在本项目中，SHA-256 是判断文件是否被篡改的核心依据。

函数采用分块读取方式，而不是一次性读取整个文件。这种实现方式能够降低内存占用，适合处理较大文件。虽然课程演示文件较小，但分块读取体现了更接近实际工程的实现方式。

### 6.1.2 `scan_directory` 函数

关键代码片段如下：

```python
def scan_directory(root_dir: Path) -> dict[str, FileSnapshot]:
    root_dir = root_dir.resolve(strict=False)
    ensure_inside_demo_workspace(root_dir)
    snapshots: dict[str, FileSnapshot] = {}

    for file_path in sorted(root_dir.rglob("*")):
        if not file_path.is_file():
            continue
        relative_path_obj = file_path.relative_to(root_dir)
        if _should_skip(relative_path_obj):
            continue
        stat = file_path.stat()
        snapshots[relative_path] = FileSnapshot(
            relative_path=relative_path,
            absolute_path=str(file_path.resolve()),
            file_name=file_path.name,
            extension=file_path.suffix.lower(),
            size=stat.st_size,
            mtime=stat.st_mtime,
            sha256=calculate_sha256(file_path),
            sensitivity=detect_sensitivity(file_path.name, relative_path),
        )
```

该函数输入为受保护目录路径，输出为 `dict[str, FileSnapshot]`，其中字典的键是文件相对路径，值是对应文件快照。函数通过 `rglob("*")` 递归扫描目录，同时跳过隐藏文件、临时文件和缓存文件，避免将无关文件纳入基线。

函数在扫描前会调用路径安全校验，确保扫描范围位于演示工作区内。这一设计非常重要，因为项目涉及文件检测和恢复，如果扫描范围不受限制，可能误触真实系统文件。本系统将扫描范围固定在 `demo_workspace/protected_files`，符合防御性课程项目的安全边界要求。

---

## 6.2 文件敏感等级识别模块

文件敏感等级识别由 `detect_sensitivity` 函数实现。系统根据文件名和路径中的关键词，将文件划分为 `LOW`、`MEDIUM` 和 `HIGH` 三类。

关键代码片段如下：

```python
def detect_sensitivity(file_name: str, relative_path: str) -> str:
    target = f"{file_name} {relative_path}".lower()
    if any(keyword.lower() in target for keyword in SENSITIVE_KEYWORDS):
        return "HIGH"
    if any(keyword.lower() in target for keyword in MEDIUM_KEYWORDS):
        return "MEDIUM"
    return "LOW"
```

该函数输入为文件名和相对路径，输出为敏感等级字符串。系统将 `finance`、`account`、`contract`、`password`、`secret`、`财务`、`合同`、`账号` 等关键词识别为高敏感关键词。原因是这些文件在实际环境中通常与资金、身份、权限、合同责任和业务数据有关，一旦删除或篡改，影响更大。

敏感等级不是单纯用于展示，而是参与风险评分。例如，同样是文件被删除，高敏感文件会比普通文件得到更高风险分值。这样设计能够体现不同文件资产价值的差异。

---

## 6.3 文件哈希基线管理模块

`baseline.py` 负责数据库初始化、基线保存和基线读取。所谓文件哈希基线，是指系统在文件处于正常状态时记录的文件快照。后续检测时，系统将当前扫描结果与基线进行对比，从而判断文件是否新增、删除或被篡改。

### 6.3.1 `init_database`

`init_database` 用于创建 SQLite 数据库表，包括 `baseline_files`、`risk_events` 和 `backups`。该函数保证系统首次运行时具备必要的数据结构。

### 6.3.2 `save_baseline`

关键代码片段如下：

```python
def save_baseline(db_path: Path, snapshots: dict[str, FileSnapshot]) -> None:
    init_database(db_path)
    created_at = now_text()
    with sqlite3.connect(db_path) as conn:
        conn.execute("DELETE FROM baseline_files")
        conn.executemany(
            "INSERT INTO baseline_files (...) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            rows,
        )
```

该函数输入为数据库路径和扫描快照字典，输出为写入数据库中的基线记录。函数首先初始化数据库，然后清空旧基线，再将当前扫描到的文件快照写入 `baseline_files` 表。

保存 `relative_path`、`size`、`mtime`、`sha256` 和 `sensitivity` 的原因如下：`relative_path` 用于安全对比和恢复；`size` 用于辅助判断文件变化；`mtime` 记录文件修改时间；`sha256` 用于判断内容完整性；`sensitivity` 用于后续风险评分。

### 6.3.3 `load_baseline`

`load_baseline` 从数据库中读取历史基线，并重新构造为 `FileSnapshot` 字典。该函数使检测模块能够使用统一的数据结构进行对比。基线管理模块的意义在于为风险检测提供“正常状态”的参照标准，如果没有基线，系统无法判断当前文件是否异常。

---

## 6.4 删除与篡改检测模块

`detector.py` 负责比较基线快照和当前快照，并生成原始变化事件。

### 6.4.1 `detect_changes`

关键代码片段如下：

```python
def detect_changes(baseline, current) -> list[dict]:
    changes = []
    all_paths = sorted(set(baseline) | set(current))
    for relative_path in all_paths:
        old_snapshot = baseline.get(relative_path)
        new_snapshot = current.get(relative_path)
        if old_snapshot is None and new_snapshot is not None:
            changes.append(_make_change("CREATED", relative_path, None, new_snapshot))
        elif old_snapshot is not None and new_snapshot is None:
            changes.append(_make_change("DELETED", relative_path, old_snapshot, None))
        elif old_snapshot and new_snapshot and old_snapshot.sha256 != new_snapshot.sha256:
            changes.append(_make_change("MODIFIED", relative_path, old_snapshot, new_snapshot))
    return changes
```

该函数输入为历史基线和当前扫描结果，输出为变化事件列表。判断规则非常明确：当前扫描有而基线没有，说明文件新增；当前扫描没有而基线有，说明文件被删除；两边都有但 SHA-256 不同，说明文件内容被修改。

该模块是风险检测的核心。它将文件状态变化从目录层面的差异转换为安全事件，为后续风险评分和报告展示提供基础数据。

### 6.4.2 `detect_bulk_change`

`detect_bulk_change` 用于判断是否发生批量变化。当一次扫描中 `CREATED`、`MODIFIED`、`DELETED` 类型事件数量达到阈值时，系统判定为批量变化。

批量变化检测的意义在于扩大风险视角。单个文件变化可能是正常操作，但多个敏感文件同时变化可能代表误操作、异常脚本、批量覆盖或其他高影响风险。

---

## 6.5 批量变更检测模块

本系统将批量变更作为特殊风险事件进行补充识别。当 `detect_bulk_change` 判断变化数量达到阈值后，`enrich_special_events` 会生成 `BULK_CHANGE` 事件。该事件记录受影响文件路径和变化数量。

这种设计避免了只关注单文件风险的问题。对于安全分析而言，多个文件同时变化往往比单个文件变化更值得关注，因为它代表更大的影响范围和更高的不确定性。

---

## 6.6 风险评分与等级判定模块

`risk_engine.py` 负责将原始变化事件转换为完整风险事件。风险事件不仅包含事件类型，还包括分值、等级、证据和建议。

### 6.6.1 `calculate_risk_score`

关键代码片段如下：

```python
def calculate_risk_score(change: dict, is_bulk: bool = False) -> tuple[int, list[str]]:
    score = 0
    if event_type == "DELETED":
        score += 50
    elif event_type == "MODIFIED":
        score += 35
    if matched_keywords:
        score += 20
    if sensitivity == "HIGH":
        score += 25
    if is_bulk:
        score += 25
    return min(score, 100), rules
```

该函数输入为变化事件和批量变化标记，输出为风险分值和命中的风险规则。文件删除基础分高于普通新增，是因为删除直接破坏数据可用性；高敏感文件变化额外加分，是因为账号、财务、合同类文件影响更大；分值封顶为 100，是为了保证风险等级易于比较。

### 6.6.2 `classify_risk_level`

风险等级划分如下：

| 分值范围 | 风险等级 |
|---|---|
| 0-29 | LOW |
| 30-59 | MEDIUM |
| 60-79 | HIGH |
| 80-100 | CRITICAL |

### 6.6.3 `build_risk_event`

`build_risk_event` 负责将原始变化事件封装为 `RiskEvent`，包括事件类型、文件路径、旧哈希、新哈希、旧大小、新大小、风险分值、风险等级、证据、建议和检测时间。

该函数的关键作用是把“检测到文件变化”转化为“可解释的安全风险”。报告中展示的风险证据主要来自该函数生成的 `evidence` 字段。

### 6.6.4 `generate_suggestion`

`generate_suggestion` 根据事件类型和风险等级生成防护建议。例如，删除事件建议从备份恢复并核查删除来源；篡改事件建议复核文件来源并限制写权限；批量变化事件建议停止批量操作来源并逐项恢复关键文件。

---

## 6.7 文件备份与恢复验证模块

`backup.py` 实现备份、恢复和恢复后验证。该模块保证系统不仅能发现风险，还能验证风险处置结果。

### 6.7.1 `backup_files`

关键代码片段如下：

```python
def backup_files(root_dir, backup_dir, snapshots, db_path) -> None:
    for relative_path, snapshot in snapshots.items():
        source = root_dir / relative_path
        target = backup_dir / relative_path
        shutil.copy2(source, target)
```

该函数输入为受保护目录、备份目录、文件快照和数据库路径，输出为备份文件和备份记录。系统在初始化基线时自动备份文件，是为了后续删除或篡改后具备可信恢复来源。

### 6.7.2 `restore_file`

关键代码片段如下：

```python
def restore_file(root_dir, backup_dir, relative_path: str) -> bool:
    if not is_safe_relative_path(relative_path):
        raise ValueError("Unsafe relative path")
    source = backup_dir / relative_path
    target = root_dir / relative_path
    shutil.copy2(source, target)
    return True
```

恢复文件前必须校验路径安全。原因是恢复功能具备写文件能力，如果不限制路径，可能被用于写入演示目录之外的位置。因此系统禁止绝对路径和 `../` 路径穿越。

### 6.7.3 `verify_restored_file`

关键代码片段如下：

```python
actual_hash = calculate_sha256(target)
if actual_hash == expected.sha256:
    return True, "Hash verification passed."
return False, "Hash verification failed."
```

恢复后重新计算 SHA-256 是为了证明恢复结果可信。文件存在并不代表内容正确，只有恢复后哈希与基线一致，才能说明文件恢复到了原始可信状态。

---

## 6.8 报告导出模块

`reporter.py` 负责风险事件保存和报告导出。

### 6.8.1 `save_events_to_db`

该函数将 `RiskEvent` 写入 `risk_events` 表，使风险事件能够被 Web 页面、CLI 和报告模块读取。

### 6.8.2 `export_events_json`

JSON 文件适合保存结构化风险数据，便于后续程序读取和二次分析。

### 6.8.3 `export_events_csv`

CSV 文件适合表格查看，也方便导入 Excel 或 WPS，用于课程报告整理。

### 6.8.4 `generate_html_report`

关键代码片段如下：

```python
def generate_html_report(events, output_path, root_dir) -> None:
    counts = _level_counts(events)
    rows = []
    for event in events:
        impact = explain_impact(event.event_type, event.relative_path, event.level)
        rows.append(...)
    output_path.write_text(report_html, encoding="utf-8")
```

该函数输入为风险事件列表、输出路径和受保护目录，输出为 HTML 报告文件。HTML 报告展示项目标题、生成时间、受保护目录、风险事件总数、风险等级分布、事件表格、风险证据、影响分析和防护建议。

---

## 6.9 命令行入口模块

`cli.py` 提供命令行演示入口。主要命令包括：

| 命令 | 作用 | 适合截图内容 |
|---|---|---|
| `demo-init` | 创建演示目录和模拟文件 | 演示环境初始化 |
| `init` | 初始化基线并备份 | 扫描文件数和备份文件数 |
| `simulate` | 模拟删除、篡改、批量变化 | 风险触发过程 |
| `scan` | 执行风险检测和评分 | 风险事件输出 |
| `restore` | 从备份恢复并校验 | 哈希验证通过 |
| `report` | 导出 JSON、CSV、HTML 报告 | 报告生成结果 |
| `web` | 启动 Web 控制台 | 可视化展示页面 |

CLI 的意义在于保证风险验证流程可复现。报告中可以通过 CLI 截图证明系统确实完成了初始化、模拟、检测、恢复和报告导出。

---

## 6.10 Web 可视化模块

Web 模块由 `web/routes.py`、`web/services.py`、Jinja2 模板、CSS 和 JavaScript 组成。页面路由负责展示界面，API 路由负责接收前端请求，服务层调用核心模块完成实际业务逻辑。

`run_scan` 是 Web 扫描功能的核心函数：

```python
def run_scan() -> dict:
    baseline = load_baseline(DB_PATH)
    current = scan_directory(PROTECTED_DIR)
    changes = detect_changes(baseline, current)
    is_bulk = detect_bulk_change(changes)
    enriched = enrich_special_events(changes, is_bulk)
    events = [build_risk_event(change, is_bulk=is_bulk) for change in enriched]
    save_events_to_db(DB_PATH, events)
    return {"success": True, "data": {...}}
```

该函数无显式输入参数，使用系统配置的数据库路径和受保护目录。输出为统一 API 响应，包含事件数量、是否批量变化、风险等级分布和事件列表。它串联了加载基线、扫描当前目录、检测变化、风险评分、事件保存和前端展示，是 Web 风险检测流程的核心。

Web 前端通过仪表盘展示风险统计，通过风险事件页面展示证据链，通过恢复页面展示恢复验证结果。相比命令行，Web 可视化更适合课程汇报和截图展示。

