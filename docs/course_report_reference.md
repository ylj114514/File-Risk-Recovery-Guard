# 《基于文件哈希基线的敏感文件异常删除、篡改检测与恢复验证系统》课程报告参考资料

副标题：面向本地敏感文件安全风险的可视化验证与防护分析  
英文项目名：File-Risk-Recovery-Guard  
课程方向：网络信息安全风险技术编程  
项目类型：本地防御性风险验证系统  

> 本文档用于整理课程 PDF 报告写作素材。内容不是 README，也不是简单的软件使用说明，而是围绕“为什么做、如何设计、如何实现、运行结果展示了什么风险、如何防护”进行组织。正式提交 PDF 时，可以在此基础上加入截图、页眉页脚、封面、目录和个人信息。

---

## 一、报告写作定位

本项目选择的安全风险方向是“文件异常删除、篡改与恢复风险”。在实际学习、办公和业务系统中，敏感文件可能包含账号清单、财务报告、合同资料、客户名单、项目计划等内容。如果这些文件被误删、恶意删除、篡改或批量修改，会造成数据不可用、数据可信性下降、审计证据丢失和恢复困难等问题。

本项目不是攻击工具，也不是调用现成安全软件，而是使用 Python 编程实现一个本地风险验证系统。系统通过文件 SHA-256 哈希基线记录文件原始状态，通过扫描与基线对比发现删除和篡改，通过风险评分规则判断风险等级，通过备份恢复和恢复后哈希校验证明恢复结果是否可信，并通过 CLI 和 Flask Web 页面展示执行结果。

报告写作时应重点体现以下逻辑：

1. 本地敏感文件存在删除、篡改和批量变化风险。
2. 文件哈希基线可以作为完整性检测的对照标准。
3. 删除和篡改检测不能只看文件名，还要结合哈希、大小、敏感等级和变化数量。
4. 恢复不是简单复制文件，恢复后必须重新计算哈希进行验证。
5. 风险展示需要给出风险对象、触发条件、证据、影响、评分和建议。

---

## 二、项目概况

### 2.1 项目名称

中文题目：《基于文件哈希基线的敏感文件异常删除、篡改检测与恢复验证系统》

副标题：面向本地敏感文件安全风险的可视化验证与防护分析

英文项目名：File-Risk-Recovery-Guard

### 2.2 项目目标

本项目的目标是开发一个本地安全演示系统，使“敏感文件被异常删除或篡改”的风险可见、可测、可验证。系统通过编程实现文件扫描、基线建立、风险模拟、异常检测、风险评分、数据库保存、备份恢复、报告导出和 Web 可视化展示。

### 2.3 项目功能清单

系统实现了以下功能：

1. 创建本地演示目录 `demo_workspace/protected_files`。
2. 生成模拟敏感文件，如 `finance_report.txt`、`account_list.txt`、`contract_2025.txt`。
3. 扫描文件并计算 SHA-256 哈希。
4. 建立文件哈希基线。
5. 自动备份基线文件。
6. 模拟敏感文件被删除。
7. 模拟敏感文件被篡改。
8. 模拟多个文件批量异常变化。
9. 检测 `DELETED`、`MODIFIED`、`CREATED`、`BULK_CHANGE`、`HIGH_SENSITIVE_CHANGED`、`SUSPICIOUS_EXTENSION` 等事件。
10. 根据风险规则计算风险分值。
11. 根据分值划分 `LOW`、`MEDIUM`、`HIGH`、`CRITICAL` 风险等级。
12. 从备份恢复被删除或篡改文件。
13. 恢复后重新计算 SHA-256 并与基线比对。
14. 生成 JSON、CSV、HTML 风险报告。
15. 提供 Flask Web 可视化界面。
16. 提供 CLI 命令行演示入口。
17. 提供 pytest 测试用例。

### 2.4 安全边界

报告中必须说明本项目是防御性风险验证系统，并遵守以下安全边界：

1. 只操作项目目录下的 `demo_workspace/protected_files`。
2. 不扫描真实系统敏感目录。
3. 不删除真实用户文件。
4. 不访问外部网络。
5. 不调用第三方攻击工具。
6. 不实现木马、后门、键盘记录、密码窃取、漏洞利用、远程控制等攻击功能。
7. 模拟新增的 `suspicious.ps1` 只写入无害文本，不执行脚本。
8. Web 服务默认只监听 `127.0.0.1`。
9. 所有恢复路径都进行安全校验，禁止 `../` 和绝对路径。

---

## 三、项目目录结构说明

项目核心目录如下：

```text
file-risk-recovery-guard/
├── file_guard/
│   ├── scanner.py        文件扫描与哈希计算模块
│   ├── baseline.py       文件基线保存与读取模块
│   ├── detector.py       文件删除、篡改、批量变更检测模块
│   ├── risk_engine.py    风险评分与等级判定模块
│   ├── backup.py         文件备份与恢复验证模块
│   ├── reporter.py       风险事件导出与 HTML 报告模块
│   ├── demo.py           演示数据生成与风险模拟模块
│   ├── cli.py            命令行入口模块
│   └── web/              Flask Web 可视化界面模块
├── tests/                pytest 测试用例
├── demo_workspace/       本地演示工作区
├── data/                 SQLite 数据库和备份目录
├── outputs/              JSON、CSV、HTML 报告输出目录
└── docs/                 课程报告辅助文档
```

