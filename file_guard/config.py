"""Project configuration constants."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEMO_WORKSPACE_DIR = PROJECT_ROOT / "demo_workspace"
PROTECTED_DIR = DEMO_WORKSPACE_DIR / "protected_files"
DATA_DIR = PROJECT_ROOT / "data"
BACKUP_DIR = DATA_DIR / "backups"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
DB_PATH = DATA_DIR / "file_guard.db"
LOG_PATH = OUTPUT_DIR / "run.log"

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 5000

SENSITIVE_KEYWORDS = [
    "password", "secret", "credential", "account", "finance", "contract",
    "财务", "合同", "账号", "密码", "凭据", "客户", "名单",
]

MEDIUM_KEYWORDS = [
    "report", "plan", "project", "note", "summary",
    "报告", "计划", "项目", "记录",
]

SUSPICIOUS_EXTENSIONS = [
    ".exe", ".bat", ".ps1", ".sh", ".vbs", ".cmd",
]
