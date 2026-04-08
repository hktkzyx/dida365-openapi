---
name: dida365-openapi
description: Use when the user wants to operate Dida365 or TickTick through the official OpenAPI, including OAuth2 setup, listing projects and tasks, creating or updating tasks, completing tasks, deleting tasks, and basic project CRUD.
---

# Dida365 OpenAPI Skill

这个 skill 用于通过滴答清单 / TickTick 官方 OpenAPI 操作项目和任务。

## 适用场景

- 用户明确提到“滴答清单”“Dida365”“TickTick”
- 需要通过开放 API 做任务同步、批量操作、自动化
- 需要先完成 OAuth2 授权，再执行项目或任务操作

## 家庭项目强规则

- 在这个家庭助理项目里，只要用户表达的是“提醒我”“记得做”“到时候提醒”“定时任务”“周期提醒”“待办跟踪”这类需求，默认都必须创建**滴答清单任务**
- 不要优先改用 `schedule`、`cron` 或仅做口头提醒；除非用户明确要求不用滴答清单，或滴答清单当前不可用
- 如果任务没有明确归属项目，优先放入**收集箱**
- 如果任务有明确日期、时间、周期规则，创建任务时要尽量完整写入 `startDate`、`dueDate`、`timeZone`、`repeatFlag` 等字段
- 如果用户说的是“提醒我”，不要只写任务时间；还要显式写入提醒触发器 `reminders`。常见场景默认使用 `TRIGGER:PT0S`（任务开始时提醒）
- 执行完成后，在回复里明确说明已创建滴答清单任务，以及放入了哪个项目或收集箱

## 目录

- `scripts/dida365_cli.py`: 直接调用官方 OAuth2 和 `open/v1` API 的脚本
- `references/api_summary.md`: 从官方开发者站和接口路径整理出的最小参考
- 仓库级说明见根目录 `README.md`

## 快速使用

先在开发者后台创建应用：

- Dida365: `https://developer.dida365.com/manage`
- TickTick: `https://developer.ticktick.com/manage`

把以下变量放进当前工作目录的 `.env`，或在命令前临时导出：

```bash
DIDA365_CLIENT_ID=你的 Client ID
DIDA365_CLIENT_SECRET=你的 Client Secret
DIDA365_SERVICE_TYPE=dida365
DIDA365_REDIRECT_URI=http://127.0.0.1:8788/callback
```

首次授权：

```bash
uv run scripts/dida365_cli.py auth
```

无浏览器环境：

```bash
uv run scripts/dida365_cli.py auth --manual
```

该模式会打印授权链接。你在任意可用浏览器里完成授权后，把最终跳转地址里的完整回调 URL，或只把 `code` 值粘贴回终端即可。

常用命令：

```bash
uv run scripts/dida365_cli.py projects list
uv run scripts/dida365_cli.py tasks list --project-id <project_id>
uv run scripts/dida365_cli.py tasks create --project-id <project_id> --title "买牛奶"
uv run scripts/dida365_cli.py remind create --title "两分钟后喝水" --at "2026-04-08 13:20:00"
uv run scripts/dida365_cli.py inbox create --title "两分钟后喝水" --start-date "2026-04-08T13:20:00+08:00" --due-date "2026-04-08T13:20:00+08:00" --time-zone "Asia/Shanghai" --reminder "TRIGGER:PT0S"
uv run scripts/dida365_cli.py tasks complete --project-id <project_id> --task-id <task_id>
uv run scripts/dida365_cli.py inbox list
uv run scripts/dida365_cli.py inbox create --title "收集箱任务"
```

## 工作流

1. 先确认是 `dida365` 还是 `ticktick`
2. 检查 `DIDA365_CLIENT_ID`、`DIDA365_CLIENT_SECRET`、`DIDA365_REDIRECT_URI`
3. 若本地还没有 token，先执行 `auth`
4. 如果用户意图是提醒、定时、周期任务，优先创建滴答清单任务，而不是停留在建议层；“提醒我”类任务要同时带上 `--reminder "TRIGGER:PT0S"`
5. 再执行项目或任务命令

## remind 命令

- `remind create` 是面向提醒场景的快捷入口
- 默认创建**单次准时提醒**
- 默认写入**收集箱**
- 默认使用 `TRIGGER:PT0S`
- 如果需要周期提醒，继续传 `--repeat-flag`

## 时间字段

脚本接受下面几类输入，并会尽量规范成 API 常见格式：

- `2026-04-08T18:30:00+08:00`
- `2026-04-08 18:30`
- `2026-04-08`

如果是定时任务，优先显式传 `--time-zone Asia/Shanghai`。

对于不带时区的输入，例如 `2026-04-08 18:30`，脚本会按 `--time-zone` 指定的时区解释，再转换成 API 使用的 UTC 时间发送。

## 注意事项

- 该脚本按官方 OAuth2 流程工作，默认 scope 为 `tasks:read tasks:write`
- token 默认保存在 `~/.config/dida365-openapi/` 下
- 收集箱不是普通项目；请用 `inbox` 子命令读取。脚本会自动解析并缓存真实 inbox `projectId`
- 如果只需要了解接口字段，再读 `references/api_summary.md`
- 如果文档页抓取失败，优先相信开发者后台、OAuth 路径和 `open/v1` 实际接口路径；不要随意改成猜测的端点
