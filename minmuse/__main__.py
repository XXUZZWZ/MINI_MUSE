from __future__ import annotations
import argparse
from pathlib import Path
from .agent import MinMuse
from .mailbox import DemoMailbox, ImapMailbox
from .settings import ROOT, Settings

def main() -> int:
    parser = argparse.ArgumentParser(description="MinMuse: summarize unread email and send a daily digest to yourself")
    parser.add_argument("--demo", action="store_true", help="use bundled fake emails; no network or credentials")
    parser.add_argument("--dry-run", action="store_true", help="create the local digest only (default)")
    parser.add_argument("--send", action="store_true", help="send the digest to the authenticated mailbox; requires a second env gate")
    args = parser.parse_args()
    if args.demo and args.send:
        parser.error("--demo never sends email")
    settings = Settings.from_env()
    if args.demo:
        mailbox = DemoMailbox(ROOT / "examples" / "fixtures")
        mails = mailbox.fetch_unread(limit=20)
    else:
        mailbox = ImapMailbox(settings)
        mails = mailbox.fetch_unread(limit=settings.max_messages)
    md_path, json_path, rows = MinMuse(settings).process(mails, send=args.send, deduplicate=not args.demo)
    print(f"Processed {len(rows)} message(s).")
    print(f"Digest: {md_path}")
    print(f"Audit JSON: {json_path}")
    if args.send:
        print("Digest sent to the authenticated mailbox.")
    else:
        print("Dry-run only; no email was sent.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
