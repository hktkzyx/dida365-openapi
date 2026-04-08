# dida365-openapi

一个可直接安装运行的 Dida365 / TickTick OpenAPI 命令行工具，并附带一个可安装的 skill 包装层。

这个仓库有两层：

- 根目录：可通过 `uv tool install` 安装的 CLI 项目
- `skills/dida365-openapi/`：供 skill 安装器使用的 skill 目录

## 适合谁

- 人类使用者：想要快速把提醒、待办、周期任务写入滴答清单
- Agent / AI 工具：需要一个可脚本化、可复用、可发布的滴答任务执行层

## 当前 CLI 能力

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

## 环境变量管理

### 必需变量

- `DIDA365_CLIENT_ID`
- `DIDA365_CLIENT_SECRET`

### 常用变量

- `DIDA365_SERVICE_TYPE`
  - 可选：`dida365` / `ticktick`
  - 默认：`dida365`
- `DIDA365_REDIRECT_URI`
  - 默认：`http://127.0.0.1:8788/callback`

### 可选变量

- `DIDA365_SCOPE`
  - 默认：`tasks:read tasks:write`
- `DIDA365_TOKEN_FILE`
  - 自定义 token 文件位置
- `DIDA365_ACCESS_TOKEN`
  - 不建议手工长期维护；通常由 token 文件管理

### access token 默认存放位置

默认路径：

```text
~/.config/dida365-openapi/{service_type}-{client_id}.json
```

例如：

```text
~/.config/dida365-openapi/dida365-<client_id>.json
```

如果你想改位置，可以：

- 设置环境变量 `DIDA365_TOKEN_FILE`
- 或在命令行使用 `--token-file`

优先级：

1. `--token-file`
2. `DIDA365_TOKEN_FILE`
3. 默认路径

### 读取顺序

CLI 启动时当前实现会按下面顺序取配置：

1. 当前进程已有的系统环境变量
2. 当前工作目录 `.env`
3. 代码默认值

也就是说：

- 写在 `.zshrc` 里的 `export DIDA365_CLIENT_ID=...` **有用**
- 只要你是在加载过 `.zshrc` 的 shell 里运行 `dida365-openapi`，这些变量就会生效
- 如果系统环境变量和 `.env` 同时存在，**系统环境变量优先**

### 建议做法

对于公开仓库和长期维护，推荐：

- 把 `DIDA365_CLIENT_ID` / `DIDA365_CLIENT_SECRET` 放在本地 `.env`
- 不把真实密钥长期写进 `.zshrc`
- token 继续放在 `~/.config/dida365-openapi/`

这样最清晰，也最不容易误提交。

## 快速开始

1. 创建并填写本地 `.env`

```bash
cp .env.example .env
```

2. 安装 CLI

本地开发：

```bash
uv tool install .
```

运行：

```bash
dida365-openapi --help
```

3. 认证

有浏览器：

```bash
dida365-openapi auth
```

无浏览器：

```bash
dida365-openapi auth --manual
```

4. 创建一个默认单次准时提醒

```bash
dida365-openapi remind create \
  --title "两分钟后喝水" \
  --at "2026-04-08 14:30:00"
```

默认行为：

- 默认放入收集箱
- 默认 `timeZone=Asia/Shanghai`
- 默认提醒触发器为 `TRIGGER:PT0S`
- 默认是单次提醒，不带重复规则

5. 创建一个周期提醒

```bash
dida365-openapi remind create \
  --title "每月调仓" \
  --at "2026-04-24 09:00:00" \
  --repeat-flag "RRULE:FREQ=MONTHLY;INTERVAL=1;BYMONTHDAY=24"
```

## 通过 GitHub / skill 安装

这个仓库的 skill 目录在：

```text
skills/dida365-openapi/
```

因此发布到 GitHub 后，skill 安装器应指向这个子路径，而不是仓库根目录。

也就是说，仓库是 CLI 项目，`skills/dida365-openapi/` 是 skill 包装层。

## 发布到 GitHub 和 skills.sh

### 发布到 GitHub

1. 确认 `.env` 没有被提交
2. 确认 `~/.config/dida365-openapi/*.json` 不在仓库里
3. 建议在发布前去 Dida365 开发者后台重新生成新的 `Client Secret`
4. 在 GitHub 创建仓库，例如 `brooksyuan/dida365-openapi`
5. 添加远程并推送：

```bash
git remote add origin git@github.com:<owner>/dida365-openapi.git
git push -u origin main
git push -u origin develop
```

### 发布到 skills.sh

skills.sh 当前**没有单独的发布命令**。

实际做法就是：

1. 把 skill 放在一个公开 git 仓库里
2. 让别人能通过 `npx skills add` 安装
3. 一旦有人安装，它就可能通过安装遥测出现在 skills.sh

对这个仓库来说，skill 的安装路径应是：

```text
https://github.com/<owner>/dida365-openapi/tree/main/skills/dida365-openapi
```

也就是说，公开发布后，你需要分享的是：

- GitHub 仓库地址
- 或者这个 skill 子路径的 GitHub 地址

## 仓库结构

```text
.
├── README.md
├── .env.example
├── pyproject.toml
├── src/dida365_openapi/
├── tests/
└── skills/
    └── dida365-openapi/
        ├── SKILL.md
        ├── agents/openai.yaml
        └── references/api_summary.md
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
