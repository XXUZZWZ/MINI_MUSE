from __future__ import annotations
import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def _load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip().strip("\"'")
        os.environ.setdefault(key, value)

@dataclass(frozen=True)
class Settings:
    imap_host: str = ""
    imap_port: int = 993
    imap_user: str = ""
    imap_password: str = ""
    smtp_host: str = ""
    smtp_port: int = 465
    smtp_user: str = ""
    smtp_password: str = ""
    digest_to: str = ""
    mailbox: str = "INBOX"
    send_enabled: bool = False
    llm_base_url: str = ""
    llm_api_key: str = ""
    llm_model: str = ""
    output_dir: Path = ROOT / "data" / "outbox"
    max_messages: int = 20

    @classmethod
    def from_env(cls) -> "Settings":
        _load_dotenv(ROOT / ".env")
        env = os.environ
        return cls(
            imap_host=env.get("IMAP_HOST", ""), imap_port=int(env.get("IMAP_PORT", "993")),
            imap_user=env.get("IMAP_USER", ""), imap_password=env.get("IMAP_PASSWORD", ""),
            smtp_host=env.get("SMTP_HOST", ""), smtp_port=int(env.get("SMTP_PORT", "465")),
            smtp_user=env.get("SMTP_USER", ""), smtp_password=env.get("SMTP_PASSWORD", ""),
            digest_to=env.get("DIGEST_TO", ""), mailbox=env.get("IMAP_MAILBOX", "INBOX"),
            send_enabled=env.get("MINMUSE_SEND_ENABLED", "false").lower() == "true",
            llm_base_url=env.get("LLM_BASE_URL", "").rstrip("/"), llm_api_key=env.get("LLM_API_KEY", ""),
            llm_model=env.get("LLM_MODEL", ""), output_dir=Path(env.get("MINMUSE_OUTPUT_DIR", str(ROOT / "data" / "outbox"))),
            max_messages=max(1, min(100, int(env.get("MINMUSE_MAX_MESSAGES", "20")))),
        )

    def validate_imap(self) -> None:
        missing = [name for name, value in (("IMAP_HOST", self.imap_host), ("IMAP_USER", self.imap_user), ("IMAP_PASSWORD", self.imap_password)) if not value]
        if missing:
            raise ValueError("Missing mailbox settings: " + ", ".join(missing))

    def validate_smtp(self) -> None:
        missing = [name for name, value in (("SMTP_HOST", self.smtp_host), ("SMTP_USER", self.smtp_user), ("SMTP_PASSWORD", self.smtp_password)) if not value]
        if missing:
            raise ValueError("Missing mail-send settings: " + ", ".join(missing))
        if not self.digest_to or self.digest_to.casefold() != self.smtp_user.casefold():
            raise ValueError("DIGEST_TO must match SMTP_USER; MinMuse only sends the digest back to its own mailbox.")
