# dida365-openapi

一个面向使用者的 Dida365 / TickTick OpenAPI 命令行工具。

它适合两类场景：

- 你自己在终端里创建项目、任务、提醒
- AI agent 通过命令行稳定调用 Dida365 / TickTick

## 安装

```bash
uv tool install git+https://github.com/hktkzyx/dida365-openapi.git
```

安装后可直接使用：

```bash
dida365-openapi --help
```

## 先准备 OpenAPI 凭据

至少需要这两个环境变量：

- `DIDA365_CLIENT_ID`
- `DIDA365_CLIENT_SECRET`

可选变量：

- `DIDA365_SERVICE_TYPE`
  - 可选值：`dida365` / `ticktick`
  - 默认：`dida365`
- `DIDA365_REDIRECT_URI`
  - 默认：`http://127.0.0.1:8788/callback`
- `DIDA365_SCOPE`
  - 默认：`tasks:read tasks:write`
- `DIDA365_TOKEN_FILE`
  - 自定义 token 文件位置
- `DIDA365_ENV_FILE`
  - 显式指定 `.env` 文件路径

## `.env` 现在读取哪里

当前版本不是读取“仓库里的 `.env`”，而是按下面顺序取配置：

1. 当前进程已有的系统环境变量
2. `--env-file /absolute/path/to/.env`
3. `DIDA365_ENV_FILE=/absolute/path/to/.env`
4. `~/.config/dida365-openapi/.env`
5. 当前工作目录 `.env`
6. 代码默认值

补充说明：

- 系统环境变量优先级最高，不会被 `.env` 覆盖
- `~/.config/dida365-openapi/.env` 适合安装后长期使用，也适合 agent 跨项目调用
- 当前工作目录 `.env` 适合项目级覆盖
- 如果同时存在用户级 `.env` 和当前目录 `.env`，当前目录的值优先

这解决了两个问题：

- 安装后的使用者不需要依赖仓库目录
- AI agent 不需要假设自己总是在同一个项目目录下运行

## 推荐做法

### 普通使用者

把凭据写到用户级配置文件：

```bash
mkdir -p ~/.config/dida365-openapi
cp .env.example ~/.config/dida365-openapi/.env
```

然后编辑：

```env
DIDA365_CLIENT_ID=your_client_id
DIDA365_CLIENT_SECRET=your_client_secret
DIDA365_SERVICE_TYPE=dida365
DIDA365_REDIRECT_URI=http://127.0.0.1:8788/callback
```

这样你在任何目录执行 `dida365-openapi` 都能读到同一套配置。

### AI agent / 自动化调用

推荐也直接使用用户级配置文件：

```bash
mkdir -p ~/.config/dida365-openapi
cp .env.example ~/.config/dida365-openapi/.env
```

这样无论是人手动调用，还是 agent 在不同项目目录下调用，默认都能读到同一份配置，通常不需要显式传 `--env-file`。

只有在下面这些场景，才建议额外指定：

- 同一台机器上要切换多套账号
- 某个 agent 需要完全独立的配置
- 你明确希望配置跟随某个任务运行时隔离

可选方式：

```bash
export DIDA365_ENV_FILE=/absolute/path/to/dida365.env
```

或者：

```bash
dida365-openapi --env-file /absolute/path/to/dida365.env projects list
```

## 给 AI agent 的最小示例

默认推荐把配置放在：

```text
~/.config/dida365-openapi/.env
```

例如：

```env
# ~/.config/dida365-openapi/.env
DIDA365_CLIENT_ID=your_client_id
DIDA365_CLIENT_SECRET=your_client_secret
DIDA365_SERVICE_TYPE=dida365
DIDA365_REDIRECT_URI=http://127.0.0.1:8788/callback
```

此时 agent 直接调用即可：

```bash
dida365-openapi projects list
```

创建提醒：

```bash
dida365-openapi remind create \
  --title "30分钟后开会" \
  --at "2026-04-08 15:00:00"
```

如果确实需要隔离配置，再单独指定：

```bash
export DIDA365_ENV_FILE=/opt/dida365/dida365.env
```

建议：

- 默认把配置放到 `~/.config/dida365-openapi/.env`
- 常规情况下不需要显式传 `--env-file`
- 把 token 文件保留在默认位置，或单独设置 `DIDA365_TOKEN_FILE`
- 多个 agent 如果共用同一账号，最好共用同一份 `.env` 和 token 文件策略

## 首次认证

有浏览器时：

```bash
dida365-openapi auth
```

无浏览器时：

```bash
dida365-openapi auth --manual
```

认证成功后，token 默认保存到：

```text
~/.config/dida365-openapi/{service_type}-{client_id}.json
```

例如：

```text
~/.config/dida365-openapi/dida365-your_client_id.json
```

如果你想改位置：

- 设置 `DIDA365_TOKEN_FILE`
- 或在命令行使用 `--token-file`

## 常见用法

### 查看项目

```bash
dida365-openapi projects list
```

### 新建项目

```bash
dida365-openapi projects create --name "工作"
```

### 查看项目内任务

```bash
dida365-openapi tasks list --project-id your_project_id
```

### 创建任务

```bash
dida365-openapi tasks create \
  --project-id your_project_id \
  --title "写周报"
```

### 创建一个单次提醒

```bash
dida365-openapi remind create \
  --title "两分钟后喝水" \
  --at "2026-04-08 14:30:00"
```

默认行为：

- 默认放入收集箱
- 默认时区为 `Asia/Shanghai`
- 默认提醒触发器为 `TRIGGER:PT0S`
- 默认是单次提醒

### 创建一个周期提醒

```bash
dida365-openapi remind create \
  --title "每月调仓" \
  --at "2026-04-24 09:00:00" \
  --repeat-flag "RRULE:FREQ=MONTHLY;INTERVAL=1;BYMONTHDAY=24"
```

## 命令概览

- `auth`: OAuth2 授权
- `projects`: 项目操作
- `tasks`: 任务操作
- `inbox`: 收集箱操作
- `remind`: 面向提醒的快捷命令

完整参数请查看：

```bash
dida365-openapi --help
dida365-openapi tasks --help
dida365-openapi remind create --help
```

## 安全说明

- 不要提交真实 `.env`
- 不要提交 token 文件
- 仓库里的 `.env.example` 只是模板，不包含真实凭据

默认敏感文件位置：

- `~/.config/dida365-openapi/.env`
- `~/.config/dida365-openapi/*.json`

## 仓库附带的 skill

仓库中包含一个可供 skill 安装器使用的目录：

```text
skills/dida365-openapi/
```

如果你只是想用 CLI，可以忽略它。

## 开发者说明

发布到 PyPI / TestPyPI 的维护者说明见：

- [CONTRIBUTING.md](./CONTRIBUTING.md)