各模块之间的关系可以概括为：`scanner.py` 负责采集文件状态，`baseline.py` 保存基线，`detector.py` 比较当前状态和基线，`risk_engine.py` 生成风险事件，`backup.py` 负责恢复验证，`reporter.py` 导出报告，`cli.py` 和 `web/` 提供用户交互入口。

---

## 四、正式报告章节参考稿

# 第 1 章 选题背景与研究目标

## 1.1 课程作业背景

“网络信息安全风险技术编程”课程要求学生围绕一个明确的安全风险，通过编程完成一个具有设计、实现、运行结果、风险分析和防护建议的完整项目。本项目选择“文件异常删除、篡改与恢复风险”作为研究对象，原因是文件安全是本地系统和业务系统中常见而重要的安全问题。相比单纯讲解理论，本项目通过编程构建完整演示环境，使风险检测、评分和恢复过程能够被直接观察。

本项目不是简单调用第三方工具，也不是只提交源代码，而是从风险场景出发，设计并实现了一个包含后端检测引擎、数据库、CLI、Web 前端、报告导出和测试用例的完整系统。

## 1.2 文件异常删除与篡改风险背景

敏感文件通常承载业务数据、账号信息、财务资料、合同内容或项目计划。一旦文件被异常删除，可能导致数据不可用和业务中断；一旦文件被篡改，可能导致错误决策、数据污染和审计困难；如果多个文件在短时间内同时变化，则可能说明存在批量误操作、异常程序或未授权写入行为。

传统人工检查文件是否存在效率较低，也难以判断文件内容是否被微小修改。因此，本项目采用 SHA-256 文件哈希作为完整性证据，通过基线对比发现文件内容变化。

## 1.3 本项目研究对象

本项目研究对象是本地演示目录中的模拟敏感文件，包括：

- `finance_report.txt`：模拟财务报告；
- `account_list.txt`：模拟账号清单；
- `contract_2025.txt`：模拟合同文件；
- `project_plan.txt`：模拟项目计划；
- `normal_note.txt`：普通笔记。

这些文件不包含真实敏感信息，只用于课程风险验证。系统通过关键词识别文件敏感等级，并根据变化类型计算风险分数。

## 1.4 本项目实现目标

项目实现目标包括：

1. 能够创建可重复演示的本地文件环境。
2. 能够扫描文件并计算 SHA-256 哈希。
3. 能够保存文件基线并作为后续检测标准。
4. 能够模拟删除、篡改、批量变化和新增可疑扩展名文件。
5. 能够识别异常变化并生成风险事件。
6. 能够根据风险规则计算分值和等级。
7. 能够从备份恢复文件并验证恢复结果。
8. 能够通过 CLI 和 Web 页面展示检测结果。
9. 能够导出 JSON、CSV、HTML 风险报告。

## 1.5 本项目与课程要求的对应关系

本项目与课程要求的对应关系如下：

| 课程要求 | 项目对应实现 |
|---|---|
 明确安全风险 | 文件异常删除、篡改和恢复风险 |
 编程实现 | 使用 Python、Flask、SQLite、Jinja2 原生实现 |
 有系统设计 | 后端检测引擎、数据库、Web 前端、CLI 分层设计 |
 有运行结果 | CLI 输出、Web 页面、HTML 报告 |
 有风险说明 | 风险评分、风险证据、影响分析 |
 有防护建议 | 最小权限、备份、哈希校验、日志审计 |

---

# 第 2 章 风险场景说明

## 2.1 敏感文件异常删除风险

敏感文件异常删除是指重要文件在未授权、误操作或异常程序影响下被删除。对于账号清单、合同、财务报告等文件，删除可能导致业务无法继续、审计资料缺失和恢复成本上升。本项目通过删除 `account_list.txt` 模拟该风险。系统扫描时发现基线中存在该文件，而当前目录中不存在该文件，因此生成 `DELETED` 风险事件。

## 2.2 敏感文件内容篡改风险

文件篡改是指文件仍然存在，但内容发生了非预期变化。仅通过文件名或路径无法发现这种风险，因此需要使用哈希进行完整性验证。本项目通过修改 `finance_report.txt` 内容，使其 SHA-256 与基线不同，从而触发 `MODIFIED` 事件。

## 2.3 多文件批量异常变化风险

多个文件同时变化通常比单个文件变化更值得关注。批量变化可能来自错误脚本、异常程序、批量误操作或未授权写入。本项目设置阈值，当一次扫描中变化文件数量达到 3 个及以上时，系统生成 `BULK_CHANGE` 事件。

## 2.4 文件恢复失败风险

文件恢复不是简单把备份复制回去。如果备份文件本身不可信、恢复路径错误或恢复后内容仍然被篡改，则恢复结果不能被认为可靠。因此本项目在恢复文件后重新计算 SHA-256，并与基线中的哈希进行比对。只有哈希一致，才认为恢复验证通过。

## 2.5 风险影响分析

本项目展示的风险影响包括：

1. 数据不可用：文件被删除后，业务或学习资料无法直接使用。
2. 数据可信性下降：文件被篡改后，即使文件仍存在，也无法确认内容是否可靠。
3. 审计困难：如果没有事件记录和证据，无法说明风险发生时间、对象和原因。
4. 恢复不确定：如果恢复后不校验哈希，无法证明恢复文件是否与原始基线一致。

---

# 第 3 章 系统需求分析

