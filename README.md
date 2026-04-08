# Dida365 OpenAPI Skill

一个面向家庭助理与自动化场景的 Dida365 / TickTick OpenAPI skill。

这个仓库当前重点解决三件事：

- 稳定完成 OAuth2 认证
- 通过 CLI 创建、更新、完成和查询任务
- 在“提醒我 / 定时任务 / 周期提醒”场景下，默认创建滴答清单任务

## 适合谁

- 人类使用者：想要快速把提醒、待办、周期任务写入滴答清单
- Agent / AI 工具：需要一个可脚本化、可复用、可发布的滴答任务执行层

## 当前能力

- `auth`: 浏览器或手动粘贴 code 完成 OAuth2
- `projects`: 项目 CRUD 和项目数据读取
- `tasks`: 普通任务 CRUD、完成
- `inbox`: 收集箱 ID 解析、读取、写入
- `remind`: 面向提醒的快捷命令

## 公开仓库的密钥策略

这个项目当前会从两个位置读取认证信息：

1. 仓库根目录 `.env`
2. 用户目录 `~/.config/dida365-openapi/*.json`

其中：

- `.env` 通常包含 `DIDA365_CLIENT_ID` 和 `DIDA365_CLIENT_SECRET`
- `~/.config/dida365-openapi/*.json` 会保存 access token 以及缓存的 inbox `projectId`

这两个位置都属于敏感信息，不应提交到公开仓库。

发布前建议额外做两件事：

- 检查本地 `.env` 和 `~/.config/dida365-openapi/*.json` 中是否仍保留真实凭据
- 在 Dida365 开发者后台重新生成一套新的 `Client Secret`，确保开发期凭据不继续沿用到公开仓库后的环境

本仓库已通过 `.gitignore` 忽略：

- `.env`
- `__pycache__/`
- 本地 IDE / agent 配置目录

请复制 `.env.example` 为你自己的 `.env` 使用。

## 快速开始

1. 创建并填写本地 `.env`

```bash
cp .env.example .env
```

2. 认证

有浏览器：

```bash
uv run scripts/dida365_cli.py auth
```

无浏览器：

```bash
uv run scripts/dida365_cli.py auth --manual
```

3. 创建一个默认单次准时提醒

```bash
uv run scripts/dida365_cli.py remind create \
  --title "两分钟后喝水" \
  --at "2026-04-08 14:30:00"
```

默认行为：

- 默认放入收集箱
- 默认 `timeZone=Asia/Shanghai`
- 默认提醒触发器为 `TRIGGER:PT0S`
- 默认是单次提醒，不带重复规则

4. 创建一个周期提醒

```bash
uv run scripts/dida365_cli.py remind create \
  --title "每月调仓" \
  --at "2026-04-24 09:00:00" \
  --repeat-flag "RRULE:FREQ=MONTHLY;INTERVAL=1;BYMONTHDAY=24"
```

## 通过 GitHub / npx skills 安装

这个仓库的**根目录就是 skill 根目录**，也就是：

- 仓库根目录直接包含 `SKILL.md`
- `agents/`、`references/`、`scripts/` 都相对于仓库根目录放置

这意味着当安装器支持“从 GitHub repo 根路径安装 skill”时，不需要额外指定子目录。

如果你后续把它发布到 GitHub，安装器应直接指向仓库根目录，而不是某个 `skills/...` 子路径。

## 仓库结构

```text
.
├── README.md
├── .env.example
├── SKILL.md
├── agents/openai.yaml
├── references/api_summary.md
├── scripts/dida365_cli.py
└── tests/test_dida365_cli.py
```

## 面向 Agent 的约定

- 提醒、定时、周期任务默认必须落为滴答清单任务
- 若没有明确项目，优先写入收集箱
- “提醒我”类任务不要只写时间，还要带 `reminders`
- 默认单次提醒，但要保留 `repeatFlag` 周期能力

## Git Flow

本仓库使用简化版 Git Flow：

- `main`: 稳定可发布
- `develop`: 日常集成
- `feature/*`: 功能开发
- `release/*`: 发布准备
- `hotfix/*`: 线上修复

如果本机没有安装 `git-flow` 命令，也可以直接用原生 `git` 按上述分支命名工作。
