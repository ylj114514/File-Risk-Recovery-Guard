# 课程 PDF 报告补充部分

报告题目：《基于文件哈希基线的敏感文件异常删除、篡改检测与恢复验证系统》  
副标题：面向本地敏感文件安全风险的可视化验证与防护分析

---

## 摘要

随着本地文件在课程学习、个人办公和小型业务场景中的广泛使用，敏感文件的完整性和可用性逐渐成为网络信息安全风险管理中的基础问题。账号清单、财务报告、合同资料和项目计划等文件虽然通常存放在本地目录中，但一旦发生异常删除、内容篡改或批量变化，仍可能造成数据不可用、内容不可信、恢复困难和安全审计证据缺失等风险。针对这一问题，本文设计并实现了一个基于文件哈希基线的本地敏感文件风险验证系统 File-Risk-Recovery-Guard。

本项目以 `demo_workspace/protected_files` 目录中的模拟敏感文件为风险对象，通过 Python 编程实现文件扫描、SHA-256 哈希计算、文件基线建立、SQLite 数据库存储、风险事件检测、风险评分、备份恢复和恢复后哈希校验等功能。系统能够检测文件被删除、文件内容被篡改、多个文件批量异常变化以及新增可疑扩展名文件等风险事件，并根据事件类型、敏感关键词、文件敏感等级、批量变化情况等规则计算风险分值，将风险划分为 LOW、MEDIUM、HIGH 和 CRITICAL 等级。

在系统功能实现方面，本项目同时提供 CLI 命令行演示入口和 Flask Web 可视化界面。CLI 用于展示完整的初始化、模拟、扫描、恢复和报告导出流程；Web 前端用于展示基线文件、风险事件、风险等级分布、恢复验证结果和报告导出状态。系统还支持导出 JSON、CSV 和 HTML 风险报告，便于后续分析和课程报告截图。

执行结果表明，系统能够正确识别 `account_list.txt` 被异常删除时产生的 DELETED 风险事件，能够识别 `finance_report.txt` 内容被修改时产生的 MODIFIED 风险事件，也能够在多个文件同时变化时生成 BULK_CHANGE 风险事件。对于被删除或篡改的文件，系统可以从备份目录恢复，并重新计算 SHA-256 哈希与基线哈希进行比对，验证恢复结果是否可信。

本项目的风险展示不仅停留在程序运行成功层面，而是通过文件路径、旧哈希、新哈希、文件大小、敏感等级、风险规则、风险分值和防护建议形成完整证据链。该系统说明了文件完整性保护、定期备份、最小权限控制、恢复后校验和日志审计在本地敏感文件防护中的重要意义。通过本项目，可以较完整地展示本地敏感文件异常删除与篡改风险的检测、分析和恢复验证过程。

---

## 关键词

文件完整性；哈希基线；异常删除检测；风险评分；恢复验证；可视化展示

---

## 目录

摘要  
关键词  

第 1 章 选题背景与研究目标  
1.1 课程作业背景  
1.2 文件异常删除与篡改风险背景  
1.3 本项目研究对象  
1.4 本项目实现目标  
1.5 本项目与课程要求的对应关系  

第 2 章 风险场景说明  
2.1 敏感文件异常删除风险  
2.2 敏感文件内容篡改风险  
2.3 多文件批量异常变化风险  
2.4 文件恢复失败风险  
2.5 风险影响分析  

第 3 章 系统需求分析  
3.1 功能需求  
3.2 非功能需求  
3.3 安全边界  
3.4 运行环境  
3.5 测试与演示需求  

第 4 章 系统总体设计  
4.1 系统总体架构  
4.2 后端检测引擎设计  
4.3 数据库存储设计  
4.4 命令行交互设计  
4.5 Web 前端可视化设计  
4.6 系统运行流程  
4.7 数据流设计  

第 5 章 数据库设计  
5.1 baseline_files 表设计  
5.2 risk_events 表设计  
5.3 backups 表设计  
5.4 数据库读写流程  
5.5 数据库在风险证据保存中的作用  

第 6 章 核心模块实现  
6.1 文件扫描与 SHA-256 哈希计算模块  
6.2 文件敏感等级识别模块  
6.3 文件哈希基线管理模块  
6.4 删除与篡改检测模块  
6.5 批量变更检测模块  
6.6 风险评分与等级判定模块  
6.7 文件备份与恢复验证模块  
6.8 报告导出模块  
6.9 命令行入口模块  
6.10 Web 可视化模块  

第 7 章 Web 前端可视化设计  
7.1 前端设计目标  
7.2 页面结构设计  
7.3 仪表盘页面设计  
7.4 基线文件页面设计  
7.5 风险事件页面设计  
7.6 模拟风险页面设计  
7.7 文件恢复页面设计  
7.8 报告导出页面设计  
7.9 前端对风险展示的增强作用  

第 8 章 执行结果展示  
8.1 演示目录初始化结果  
8.2 文件基线初始化结果  
8.3 模拟文件删除结果  
8.4 删除风险检测结果  
8.5 文件恢复验证结果  
8.6 模拟文件篡改结果  
8.7 篡改风险检测结果  
8.8 批量变更检测结果  
8.9 Web 仪表盘展示结果  
8.10 风险事件页面展示结果  
8.11 HTML 报告导出结果  

