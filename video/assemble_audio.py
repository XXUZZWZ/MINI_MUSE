from pathlib import Path
import json, wave
ROOT=Path(__file__).resolve().parent
PARTS=ROOT/'voice_parts'
LINES=[
('每天早上打开邮箱，真正耗时间的常常不是回复，而是判断：哪封重要，哪封要行动？','hook'),
('个人 Agent Muse 让人感兴趣的地方，是你交代目标后，它还能在后台继续把事情往前推。','muse'),
('这期不复刻大系统，只做一个叫 MinMuse 的最小版本：读未读邮件、整理成日报，再发回自己的邮箱。','muse'),
('先说明，MinMuse 是独立教学项目，不依赖 Meta Muse 服务，也不代表它的内部实现。','muse'),
('我通过 SSH 看了阿里云上的现有邮件程序：它每天用 SMTP 发提醒，但没有读取收件箱。','existing'),
('所以我们把新项目放在旁边，保留旧服务不动，只补上 IMAP 读取和 AI 整理这半条链路。','existing'),
('整个 Agent 可以画成五步：定时触发，读取邮件，模型整理，写出日报，最后发给自己。','flow'),
('Linux cron 每天固定时间启动 Python，不需要常驻大模型。','flow'),
('第二步连接 IMAP。账号和应用密码从环境变量读取，不写进代码，也不提交到 GitHub。','imap'),
('程序只搜索未读邮件，并用只读模式打开邮箱。取正文时用 BODY.PEEK，不把邮件改成已读。','imap'),
('为控制范围，第一版只取最近二十封，只提取纯文本；附件、网页链接和 HTML 都跳过。','imap'),
('接着 Agent 对每封邮件调用一个摘要器，输出类别、摘要、是否要处理，以及建议下一步。','agent'),
('有模型配置时，它调用 OpenAI 兼容接口；没配模型时，就走本地规则，离线示例也能跑。','agent'),
('注意，邮件正文是外部输入，不是给 Agent 下命令。模型只负责分类和摘要，没有浏览器或命令行工具。','agent'),
('样例里故意放了一封可疑邮件，正文要求忽略规则并索要密码。程序会把它标红为不可信内容，不照做。','security'),
('整理结果先写成本地 Markdown 日报和 JSON 记录。日志只记数量和文件路径，不打印邮箱正文或凭据。','report'),
('第五步通过 SMTP 把日报发回登录的那个邮箱。收件地址被锁定，不能让模型挑一个外部地址。','send'),
('而且默认 dry-run。只有命令里明确加上 send，同时环境开关也打开，程序才会发出邮件。','send'),
('这样第一版实现的是“自动收件、自动整理、自动给自己发摘要”，不会自动回复陌生人。','send'),
('来看演示。我运行 Python 模块的 demo 参数，用的是仓库里三封虚构样例，不联网，也不需要账号。','demo'),
('第一封被识别成工作邮件，提醒周五面试和需要准备的项目介绍。','demo'),
('第二封是账单通知。第三封尝试操控 Agent，被标成可疑指令，建议人工核对。','demo'),
('程序生成 Markdown 日报和 JSON。成功发送后，会记下邮件哈希，避免重复整理；dry-run 不记账也不发信。','demo'),
('接入邮箱前填好 IMAP、SMTP 和应用密码，先运行 --dry-run 检查。','setup'),
('确认内容正确后，再开启发送开关；日报收件人仍只能是邮箱账号本人。','setup'),
('阿里云单独部署 MinMuse，配置自己的虚拟环境、.env 和 cron。','deploy'),
('不要覆盖现有每日提醒程序。出问题时只删除 MinMuse 的 cron 行和目录，回滚边界很清楚。','deploy'),
('这个项目只有标准库，没有沉重框架。你可以从 mailbox、summarizer、agent 三个文件顺着读。','repo'),
('仓库带离线样例、架构图和部署说明，一条命令就能复现。','repo'),
('下一步可以加人工确认后的回复草稿、按主题归档、重复邮件去重；不要第一天就做全自动对外回复。','roadmap'),
('MinMuse 想讲清楚的只有一件事：Agent 不神秘，它是触发器、工具、模型、状态和边界组成的可检查流程。','close'),
('先在假邮件上跑通，再决定是否连接真实邮箱。','close'),
]
GAP=0.2
parts=[]
for i in range(len(LINES)):
    with wave.open(str(PARTS/f'{i+1:02d}.wav'),'rb') as w: parts.append((w.getparams(),w.readframes(w.getnframes())))
ref=parts[0][0]
if any((p.nchannels,p.sampwidth,p.framerate,p.comptype)!=(ref.nchannels,ref.sampwidth,ref.framerate,ref.comptype) for p,_ in parts): raise ValueError('Inconsistent WAV formats')
rate=ref.framerate; gap=int(rate*GAP); cursor=0; cues=[]
with wave.open(str(ROOT/'voice.wav'),'wb') as out:
    out.setparams(ref)
    for i,((_,data),(text,scene)) in enumerate(zip(parts,LINES)):
        frames=len(data)//ref.nchannels//ref.sampwidth; start,end=cursor/rate,(cursor+frames)/rate
        cues.append({'start':round(start,3),'end':round(end,3),'text':text,'scene':scene})
        out.writeframes(data); cursor+=frames
        if i<len(parts)-1: out.writeframes(b'\0'*gap*ref.nchannels*ref.sampwidth);cursor+=gap
length=cursor/rate
(ROOT/'timings.json').write_text(json.dumps({'duration':round(length,3),'cues':cues},ensure_ascii=False,indent=2),encoding='utf-8')
def stamp(t):
    ms=round(t*1000); h,ms=divmod(ms,3600000); m,ms=divmod(ms,60000); s,ms=divmod(ms,1000); return f'{h:02}:{m:02}:{s:02},{ms:03}'
srt=[]
for i,c in enumerate(cues):
    end=cues[i+1]['start'] if i+1<len(cues) else length
    srt += [str(i+1),f'{stamp(c["start"])} --> {stamp(end)}',c['text'],'']
(ROOT/'subtitles.srt').write_text('\n'.join(srt),encoding='utf-8-sig')
print(json.dumps({'duration_seconds':round(length,2),'cues':len(cues)},ensure_ascii=False))
