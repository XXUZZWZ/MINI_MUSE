# MinMuse

**A tiny, inspectable inbox agent:** read unread mail, classify and summarize it, then send one daily digest back to your own mailbox.

Inspired by the idea of a personal agent that keeps working in the background, MinMuse keeps the workflow deliberately small and visible:

```text
cron → IMAP read-only inbox scan → summarize/classify → local report → SMTP digest to self
```

MinMuse is an independent educational project. It does not use Meta Muse APIs or claim to reproduce Meta's system.

## What it does

- Reads only `UNSEEN` messages using IMAP `READONLY` and `BODY.PEEK[]`.
- Extracts plain text only; attachments and HTML are ignored.
- Summarizes and labels each message (work, study, billing, personal, other).
- Writes a Markdown digest and JSON audit record locally.
- Keeps hashed IDs for successfully sent items so the daily job does not repeat the same unread messages; a dry-run does not mark mail as processed.
- Can send the digest only to the same mailbox used for SMTP authentication.
- Defaults to dry-run. Sending requires both `--send` and `MINMUSE_SEND_ENABLED=true`.
- Offers an offline demo with fake sample emails; no credentials or network needed.

It does **not** autonomously reply to strangers, open links, download attachments, or execute instructions embedded in an email. Those are separate features and are intentionally outside this first build.

## Quick demo

Python 3.11+; no third-party packages are required.

```bash
python -m minmuse --demo
```

The demo reads the fake messages in `examples/fixtures/`, creates a digest under `data/outbox/`, and prints it. It never contacts an email server.

## Configure a mailbox

Copy `.env.example` to `.env` and fill in your provider's IMAP/SMTP host, ports, account, and app password. Never commit `.env`.

```bash
python -m minmuse --dry-run
```

Review the generated digest in `data/outbox/` before enabling sending. To send one digest to yourself:

```bash
MINMUSE_SEND_ENABLED=true python -m minmuse --send
```

The recipient is pinned to `SMTP_USER`; the program rejects a different `DIGEST_TO`. To schedule a daily run, use a cron entry only after a successful dry-run, for example:

```cron
0 8 * * * cd /path/to/MinMuse && /usr/bin/env MINMUSE_SEND_ENABLED=true /path/to/python -m minmuse --send >> data/minmuse.log 2>&1
```

Use a restricted mailbox or app password. Keep `.env`, logs, and generated reports private. Inbox bodies are untrusted input; the model is asked to summarize them, not follow their instructions.

## LLM configuration (optional)

Without an LLM key, the offline rule-based summarizer keeps the demo reproducible. For real inboxes, MinMuse can call any OpenAI-compatible chat-completions endpoint:

- `LLM_BASE_URL` (example: `https://api.example.com/v1`)
- `LLM_API_KEY`
- `LLM_MODEL`

Only message text is sent to that endpoint. If this is a concern, use a local OpenAI-compatible model server. The application never logs message bodies or API keys.

## Project map

- `minmuse/mailbox.py` — IMAP reader and sample mailbox
- `minmuse/summarizer.py` — offline rules plus OpenAI-compatible adapter
- `minmuse/agent.py` — workflow, digest generation, send gate
- `minmuse/settings.py` — environment configuration
- `docs/ARCHITECTURE.md` — flow and trust boundaries
- `docs/VIDEO_PLAN.md` — 4–5 minute episode outline
- `video/remotion/` — reproducible frame-based video renderer
- `video/subtitles.srt` — subtitles for the narrated episode

## Video walkthrough

The narrated 4-minute episode is rendered with Remotion from the same scene artwork and subtitle timings. See [video/remotion/README.md](video/remotion/README.md) for local rendering. The exported MP4 and generated voice WAV stay out of Git; the cover, script, subtitle timings, and renderer source are included.

## Security boundaries

- Read-only IMAP and a maximum message count/body size.
- No auto-replies to external senders.
- Outbound recipient must equal the authenticated SMTP mailbox.
- Sending is disabled unless the CLI flag and environment gate are both set.
- No secrets in the repo; `.env` and generated data are ignored by Git.

## License

MIT. See [LICENSE](LICENSE).
