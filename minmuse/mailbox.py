from __future__ import annotations
import imaplib
import hashlib
import ssl
from dataclasses import dataclass
from email import policy
from email.header import decode_header, make_header
from email.parser import BytesParser
from pathlib import Path
from .settings import Settings

@dataclass
class Mail:
    message_id: str
    sender: str
    subject: str
    date: str
    body: str

    @property
    def fingerprint(self) -> str:
        source = self.message_id or "\n".join((self.sender, self.subject, self.date, self.body))
        return hashlib.sha256(source.encode("utf-8", errors="replace")).hexdigest()


def _header(value: str | None) -> str:
    if not value:
        return "(无主题)"
    try:
        return str(make_header(decode_header(value)))
    except Exception:
        return value


def _text_body(message) -> str:
    chunks: list[str] = []
    parts = message.walk() if message.is_multipart() else [message]
    for part in parts:
        if part.get_content_disposition() == "attachment":
            continue
        if part.get_content_type() != "text/plain":
            continue
        try:
            content = part.get_content()
            if isinstance(content, str):
                chunks.append(content)
        except Exception:
            continue
    return "\n".join(chunks).strip()[:6000]


def parse_message(raw: bytes) -> Mail:
    msg = BytesParser(policy=policy.default).parsebytes(raw)
    sender = _header(msg.get("From"))
    return Mail(
        message_id=(msg.get("Message-ID") or "").strip(),
        sender=sender,
        subject=_header(msg.get("Subject")),
        date=str(msg.get("Date") or ""),
        body=_text_body(msg),
    )


class DemoMailbox:
    def __init__(self, fixture_dir: Path):
        self.fixture_dir = fixture_dir

    def fetch_unread(self, limit: int = 20) -> list[Mail]:
        files = sorted(self.fixture_dir.glob("*.eml"))[:limit]
        return [parse_message(path.read_bytes()) for path in files]


class ImapMailbox:
    """Fetch unread messages without changing the server-side Seen flag."""
    def __init__(self, settings: Settings):
        self.settings = settings

    def fetch_unread(self, limit: int = 20) -> list[Mail]:
        s = self.settings
        s.validate_imap()
        client = imaplib.IMAP4_SSL(s.imap_host, s.imap_port, ssl_context=ssl.create_default_context())
        try:
            client.login(s.imap_user, s.imap_password)
            status, _ = client.select(s.mailbox, readonly=True)
            if status != "OK":
                raise RuntimeError("IMAP could not open the configured mailbox")
            status, result = client.search(None, "UNSEEN")
            if status != "OK" or not result:
                return []
            ids = result[0].split()[-limit:]
            mails: list[Mail] = []
            for uid in ids:
                status, chunks = client.fetch(uid, "(BODY.PEEK[])")
                if status != "OK":
                    continue
                raw = next((item[1] for item in chunks if isinstance(item, tuple) and isinstance(item[1], bytes)), None)
                if raw:
                    mails.append(parse_message(raw))
            return mails
        finally:
            try:
                client.logout()
            except Exception:
                pass
