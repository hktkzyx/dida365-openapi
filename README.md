# dida365-openapi

一个用于 Dida365 / TickTick OpenAPI 的命令行工具，也附带可供 agent 使用的 skill。

适合两类场景：

- 你自己在终端里创建项目、任务、提醒
- AI agent 通过 CLI 或 skill 调用 Dida365 / TickTick

## 安装 CLI

推荐直接从 PyPI 安装：

```bash
uv tool install dida365-openapi
```

也可以使用：

```bash
pipx install dida365-openapi
```

安装后可直接使用：

```bash
dida365-openapi --help
```

如果你要看源码或参与开发：

```bash
git clone https://github.com/hktkzyx/dida365-openapi.git
```

## 安装 Skill

如果你想把它作为 skill 给 agent 使用，可以通过 `npx skills` 安装仓库里的 skill 目录：

```bash
npx skills add https://github.com/hktkzyx/dida365-openapi --skill dida365-openapi
```

仓库里的 skill 目录是：

```text
skills/dida365-openapi/
```

## 获取 OpenAPI 凭据

你需要先在 Dida365 / TickTick 的开发者后台创建应用，拿到：

- `Client ID`
- `Client Secret`

开发者入口：

- Dida365: `https://developer.dida365.com/`
- TickTick: `https://developer.ticktick.com/`

创建应用时，回调地址可填写：

```text
http://127.0.0.1:8788/callback
```

## 配置

至少需要这两个环境变量：

- `DIDA365_CLIENT_ID`
- `DIDA365_CLIENT_SECRET`

常用可选项：

- `DIDA365_SERVICE_TYPE`
  - `dida365` / `ticktick`
  - 默认 `dida365`
- `DIDA365_REDIRECT_URI`
  - 默认 `http://127.0.0.1:8788/callback`
- `DIDA365_SCOPE`
  - 默认 `tasks:read tasks:write`
- `DIDA365_TOKEN_FILE`
  - 自定义 token 文件位置
- `DIDA365_ENV_FILE`
  - 显式指定 `.env` 文件路径

推荐把配置写到：

```text
~/.config/dida365-openapi/.env
```

例如：

```bash
mkdir -p ~/.config/dida365-openapi
cat > ~/.config/dida365-openapi/.env <<'EOF'
DIDA365_CLIENT_ID=your_client_id
DIDA365_CLIENT_SECRET=your_client_secret
DIDA365_SERVICE_TYPE=dida365
DIDA365_REDIRECT_URI=http://127.0.0.1:8788/callback
EOF
```

把 `your_client_id` 和 `your_client_secret` 替换成你在开发者后台拿到的值。

## `.env` 读取顺序

CLI 会按下面顺序取配置：

1. 当前进程环境变量
2. `--env-file /absolute/path/to/.env`
3. `DIDA365_ENV_FILE=/absolute/path/to/.env`
4. `~/.config/dida365-openapi/.env`
5. 当前工作目录 `.env`
6. 默认值

这意味着：

- 普通用户通常只需要维护 `~/.config/dida365-openapi/.env`
- agent 在不同项目目录下运行时，默认也能复用同一套配置
- 只有多账号或隔离场景，才需要显式传 `--env-file`

## 首次认证

有浏览器时：

```bash
dida365-openapi auth
```

无浏览器时：

```bash
dida365-openapi auth --manual
```

认证成功后，token 默认保存在：

```text
~/.config/dida365-openapi/{service_type}-{client_id}.json
```

## 常见用法

查看项目：

```bash
dida365-openapi projects list
```

新建项目：

```bash
dida365-openapi projects create --name "工作"
```

查看项目内任务：

```bash
dida365-openapi tasks list --project-id your_project_id
```

创建任务：

```bash
dida365-openapi tasks create \
  --project-id your_project_id \
  --title "写周报"
```

创建单次提醒：

```bash
dida365-openapi remind create \
  --title "两分钟后喝水" \
  --at "2026-04-08 14:30:00"
```

创建周期提醒：

```bash
dida365-openapi remind create \
  --title "每月调仓" \
  --at "2026-04-24 09:00:00" \
  --repeat-flag "RRULE:FREQ=MONTHLY;INTERVAL=1;BYMONTHDAY=24"
```

更多参数：

```bash
dida365-openapi --help
dida365-openapi tasks --help
dida365-openapi remind create --help
```

## 开发者说明

发布到 PyPI / TestPyPI 的维护者说明见：

- [CONTRIBUTING.md](./CONTRIBUTING.md)