## 3.1 功能需求

系统需要完成演示数据生成、文件扫描、哈希计算、基线保存、备份、风险模拟、异常检测、风险评分、风险事件保存、恢复验证、报告导出、CLI 演示和 Web 展示等功能。

## 3.2 非功能需求

系统需要满足以下非功能需求：

1. 可重复演示：能够通过 `reset` 恢复初始状态。
2. 可解释：每个风险事件都应包含证据和建议。
3. 可视化：Web 页面适合课堂展示和截图。
4. 可测试：核心模块应具备 pytest 测试。
5. 可维护：模块职责清晰，便于扩展。

## 3.3 安全边界

系统只允许操作 `demo_workspace/protected_files`，不访问真实系统目录。恢复文件时必须校验路径安全，禁止路径穿越和绝对路径。Web 服务默认监听 `127.0.0.1`，避免无意暴露到公网。

## 3.4 运行环境

运行环境包括：

- Python 3.10+；
- Flask；
- SQLite；
- Jinja2；
- 原生 HTML、CSS、JavaScript；
- pytest。

## 3.5 测试与演示需求

测试覆盖文件扫描、基线保存、异常检测、风险评分、备份恢复和 Web 服务层。演示流程需要能够展示从初始化、模拟、扫描、恢复到报告导出的完整闭环。

---

# 第 4 章 系统总体设计

## 4.1 系统总体架构

系统采用分层架构：

```text
用户操作层：CLI / Web 页面
业务服务层：web/services.py、cli.py
检测分析层：scanner.py、detector.py、risk_engine.py
数据持久层：baseline.py、reporter.py、SQLite
恢复验证层：backup.py
演示数据层：demo_workspace/protected_files
```

这种设计的优点是：扫描、检测、评分、恢复、展示相互独立，便于测试和维护。

## 4.2 后端检测引擎设计

后端检测引擎以文件快照为核心。扫描模块生成当前快照，基线模块加载历史快照，检测模块比较两者差异，风险引擎将差异转换为风险事件。这样可以把文件状态变化抽象为标准事件，便于评分和报告展示。

## 4.3 数据库存储设计

SQLite 数据库用于保存基线文件、风险事件和备份记录。选择 SQLite 的原因是它不需要单独部署数据库服务，适合本地课程演示，同时能够保证数据结构化保存。

## 4.4 命令行交互设计

CLI 提供 `demo-init`、`init`、`simulate`、`scan`、`restore`、`report`、`web`、`reset` 等命令。CLI 的作用是支持截图演示和完整流程验证，也便于在没有浏览器时运行系统。

## 4.5 Web 前端可视化设计

Web 前端采用 Flask + Jinja2 + 原生 CSS/JS。页面包括仪表盘、基线文件、风险事件、扫描检测、模拟风险、文件恢复和报告导出。前端不仅展示数据，还将操作结果转换为可读段落，便于课程报告截图。

## 4.6 系统运行流程

系统运行流程如下：

1. 创建演示目录和模拟敏感文件。
2. 扫描文件并计算 SHA-256。
3. 保存基线并备份文件。
4. 执行删除、篡改或批量变化模拟。
5. 再次扫描当前文件状态。
6. 对比基线生成变化事件。
7. 计算风险分数和等级。
8. 保存风险事件到数据库。
9. Web 页面展示风险统计和证据。
10. 从备份恢复文件并验证哈希。
11. 导出 JSON、CSV、HTML 报告。

## 4.7 数据流设计

数据流可以表示为：

```text
protected_files
  -> scanner.py 生成 FileSnapshot
  -> baseline.py 保存 baseline_files
  -> detector.py 生成变化事件
  -> risk_engine.py 生成 RiskEvent
  -> reporter.py 保存 risk_events
  -> Web/CLI/HTML 报告展示
```

---

# 第 5 章 数据库设计

## 5.1 baseline_files 表设计

`baseline_files` 保存文件基线信息，包括相对路径、绝对路径、文件名、扩展名、大小、修改时间、SHA-256 和敏感等级。相对路径用于安全恢复和对比，SHA-256 用于判断内容是否变化。

## 5.2 risk_events 表设计

`risk_events` 保存风险事件，包括事件类型、文件路径、旧哈希、新哈希、旧大小、新大小、风险分值、风险等级、风险证据、防护建议和检测时间。该表是后续 Web 展示和报告导出的主要数据来源。

## 5.3 backups 表设计

`backups` 保存备份信息，包括文件相对路径、备份路径、备份哈希和创建时间。备份表用于确认文件恢复来源，并支持恢复后校验。

## 5.4 数据库读写流程

初始化基线时，系统先创建数据库表，再扫描当前文件，将快照写入 `baseline_files`。扫描检测时，系统读取基线并与当前快照对比，将生成的风险事件写入 `risk_events`。导出报告时，系统从 `risk_events` 读取历史事件。

## 5.5 数据库在风险证据保存中的作用

数据库使风险事件具有可追溯性。每条事件不仅保存类型和路径，还保存哈希变化、大小变化、风险分值和建议。这些信息能够作为课程报告中的风险证据，说明系统不是只输出“有风险”，而是能够说明“为什么判定为风险”。

---

# 第 6 章 核心模块实现

## 6.1 文件扫描与 SHA-256 哈希计算模块

`scanner.py` 负责扫描 `demo_workspace/protected_files` 目录，获取文件路径、大小、修改时间、SHA-256 哈希值和敏感等级。该模块是整个检测系统的数据入口。

