# GitHub 上线与自然增长建议

## 仓库信息

- 建议仓库名：`minmuse-email-agent`
- 描述：A tiny inbox agent: IMAP read-only → LLM digest → SMTP to self, with a safe offline demo.
- Topics：`ai-agent` `email-automation` `imap` `smtp` `python` `llm` `self-hosted`
- License：MIT

## 发布前页面整理

1. README 首屏保留一句话、架构流程和 `python -m minmuse --demo`。
2. 放一个脱敏的离线演示截图，明确它使用虚构邮件。
3. 发布 4–5 分钟讲解视频，在简介里链接仓库；不要放服务器路径、邮箱地址或真实邮件画面。
4. 发布时列出清晰边界：默认 dry-run，只给自己发日报，IMAP 只读。
5. 收到 issue 后把实际需求拆成可复现的小功能，保持 demo 一直能跑。

流量无法保证；这个项目的可分享点是“一条命令离线复现 + 从邮件到日报的完整闭环 + 不会误发陌生人”。

**状态：**本地仓库内容在整理中，尚未创建或推送公开 GitHub 仓库。
