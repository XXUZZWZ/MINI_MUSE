# 阿里云独立部署草案

已只读检查服务器：当前每日任务提醒使用 SMTP 外发；MinMuse 第一版需要 IMAP 收件箱读取，二者是不同工作流。此部署建议放到独立目录 `/opt/minmuse`，独立 `.env` 和 cron，不修改当前提醒服务。

## 上线前顺序

1. 先在本地运行 `python -m minmuse --demo`。
2. 在服务器独立目录创建 Python 3.11+ 虚拟环境并上传干净源码，不上传 `.env`、日志、真实邮件和输出目录。
3. 配置邮箱提供商的 IMAP/SMTP 主机和专用应用密码，文件权限设为 `600`。
4. 运行 `python -m minmuse --dry-run`，人工查看日报是否分类正确。
5. 先手动启用发送闸门，只发到认证账号自身的邮箱，确认成功后再添加单独的每日 cron。
6. 观察日志与日报几天后再决定是否常驻。

## 独立 cron 模板

```cron
0 8 * * * cd /opt/minmuse && /opt/minmuse/.venv/bin/python -m minmuse --send >> /opt/minmuse/data/minmuse.log 2>&1
```

`.env` 中 `MINMUSE_SEND_ENABLED=true` 仍是第二道发送条件。此 cron 不会编辑或覆盖服务器现有的每日邮件任务。部署前应检查服务器本地时区和现有 cron 的实际运行时间。

## 回滚

移除 MinMuse 自己的 cron 行并停止其进程即可；现有每日提醒目录与定时任务保持独立。

**此文档是待执行方案，当前尚未向阿里云上传或部署任何 MinMuse 文件。**