### 6.1.1 `calculate_sha256` 函数

关键代码片段：

```python
def calculate_sha256(file_path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with file_path.open("rb") as file_obj:
        for chunk in iter(lambda: file_obj.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()
```

函数作用：计算指定文件的 SHA-256 哈希值。  
输入参数：`file_path` 表示待计算的文件路径，`chunk_size` 表示分块读取大小。  
输出结果：返回文件内容对应的 SHA-256 十六进制字符串。  
核心逻辑：以二进制方式打开文件，按块读取内容并逐步更新哈希对象，最后输出摘要。  
系统作用：为文件完整性验证提供唯一内容指纹。  
与风险检测的关系：如果同一路径文件当前哈希与基线哈希不同，则说明文件内容被修改，可判定为 `MODIFIED`。

使用 SHA-256 的原因是它具有较低碰撞概率，能够较可靠地反映文件内容是否变化。使用分块读取的原因是避免一次性读取大文件造成内存占用过高，虽然本项目演示文件较小，但这种实现方式更符合实际系统设计。

### 6.1.2 `scan_directory` 函数

关键代码片段：

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
            size=stat.st_size,
            mtime=stat.st_mtime,
            sha256=calculate_sha256(file_path),
            sensitivity=detect_sensitivity(file_path.name, relative_path),
        )
    return snapshots
```

函数作用：递归扫描受保护目录，生成文件快照字典。  
输入参数：`root_dir` 表示受保护目录。  
输出结果：返回 `dict[str, FileSnapshot]`，键为相对路径，值为文件快照对象。  
核心逻辑：递归遍历文件，跳过隐藏文件和临时文件，记录文件大小、修改时间、哈希和敏感等级。  
系统作用：为基线建立和当前状态检测提供统一数据结构。  
与风险检测的关系：当前扫描结果会与历史基线对比，从而判断新增、删除和篡改。

## 6.2 文件敏感等级识别模块

`detect_sensitivity` 函数根据文件名和路径中的关键词识别敏感等级。系统将 `finance`、`account`、`contract`、`password`、`secret`、`财务`、`合同`、`账号` 等关键词判定为高敏感，因为这些文件通常与财务资料、账号资产、合同责任或身份凭据相关。

关键代码片段：

```python
def detect_sensitivity(file_name: str, relative_path: str) -> str:
    target = f"{file_name} {relative_path}".lower()
    if any(keyword.lower() in target for keyword in SENSITIVE_KEYWORDS):
        return "HIGH"
    if any(keyword.lower() in target for keyword in MEDIUM_KEYWORDS):
        return "MEDIUM"
    return "LOW"
