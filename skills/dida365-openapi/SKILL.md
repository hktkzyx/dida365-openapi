---
name: dida365-openapi
description: Use when the user wants to operate Dida365 or TickTick through the official OpenAPI, especially for reminder creation, scheduled tasks, recurring reminders, inbox operations, and project/task CRUD through the dida365-openapi CLI.
---

# Dida365 OpenAPI Skill

这个 skill 用于通过 `dida365-openapi` 操作 Dida365 / TickTick。

## 适用场景

- 用户提到“滴答清单”“Dida365”“TickTick”
- 需要创建提醒、待办、周期任务
- 需要读取或管理项目、任务、收集箱

## 使用前准备

需要先安装 CLI：

```bash
uv tool install dida365-openapi
```

还需要在 Dida365 / TickTick 开发者后台创建应用，并配置本地环境变量：

- `DIDA365_CLIENT_ID`
- `DIDA365_CLIENT_SECRET`

推荐把配置写到：

```text
~/.config/dida365-openapi/.env
```

例如：

```env
DIDA365_CLIENT_ID=your_client_id
DIDA365_CLIENT_SECRET=your_client_secret
DIDA365_SERVICE_TYPE=dida365
DIDA365_REDIRECT_URI=http://127.0.0.1:8788/callback
```

首次使用前需要先完成授权：

```bash
dida365-openapi auth
```

无浏览器环境可使用：

```bash
dida365-openapi auth --manual
```

## 默认行为

- 提醒和定时任务优先使用 `remind create`
- 没有明确项目时，默认放入收集箱
- 默认创建单次准时提醒
- 周期提醒通过 `--repeat-flag` 表达

## 常用命令

创建单次提醒：

```bash
dida365-openapi remind create --title "两分钟后喝水" --at "2026-04-08 14:30:00"
```

创建周期提醒：

```bash
dida365-openapi remind create --title "每月调仓" --at "2026-04-24 09:00:00" --repeat-flag "RRULE:FREQ=MONTHLY;INTERVAL=1;BYMONTHDAY=24"
```

查看收集箱任务：

```bash
dida365-openapi inbox list
```

查看项目列表：

```bash
dida365-openapi projects list
```

查看某个项目下的任务：

```bash
dida365-openapi tasks list --project-id <project_id>
```

## 调用建议

1. 先确认本机已配置凭据并完成授权
2. 如果用户意图是“提醒我”，优先用 `remind create`
3. 如果用户要求重复执行，补上 `--repeat-flag`
4. 如果用户未指定项目，默认写入收集箱

## 参考资料

- OpenAPI 简要说明：`references/api_summary.md`
- CLI 使用说明：仓库根目录 `README.md`
