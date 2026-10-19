<!-- ai-bridge -->
# scraper — AI 工作说明（Claude & Codex 共用）

> Codex 自动读本文件；Claude Code 通过 CLAUDE.md 导入本文件。改这里两边同时生效。

**一句话**：公开仓库，目前只有一个空的 scraper.py 占位。

**开工先读**：
- （无）
- `.ai/HANDOFF.md`（最新交接在最上面）

**公开**仓库，目前只有一个空的 `scraper.py`。开始写之前先问 Franz 要抓什么。
因为是公开仓库，交接记录里不要写客户信息、网址凭据或私人内容。

## Claude ↔ Codex 交接协议（ai-bridge）

Franz 同时用 Claude 和 Codex；一边 token 用完就切到另一边。规则：**交接靠仓库里的文件，不靠记忆**。

**开工 / 刚切换过来**
1. 有 ai-bridge MCP：调用 `resume(project="scraper", agent="<claude|codex>")`。
2. 没有：`git pull`，读 `.ai/HANDOFF.md` 最上面的一条，按“下一步”继续。

**收工 / token 快用完（剩 ~15% 就做，别等用光）**
1. 有 ai-bridge MCP：调用 `checkpoint(project="scraper", agent=..., title=..., done=[...], next_steps=[...], open_issues=[...])`，它会写交接、commit、push。
2. 没有：在 `.ai/HANDOFF.md` 顶部按下面格式加一条，`git add -A && git commit -m "[claude] checkpoint: …" && git push`。

```
## YYYY-MM-DD HH:MM · [claude|codex] · 一句话标题

- 完成：…
- 改动文件：…
- 下一步：具体到文件/函数/命令，另一个 AI 不用问 Franz 就能继续
- 未解决/注意：…
```

- 提交信息用 `[claude]` / `[codex]` 前缀。
- 不提交 `.env`、密钥、token、数据库文件。
- 想了解 Franz 的其他项目：`project_brief(name)` / `list_projects()`。
