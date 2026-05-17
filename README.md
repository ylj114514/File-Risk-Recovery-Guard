# File-Risk-Recovery-Guard

## 项目简介

《基于文件哈希基线的敏感文件异常删除、篡改检测与恢复验证系统》是一个面向课程作业的本地安全风险验证项目。系统通过 SHA-256 文件哈希基线、SQLite 存储、风险评分、备份恢复和 Flask Web 可视化界面，展示敏感文件被异常删除、篡改、批量修改或新增可疑脚本文件时的检测与恢复过程。

副标题：面向本地敏感文件安全风险的可视化验证与防护分析。

## 课程作业背景

本项目服务于“网络信息安全风险技术编程”课程平时作业。重点不是调用现成攻击工具，而是围绕一个明确风险场景完成可运行、可展示、可分析的防御性系统。项目输出包括源码、命令行运行结果、Web 可视化页面、风险报告导出、测试用例和报告辅助文档。

## 选题方向

选题方向是“文件异常删除/恢复风险验证与防护分析”。本地敏感文件一旦被误删、恶意删除或篡改，可能造成资料不可用、审计证据丢失、业务数据被污染等问题。文件哈希基线可以让变化可测，备份恢复和哈希校验可以让恢复结果可验证。

## 安全边界

- 只操作项目目录下的 `demo_workspace/protected_files/`。
- 不扫描真实系统敏感目录。
- 不删除真实用户文件。
- 不访问外部网络。
- 不调用第三方攻击工具。
- 不实现木马、后门、键盘记录、密码窃取、漏洞利用或远程控制。
- 新增 `suspicious.ps1` 只写入无害文本，不执行。
- Web 服务默认只监听 `127.0.0.1`。
- 所有恢复路径都禁止 `../` 和绝对路径。

## 项目功能

- 创建演示工作区和模拟敏感文件。
- 初始化文件哈希基线。
- 自动备份基线文件。
- 模拟删除、篡改、批量变化和新增可疑扩展名文件。
- 检测 `CREATED`、`MODIFIED`、`DELETED`、`SUSPICIOUS_EXTENSION`、`HIGH_SENSITIVE_CHANGED`、`BULK_CHANGE`。
- 根据规则计算风险分值和风险等级。
- 保存风险事件到 SQLite。
- 从备份恢复文件并进行 SHA-256 校验。
- 导出 JSON、CSV、HTML 风险报告。
- 提供 CLI 和 Web 两种演示入口。
- 提供 pytest 测试用例。

## 项目结构

```text
file-risk-recovery-guard/
├── file_guard/
│   ├── scanner.py      # 文件扫描与 SHA-256
│   ├── baseline.py     # SQLite 基线数据库
│   ├── detector.py     # 删除、篡改、新增、批量变化检测
│   ├── risk_engine.py  # 风险评分与建议生成
│   ├── backup.py       # 备份、恢复、校验
│   ├── reporter.py     # JSON、CSV、HTML 报告
│   ├── demo.py         # 演示数据与安全模拟
│   ├── cli.py          # 命令行入口
│   └── web/            # Flask + Jinja2 + 原生前端
├── tests/              # pytest 测试
├── demo_workspace/     # 受保护演示目录
├── data/               # SQLite 与备份
├── outputs/            # 报告输出
└── docs/               # 课程报告辅助文档
```

## 安装方法

```bash
cd file-risk-recovery-guard
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
pip install -r requirements.txt
```

macOS/Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## CLI 使用方式

```bash
python -m file_guard.cli demo-init
python -m file_guard.cli init --root demo_workspace/protected_files
python -m file_guard.cli simulate --case delete
python -m file_guard.cli scan --root demo_workspace/protected_files
python -m file_guard.cli restore --path account_list.txt
python -m file_guard.cli simulate --case modify
python -m file_guard.cli scan --root demo_workspace/protected_files
python -m file_guard.cli simulate --case bulk
python -m file_guard.cli scan --root demo_workspace/protected_files
python -m file_guard.cli simulate --case suspicious
python -m file_guard.cli scan --root demo_workspace/protected_files
python -m file_guard.cli report
```

启动 Web：

```bash
python -m file_guard.cli web
```

访问：

```text
http://127.0.0.1:5000
```

## Web 前端使用方式

1. 打开仪表盘。
2. 点击“创建演示环境”。
3. 点击“初始化基线”。
4. 查看“基线文件”页面。
5. 在“模拟风险”页面执行删除、篡改、批量变化或新增可疑脚本模拟。
6. 在“扫描检测”页面执行扫描。
7. 在“风险事件”页面查看详情。
8. 在“文件恢复”页面输入 `account_list.txt` 进行恢复验证。
9. 在“报告导出”页面生成 JSON、CSV 和 HTML 报告。

## 风险评分规则

- `DELETED`：+50
- `MODIFIED`：+35
- `CREATED`：+15
- `SUSPICIOUS_EXTENSION`：+45
- `HIGH_SENSITIVE_CHANGED`：+25
- `BULK_CHANGE`：+25
- 文件名或路径包含敏感关键词：+20
- 文件敏感等级为 `HIGH`：+25
- 文件敏感等级为 `MEDIUM`：+10
- 可疑扩展名：+30
- 文件大小变为 0：+25
- 批量变化数量达到 3 个及以上：+25
- 删除高敏感文件额外：+20
- 篡改高敏感文件额外：+15
- 最高分限制：100

风险等级：

- 0-29：LOW
- 30-59：MEDIUM
- 60-79：HIGH
- 80-100：CRITICAL

## 运行演示流程

推荐截图流程：

```bash
python -m file_guard.cli reset
python -m file_guard.cli init --root demo_workspace/protected_files
python -m file_guard.cli simulate --case delete
python -m file_guard.cli scan --root demo_workspace/protected_files
python -m file_guard.cli restore --path account_list.txt
python -m file_guard.cli simulate --case modify
python -m file_guard.cli scan --root demo_workspace/protected_files
python -m file_guard.cli report
python -m file_guard.cli web
```

## 截图建议

- CLI 初始化基线结果。
- CLI 删除模拟和扫描结果。
- Web 仪表盘统计卡片。
- 基线文件列表。
- 风险事件详情展开。
- 文件恢复哈希校验通过。
- HTML 风险报告页面。

## 预防措施总结

- 对敏感目录建立哈希基线并定期扫描。
- 对高敏感文件实施最小权限写入。
- 对删除和批量修改操作进行日志审计。
- 建立离线或只读备份。
- 恢复后必须重新计算哈希并与基线比对。
- 禁止在敏感目录中存放不明脚本或可执行文件。

## 常见问题

`scan` 发现所有文件都是 `CREATED`：通常是还没有执行 `init` 初始化基线。

恢复失败：请确认已经执行过 `init`，并且 `data/backups/` 中存在备份文件。

Web 无法访问：确认服务监听地址是 `http://127.0.0.1:5000`，并且端口未被占用。

报告为空：说明数据库中暂无风险事件，可以先执行一次模拟和扫描。

## 注意事项

本项目只用于课程作业和防御性风险验证，不具备攻击功能。请不要把演示目录改成真实系统目录，不要执行模拟创建的脚本文件，不要将 Web 默认监听地址改为公网地址。