```

函数作用：识别文件敏感等级。  
输入参数：文件名和文件相对路径。  
输出结果：`LOW`、`MEDIUM` 或 `HIGH`。  
核心逻辑：将文件名和路径转换为小写后匹配敏感关键词。  
系统作用：为风险评分提供敏感度依据。  
与风险检测的关系：高敏感文件发生删除或篡改时，风险分值会更高。

## 6.3 文件哈希基线管理模块

`baseline.py` 负责初始化数据库、保存基线和读取基线。文件基线是系统对“正常状态”的记录，后续检测都以基线为参照。

### 6.3.1 `init_database`

该函数创建 `baseline_files`、`risk_events` 和 `backups` 三张表。它保证系统首次运行时数据库结构存在。

### 6.3.2 `save_baseline`

关键代码片段：

```python
def save_baseline(db_path: Path, snapshots: dict[str, FileSnapshot]) -> None:
    init_database(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.execute("DELETE FROM baseline_files")
        conn.executemany(
            "INSERT INTO baseline_files (...) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [...]
        )
```

函数作用：将扫描得到的文件快照保存为新的基线。  
输入参数：数据库路径和文件快照字典。  
输出结果：无直接返回值，数据写入 SQLite。  
核心逻辑：先清空旧基线，再批量插入当前文件快照。  
系统作用：确定后续检测的正常参照状态。  
与风险检测的关系：如果没有基线，系统无法判断当前文件是否被删除或篡改。

### 6.3.3 `load_baseline`

`load_baseline` 从数据库读取历史基线，并重新构造为 `FileSnapshot` 字典，供 `detector.py` 对比使用。

保存 `relative_path`、`size`、`mtime`、`sha256`、`sensitivity` 的原因如下：

- `relative_path`：作为对比和恢复的安全路径；
- `size`：辅助说明文件大小是否变化；
- `mtime`：记录文件修改时间；
- `sha256`：判断内容完整性；
- `sensitivity`：参与风险评分。

## 6.4 删除与篡改检测模块

`detector.py` 将基线快照和当前快照进行对比，生成原始变化事件。

### 6.4.1 `detect_changes`

关键代码片段：

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

函数作用：识别新增、删除和修改事件。  
输入参数：历史基线快照和当前扫描快照。  
输出结果：变化事件列表。  
核心逻辑：对基线路径集合和当前路径集合取并集，逐个路径判断状态。  
系统作用：将文件状态差异转化为安全事件。  
与风险检测的关系：`DELETED`、`MODIFIED` 是后续风险评分的主要依据。

### 6.4.2 `detect_bulk_change`

```python
def detect_bulk_change(changes: list[dict], threshold: int = 3) -> bool:
    return sum(1 for change in changes if change.get("event_type") in base_events) >= threshold
```

当一次扫描中基础变化数量达到 3 个及以上时，系统认为发生批量变化。批量变化比单文件变化风险更高，因为它可能代表批量误操作或异常程序行为。

## 6.5 批量变更检测模块

批量变更检测不是简单增加一个事件类型，而是对多个文件变化进行整体判断。当系统发现同一次扫描中多个文件同时发生 `CREATED`、`MODIFIED` 或 `DELETED` 时，会补充生成 `BULK_CHANGE` 事件。

该设计的意义在于：单个文件变化可能是正常操作，但多个敏感文件短时间内同时变化更可能造成较大影响，需要在风险报告中单独突出。

## 6.6 风险评分与等级判定模块

`risk_engine.py` 负责将原始变化事件转换为带有分数、等级、证据和建议的 `RiskEvent`。

### 6.6.1 `calculate_risk_score`

关键代码片段：

```python
def calculate_risk_score(change: dict, is_bulk: bool = False) -> tuple[int, list[str]]:
    score = 0
    if event_type == "DELETED":
        score += 50
    elif event_type == "MODIFIED":
        score += 35
    if matched_sensitive_keywords:
        score += 20
    if sensitivity == "HIGH":
        score += 25
    if is_bulk:
        score += 25
    return min(score, 100), rules
```

函数作用：根据事件类型、敏感等级、关键词、扩展名和批量情况计算风险分值。  
输入参数：变化事件字典和是否批量变化。  
输出结果：风险分值和命中的规则说明。  
核心逻辑：按照规则累加分值，并限制最高分为 100。  
系统作用：将检测结果量化，便于排序、展示和报告分析。  
与风险检测的关系：分值越高，说明事件越需要优先处理。

文件删除比普通新增风险更高，因为删除会直接造成数据不可用；高敏感文件变化额外加分，是因为账号、财务、合同等文件影响更大；分值限制在 100 是为了避免多个规则叠加后难以比较。

### 6.6.2 `classify_risk_level`

风险等级划分如下：

| 分值范围 | 等级 |
|---|---|
 0-29 | LOW |
 30-59 | MEDIUM |
 60-79 | HIGH |
 80-100 | CRITICAL |

### 6.6.3 `build_risk_event`

`build_risk_event` 将原始变化事件转换为完整风险事件，包含事件类型、路径、旧哈希、新哈希、大小变化、分值、等级、证据、建议和时间。

关键作用是把“检测到变化”变成“可解释的风险证据”。报告中展示的风险证据主要来自该函数生成的 `evidence` 字段。

### 6.6.4 `generate_suggestion`

该函数根据事件类型和风险等级生成防护建议。例如，删除事件建议从备份恢复并核查删除来源；篡改事件建议复核内容来源并限制写权限；可疑扩展名事件建议不要执行该文件并检查来源。

## 6.7 文件备份与恢复验证模块

`backup.py` 负责在初始化基线时备份文件，在恢复时校验路径安全，并在恢复后验证哈希。

### 6.7.1 `backup_files`

关键代码片段：

```python
def backup_files(root_dir, backup_dir, snapshots, db_path) -> None:
    for relative_path, snapshot in snapshots.items():
        source = root_dir / relative_path
        target = backup_dir / relative_path
        shutil.copy2(source, target)
```

函数作用：将基线文件复制到备份目录。  
输入参数：受保护目录、备份目录、文件快照和数据库路径。  
输出结果：备份文件和备份记录。  
核心逻辑：保持相对路径结构复制文件，并写入 `backups` 表。  
系统作用：为后续恢复提供可信来源。  
与恢复验证的关系：没有备份，就无法恢复被删除的文件。

### 6.7.2 `restore_file`

关键代码片段：

```python
def restore_file(root_dir, backup_dir, relative_path: str) -> bool:
    if not is_safe_relative_path(relative_path):
        raise ValueError("Unsafe relative path")
    source = backup_dir / relative_path
    target = root_dir / relative_path
    shutil.copy2(source, target)
    return True
```

函数作用：从备份目录恢复指定文件。  
输入参数：受保护目录、备份目录、文件相对路径。  
输出结果：恢复成功返回 `True`，备份不存在返回 `False`。  
核心逻辑：先校验路径安全，再从备份目录复制到受保护目录。  
系统作用：实现删除或篡改后的恢复操作。  
与安全边界的关系：禁止路径穿越，避免恢复功能写入演示目录之外。

### 6.7.3 `verify_restored_file`

关键代码片段：

```python
def verify_restored_file(root_dir, baseline, relative_path) -> tuple[bool, str]:
    actual_hash = calculate_sha256(target)
    if actual_hash == expected.sha256:
        return True, "Hash verification passed."
    return False, "Hash verification failed."
```

函数作用：恢复后重新计算文件哈希并与基线比对。  
输入参数：受保护目录、基线字典、文件相对路径。  
输出结果：是否验证成功和说明文本。  
核心逻辑：计算恢复后文件 SHA-256，与基线哈希比较。  
系统作用：证明恢复结果是否可信。  
与恢复验证的关系：哈希一致说明恢复后的文件内容与基线状态一致。

## 6.8 报告导出模块

`reporter.py` 负责将风险事件保存到数据库，并导出 JSON、CSV、HTML 报告。

### 6.8.1 `save_events_to_db`

该函数将风险事件写入 `risk_events` 表，使事件能够被 Web 页面和报告模块读取。

### 6.8.2 `export_events_json`

JSON 适合保存结构化风险数据，便于程序再次读取和分析。

### 6.8.3 `export_events_csv`

CSV 适合表格化查看，也便于导入 Excel 或 WPS。

### 6.8.4 `generate_html_report`

关键代码片段：

```python
def generate_html_report(events, output_path, root_dir) -> None:
    counts = _level_counts(events)
    rows = []
    for event in events:
        impact = explain_impact(event.event_type, event.relative_path, event.level)
        rows.append(...)
    output_path.write_text(report_html, encoding="utf-8")
```

函数作用：生成可视化 HTML 风险报告。  
输入参数：风险事件列表、输出路径、受保护目录。  
输出结果：`outputs/report.html`。  
核心逻辑：统计风险等级分布，生成事件表格，写入 HTML 文件。  
系统作用：将检测结果转换为适合截图和提交的报告页面。  
与风险分析的关系：HTML 报告集中展示风险对象、触发条件、证据、影响分析、分值、等级和建议。

## 6.9 命令行入口模块

`cli.py` 提供完整演示流程：

| 命令 | 作用 | 可截图内容 |
|---|---|---|
 `demo-init` | 创建演示目录和文件 | 演示目录初始化 |
 `init` | 初始化基线和备份 | 扫描文件数、备份文件数 |
 `simulate --case delete` | 模拟删除账号文件 | 删除操作结果 |
 `simulate --case modify` | 模拟篡改财务文件 | 篡改操作结果 |
 `simulate --case bulk` | 模拟批量变化 | 批量变化结果 |
 `scan` | 执行检测和评分 | 风险事件列表 |
 `restore --path account_list.txt` | 恢复文件并校验 | 哈希验证通过 |
 `report` | 导出报告 | JSON/CSV/HTML 生成结果 |
 `web` | 启动 Web 页面 | Web 仪表盘 |

CLI 将系统流程串联起来，适合在课程报告中展示程序运行过程。

## 6.10 Web 可视化模块

Web 模块包括 `web/routes.py`、`web/services.py`、模板文件和静态资源。

### 6.10.1 页面路由

页面路由包括：

- `/`：仪表盘；
- `/baseline`：基线文件；
- `/events`：风险事件；
- `/scan`：扫描检测；
- `/simulate`：模拟风险；
- `/restore`：文件恢复；
- `/reports`：报告导出。

### 6.10.2 API 路由与服务层

`web/services.py` 中的 `run_scan` 是 Web 扫描功能的核心。

关键代码片段：

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

函数作用：执行一次完整 Web 风险扫描。  
输入参数：无显式输入，使用系统配置的数据库和受保护目录。  
输出结果：统一 API 响应，包含事件数量、风险分布和事件列表。  
核心逻辑：加载基线、扫描当前目录、检测变化、计算风险、保存事件、返回结果。  
系统作用：支撑前端“执行风险扫描”按钮。  
与风险展示的关系：前端根据该函数返回的数据展示风险统计和事件详情。

### 6.10.3 前端对风险展示的增强

Web 前端通过统计卡片、风险等级标签、风险分布条、事件表格和恢复结果摘要，将命令行结果转化为更直观的课程展示材料。风险事件页面可以展开查看 old_hash、new_hash、old_size、new_size、完整证据和防护建议，使报告截图更有说服力。

---

# 第 7 章 Web 前端可视化设计

## 7.1 前端设计目标

前端设计目标是让风险检测结果更易理解和展示。相比命令行输出，Web 页面能够同时展示统计数据、风险等级分布、事件列表和操作结果，更适合课堂汇报和 PDF 截图。

## 7.2 页面结构设计

页面采用左侧导航栏和右侧主内容区。左侧导航用于切换功能，右侧内容区显示当前页面。页面风格保持简洁，重点突出风险等级、风险对象和证据。

## 7.3 仪表盘页面设计

仪表盘展示受保护文件数、风险事件总数、HIGH 事件数、CRITICAL 事件数、风险等级分布和最近事件。该页面用于快速说明系统当前状态。

## 7.4 基线文件页面设计

基线文件页面展示每个文件的路径、文件名、扩展名、大小、敏感等级、SHA-256 前 16 位和修改时间。该页面说明系统已经建立了完整性检测基线。

## 7.5 风险事件页面设计

风险事件页面展示风险等级、风险分值、事件类型、文件路径、证据、建议和检测时间。点击事件可以展开查看完整哈希变化和大小变化。

## 7.6 模拟风险页面设计

模拟风险页面提供删除、篡改、批量变化和新增可疑脚本按钮，并明确说明所有操作只发生在演示目录中。

## 7.7 文件恢复页面设计

文件恢复页面允许输入安全相对路径，并展示恢复是否成功、哈希校验是否通过。

## 7.8 报告导出页面设计

报告导出页面生成 JSON、CSV、HTML 文件，并提供 HTML 报告查看入口。

## 7.9 前端对风险展示的增强作用

前端将抽象的检测数据转化为可读的可视化材料，包括风险等级标签、分布条、结果摘要和表格。这使风险不再停留在代码层，而是能够被观察、截图和解释。

---

# 第 8 章 执行结果展示

本章用于放置程序运行截图。正式 PDF 中建议每张截图下方配 2 至 4 行说明，说明执行命令、观察到的结果和安全意义。

## 8.1 演示目录初始化结果

运行命令：

```bash
python -m file_guard.cli demo-init
```

预期结果：系统创建 `demo_workspace/protected_files` 并生成模拟敏感文件。

【截图 1：demo-init 初始化演示目录】

## 8.2 文件基线初始化结果

运行命令：

```bash
python -m file_guard.cli init --root demo_workspace/protected_files
```

预期结果：系统扫描 5 个文件，保存基线，并备份文件。

【截图 2：init 初始化文件哈希基线】

## 8.3 Web 首页仪表盘

Web 仪表盘展示基线文件数量、风险事件数量、风险等级分布和最近事件。

【截图 3：Web 首页仪表盘】

## 8.4 基线文件列表页面

基线文件页面展示每个文件的 SHA-256 前 16 位和敏感等级。

【截图 4：基线文件列表页面】

## 8.5 模拟文件删除结果

运行命令：

```bash
python -m file_guard.cli simulate --case delete
```

系统删除演示目录中的 `account_list.txt`。

【截图 5：模拟风险页面】  
【截图 6：simulate delete 模拟删除 account_list.txt】

## 8.6 删除风险检测结果

运行命令：

```bash
python -m file_guard.cli scan --root demo_workspace/protected_files
```

系统检测到 `account_list.txt` 在基线中存在，但当前目录中不存在，因此生成 `DELETED` 事件。

【截图 7：scan 检测 DELETED 风险】

## 8.7 文件恢复验证结果

运行命令：

```bash
python -m file_guard.cli restore --path account_list.txt
```

系统从备份恢复文件，并重新计算哈希。若哈希与基线一致，则说明恢复成功。

【截图 8：文件恢复页面】  
【截图 9：恢复后哈希验证通过】

## 8.8 文件篡改检测结果

运行命令：

```bash
python -m file_guard.cli simulate --case modify
python -m file_guard.cli scan --root demo_workspace/protected_files
```

系统检测到 `finance_report.txt` 当前 SHA-256 与基线 SHA-256 不一致，因此生成 `MODIFIED` 事件。

【截图 10：simulate modify 模拟篡改 finance_report.txt】  
【截图 11：scan 检测 MODIFIED 风险】

## 8.9 风险事件页面展示结果

风险事件页面展示事件类型、风险分值、风险等级、风险证据和防护建议。

【截图 12：风险事件页面】

## 8.10 报告导出页面展示结果

系统生成 JSON、CSV、HTML 报告文件。

【截图 13：报告导出页面】  
【截图 14：HTML 风险报告页面】

---

# 第 9 章 风险展示与分析

## 9.1 风险展示方法

本项目通过“风险对象、触发条件、风险证据、影响分析、风险评分、风险等级、防护建议、验证方法”八个方面展示风险。这样可以避免只展示“检测成功”，而是说明检测结果背后的安全含义。

## 9.2 风险案例一：账号文件被异常删除

1. 风险对象：`account_list.txt`，模拟账号清单文件。
2. 触发条件：执行删除模拟后，当前扫描中该文件不存在，但基线中存在。
3. 风险证据：事件类型为 `DELETED`，`old_hash` 存在，`new_hash` 为空，文件敏感等级为 `HIGH`，路径包含 `account`。
4. 影响分析：账号文件被删除可能导致账号资料不可用，并影响审计和恢复。
5. 风险评分：删除 +50，敏感关键词 +20，高敏感 +25，删除高敏感文件额外 +20，最高限制为 100。
6. 风险等级：`CRITICAL`。
7. 防护建议：立即从备份恢复，核查删除来源，限制敏感目录写权限，保留日志。
8. 本项目如何验证：通过 `simulate --case delete` 删除文件，再通过 `scan` 检测删除事件，最后通过 `restore` 恢复并校验哈希。

## 9.3 风险案例二：财务文件被篡改

1. 风险对象：`finance_report.txt`，模拟财务报告。
2. 触发条件：执行篡改模拟后，文件仍存在，但 SHA-256 与基线不同。
3. 风险证据：事件类型为 `MODIFIED`，`old_hash` 和 `new_hash` 不一致，文件敏感等级为 `HIGH`，路径包含 `finance`。
4. 影响分析：财务文件被篡改可能造成错误决策、数据污染和审计风险。
5. 风险评分：篡改 +35，敏感关键词 +20，高敏感 +25，篡改高敏感文件额外 +15，合计可达到 `CRITICAL`。
6. 风险等级：`CRITICAL`。
7. 防护建议：复核文件来源，从可信备份恢复，限制写权限。
8. 本项目如何验证：通过 `simulate --case modify` 修改内容，再通过 `scan` 对比哈希变化。

## 9.4 风险案例三：多个敏感文件批量变化

1. 风险对象：`finance_report.txt`、`contract_2025.txt`、`project_plan.txt` 等多个文件。
2. 触发条件：一次扫描中 3 个及以上文件发生新增、删除或修改。
3. 风险证据：系统生成多个 `MODIFIED` 事件，并补充生成 `BULK_CHANGE` 事件。
4. 影响分析：批量变化可能表示异常脚本、误操作或未授权程序行为，影响范围更大。
5. 风险评分：批量变化 +25，高敏感文件变化和敏感关键词继续叠加。
6. 风险等级：通常为 `HIGH` 或 `CRITICAL`。
7. 防护建议：暂停批量写入来源，逐项核对文件，优先恢复高敏感文件。
8. 本项目如何验证：通过 `simulate --case bulk` 批量修改多个文件，再执行扫描。

## 9.5 风险对象分析

系统根据文件名和路径识别敏感对象。账号、财务、合同等文件被判定为高敏感文件，是因为这些文件在真实场景中通常与身份、资金、责任和业务连续性相关。

## 9.6 触发条件分析

本项目触发风险的条件包括：文件不存在、文件哈希变化、新增可疑扩展名文件、多个文件同时变化等。这些条件都可以由程序自动判断，避免依赖人工主观判断。

## 9.7 风险证据分析

风险证据包括 `old_hash`、`new_hash`、`old_size`、`new_size`、敏感关键词、敏感等级和命中的评分规则。证据越完整，风险分析越具有说服力。

## 9.8 影响范围分析

单个低敏感文件变化影响较小，而高敏感文件删除或多个文件批量变化影响较大。系统通过敏感等级和批量变化规则体现影响范围差异。

## 9.9 风险等级判定依据

风险等级由分值决定：

- 0-29：LOW；
- 30-59：MEDIUM；
- 60-79：HIGH；
- 80-100：CRITICAL。

---

# 第 10 章 预防措施与防护建议

## 10.1 最小权限原则

敏感目录应限制写入权限，仅允许必要用户或程序修改文件。对于账号、财务、合同文件，应避免所有用户都拥有写权限。

## 10.2 定期备份策略

应定期备份高敏感文件，并保留多个版本。备份目录应与工作目录隔离，避免异常删除同时影响原文件和备份。

## 10.3 文件完整性监测

应定期计算文件哈希并与基线对比。对于重要文件，可以在每次修改前后记录哈希，以便判断内容是否被篡改。

## 10.4 删除保护与恢复验证

文件恢复后必须重新计算哈希。仅仅看到文件恢复存在并不代表内容可信，只有哈希与基线一致，才能证明恢复到可信版本。

## 10.5 日志审计与异常告警

系统应记录风险事件、检测时间、文件路径和风险证据。当出现高敏感文件删除、篡改或批量变化时，应进行告警。

## 10.6 高敏感文件分级管理

账号、财务、合同、客户名单等文件应标记为高敏感对象，并设置更严格的监测、备份和恢复策略。

## 10.7 项目改进方向

后续可以增加实时监控、更多文件类型识别、用户操作日志关联、备份版本管理和更细粒度的权限分析。

---

# 第 11 章 总结

## 11.1 项目完成情况

本项目完成了从演示数据生成、基线建立、异常模拟、风险检测、风险评分、备份恢复、恢复验证到报告导出的完整流程。系统提供 CLI 和 Web 两种交互方式，并具备测试用例。

## 11.2 项目创新点

项目将文件哈希基线、敏感等级识别、风险评分、恢复验证和 Web 可视化结合起来，使文件安全风险能够以证据链形式展示。

## 11.3 项目不足

当前系统主要用于本地课程演示，不具备实时监控能力，也没有接入真实系统审计日志。风险评分规则为课程演示设计，仍可进一步优化。

## 11.4 后续改进方向

可以加入定时扫描、文件变化实时监听、备份版本对比、用户操作审计和权限风险分析。

## 11.5 课程学习收获

通过本项目，可以理解文件完整性检测、哈希基线、风险评分、备份恢复和安全边界控制等知识点，也能体会到安全系统不仅要检测风险，还要提供证据、解释影响并给出可执行的防护建议。

---

## 附录 A：推荐演示命令

```bash
python -m file_guard.cli reset
python -m file_guard.cli demo-init
python -m file_guard.cli init --root demo_workspace/protected_files
python -m file_guard.cli simulate --case delete
python -m file_guard.cli scan --root demo_workspace/protected_files
python -m file_guard.cli restore --path account_list.txt
python -m file_guard.cli simulate --case modify
python -m file_guard.cli scan --root demo_workspace/protected_files
python -m file_guard.cli simulate --case bulk
python -m file_guard.cli scan --root demo_workspace/protected_files
python -m file_guard.cli report
python -m file_guard.cli web
```

---

## 附录 B：截图清单

1. 【截图 1：demo-init 初始化演示目录】
2. 【截图 2：init 初始化文件哈希基线】
3. 【截图 3：Web 首页仪表盘】
4. 【截图 4：基线文件列表页面】
5. 【截图 5：模拟风险页面】
6. 【截图 6：simulate delete 模拟删除 account_list.txt】
7. 【截图 7：scan 检测 DELETED 风险】
8. 【截图 8：文件恢复页面】
9. 【截图 9：恢复后哈希验证通过】
10. 【截图 10：simulate modify 模拟篡改 finance_report.txt】
11. 【截图 11：scan 检测 MODIFIED 风险】
12. 【截图 12：风险事件页面】
13. 【截图 13：报告导出页面】
14. 【截图 14：HTML 风险报告页面】

---

## 附录 C：可直接放入报告的项目贡献描述

本项目由本人基于 Python 标准库和 Flask 框架实现，核心检测逻辑未调用第三方安全工具。系统通过 `pathlib`、`hashlib`、`sqlite3`、`shutil`、`json`、`csv` 等标准库完成文件扫描、哈希计算、数据库存储、备份恢复和报告导出。项目重点体现了文件完整性检测、风险评分、恢复验证和可视化展示的完整闭环。