第 9 章 风险展示与分析  
9.1 风险展示方法  
9.2 风险案例一：账号文件被异常删除  
9.3 风险案例二：财务文件被篡改  
9.4 风险案例三：多个敏感文件批量变化  
9.5 风险对象分析  
9.6 触发条件分析  
9.7 风险证据分析  
9.8 影响范围分析  
9.9 风险等级判定依据  

第 10 章 预防措施与防护建议  
10.1 最小权限原则  
10.2 定期备份策略  
10.3 文件完整性监测  
10.4 删除保护与恢复验证  
10.5 日志审计与异常告警  
10.6 高敏感文件分级管理  
10.7 项目改进方向  

第 11 章 总结  
11.1 项目完成情况  
11.2 项目创新点  
11.3 项目不足  
11.4 后续改进方向  
11.5 课程学习收获  

参考文献  

---

## 结论

本文围绕本地敏感文件异常删除、篡改和恢复风险，设计并实现了一个基于文件哈希基线的风险验证系统 File-Risk-Recovery-Guard。系统完成了演示目录创建、模拟敏感文件生成、文件扫描、SHA-256 哈希计算、基线保存、自动备份、异常变化检测、风险评分、文件恢复、恢复后哈希验证、风险报告导出和 Web 可视化展示等功能，形成了从风险发生、风险检测、风险分析到恢复验证的完整闭环。

在风险展示方面，系统重点验证了三类典型风险。第一，账号文件 `account_list.txt` 被异常删除时，系统能够通过“基线中存在、当前扫描缺失”的条件识别 DELETED 事件，并结合 account 敏感关键词和 HIGH 敏感等级将其判定为 CRITICAL 风险。第二，财务文件 `finance_report.txt` 被篡改时，系统能够通过当前 SHA-256 与基线 SHA-256 不一致识别 MODIFIED 事件，说明文件内容完整性遭到破坏。第三，当多个敏感文件在同一次扫描中发生变化时，系统能够识别 BULK_CHANGE 风险，体现批量异常变化对影响范围和处置优先级的提升。

在恢复验证方面，系统不是简单地将备份文件复制回受保护目录，而是在恢复后重新计算文件 SHA-256，并与数据库中保存的基线哈希进行比对。只有恢复后哈希与基线哈希一致，系统才判定恢复验证通过。该设计说明，安全恢复不仅要关注文件是否重新出现，还要确认恢复后的内容是否与可信基线一致。

从防护意义上看，本项目说明了文件完整性监测、基线管理、定期备份、最小权限控制、日志审计和恢复后校验的重要性。对于账号、财务、合同等高敏感文件，仅依靠人工查看文件是否存在是不够的，还需要通过哈希基线和风险评分机制识别内容变化和异常行为。同时，Web 可视化界面和 HTML 报告导出功能增强了风险展示效果，使风险对象、风险证据、风险等级和防护建议能够更清晰地呈现。

本项目仍有进一步改进空间。当前系统主要面向本地课程演示，采用主动扫描方式检测风险，后续可以增加实时文件系统监听、备份版本管理、用户操作日志关联、权限变更分析和自动告警机制。还可以进一步完善敏感文件识别策略，引入更细粒度的文件分类和风险规则，使系统更接近真实环境中的文件完整性监测工具。

综上，本项目通过自主编程实现了一个具有明确风险场景、完整检测流程、可视化结果和恢复验证能力的本地敏感文件安全风险验证系统，较好地体现了网络信息安全风险技术编程课程对“风险识别、系统实现、运行结果、风险分析和防护建议”的综合要求。

---

## 参考文献建议

正式 PDF 中可根据学校格式调整为 GB/T 7714 或课程要求格式。以下为建议参考资料：

[1] Python Software Foundation. Python 3 Documentation: hashlib — Secure hashes and message digests[EB/OL]. https://docs.python.org/3/library/hashlib.html.

[2] Python Software Foundation. Python 3 Documentation: sqlite3 — DB-API 2.0 interface for SQLite databases[EB/OL]. https://docs.python.org/3/library/sqlite3.html.

[3] Python Software Foundation. Python 3 Documentation: pathlib — Object-oriented filesystem paths[EB/OL]. https://docs.python.org/3/library/pathlib.html.

[4] Pallets Projects. Flask Documentation[EB/OL]. https://flask.palletsprojects.com/.

[5] SQLite Consortium. SQLite Documentation[EB/OL]. https://www.sqlite.org/docs.html.

[6] National Institute of Standards and Technology. Security and Privacy Controls for Information Systems and Organizations, NIST Special Publication 800-53 Revision 5[S]. 2020.

[7] National Institute of Standards and Technology. Guide for Conducting Risk Assessments, NIST Special Publication 800-30 Revision 1[S]. 2012.

[8] National Institute of Standards and Technology. Contingency Planning Guide for Federal Information Systems, NIST Special Publication 800-34 Revision 1[S]. 2010.

[9] OWASP Foundation. OWASP Secure Coding Practices Quick Reference Guide[EB/OL]. https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/.

[10] OWASP Foundation. OWASP Cheat Sheet Series: File Upload Cheat Sheet and Logging Cheat Sheet[EB/OL]. https://cheatsheetseries.owasp.org/.

[11] Schneier B. Applied Cryptography: Protocols, Algorithms, and Source Code in C[M]. 2nd ed. New York: Wiley, 1996.

[12] Stallings W. Cryptography and Network Security: Principles and Practice[M]. 8th ed. Pearson, 2020.

