from __future__ import annotations
import json
import smtplib
import ssl
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path
from .mailbox import Mail
from .settings import Settings
from .summarizer import Analysis, OpenAICompatibleSummarizer

class MinMuse:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.summarizer = OpenAICompatibleSummarizer(settings)

    def process(self, mails: list[Mail], *, send: bool = False, deduplicate: bool = True) -> tuple[Path, Path, list[dict]]:
        processed_path = self.settings.output_dir.parent / "processed_ids.json"
        processed = set()
        if deduplicate and processed_path.exists():
            try:
                processed = set(json.loads(processed_path.read_text(encoding="utf-8")))
            except (OSError, ValueError, TypeError):
                processed = set()
        fresh = [mail for mail in mails if not deduplicate or mail.fingerprint not in processed]
        rows: list[dict] = []
        for mail in fresh:
            analysis = self.summarizer.summarize(mail)
            rows.append({"mail": {"sender": mail.sender,
                                   "subject": mail.subject, "date": mail.date},
                         "analysis": analysis.__dict__})
        today = datetime.now().astimezone().strftime("%Y-%m-%d")
        self.settings.output_dir.mkdir(parents=True, exist_ok=True)
        json_path = self.settings.output_dir / f"digest-{today}.json"
        md_path = self.settings.output_dir / f"digest-{today}.md"
        json_path.write_text(json.dumps({"date": today, "count": len(rows), "items": rows}, ensure_ascii=False, indent=2), encoding="utf-8")
        md_path.write_text(self.render_markdown(today, rows), encoding="utf-8")
        if send:
            self.send_to_self(today, md_path.read_text(encoding="utf-8"))
            if deduplicate and fresh:
                processed.update(mail.fingerprint for mail in fresh)
                processed_path.parent.mkdir(parents=True, exist_ok=True)
                processed_path.write_text(json.dumps(sorted(processed)[-5000:], indent=2), encoding="utf-8")
        return md_path, json_path, rows

    @staticmethod
    def render_markdown(today: str, rows: list[dict]) -> str:
        lines = [f"# 收件箱日报 · {today}", "", f"共整理 **{len(rows)}** 封未读邮件。", ""]
        if not rows:
            lines += ["今天没有新的、尚未整理的未读邮件。", ""]
        for i, row in enumerate(rows, 1):
            mail, analysis = row["mail"], row["analysis"]
            marker = "🔴" if analysis.get("priority") == "high" else "📩"
            lines += [f"## {i}. {marker} [{analysis['category']}] {mail['subject']}",
                      f"- 发件人：{mail['sender']}", f"- 摘要：{analysis['summary']}",
                      f"- 需要处理：{'是' if analysis['action_required'] else '否'}",
                      f"- 建议：{analysis['suggested_next_step']}", ""]
        lines += ["---", "由 MinMuse 自动整理。原始邮件内容未写入日志。", ""]
        return "\n".join(lines)

    def send_to_self(self, today: str, markdown: str) -> None:
        s = self.settings
        if not s.send_enabled:
            raise RuntimeError("Sending is disabled. Set MINMUSE_SEND_ENABLED=true and pass --send explicitly.")
        s.validate_smtp()
        message = EmailMessage()
        message["From"] = s.smtp_user
        message["To"] = s.smtp_user
        message["Subject"] = f"MinMuse 收件箱日报 · {today}"
        message.set_content(markdown)
        context = ssl.create_default_context()
        if s.smtp_port == 465:
            with smtplib.SMTP_SSL(s.smtp_host, s.smtp_port, context=context, timeout=30) as client:
                client.login(s.smtp_user, s.smtp_password)
                client.send_message(message, to_addrs=[s.smtp_user])
        else:
            with smtplib.SMTP(s.smtp_host, s.smtp_port, timeout=30) as client:
                client.ehlo(); client.starttls(context=context); client.ehlo()
                client.login(s.smtp_user, s.smtp_password)
                client.send_message(message, to_addrs=[s.smtp_user])
