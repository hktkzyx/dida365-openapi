---
name: dida365-openapi
description: Use when the user wants to operate Dida365 or TickTick through the official OpenAPI, especially for reminder creation, scheduled tasks, recurring reminders, inbox operations, and project/task CRUD through the dida365-openapi CLI.
---

# Dida365 OpenAPI Skill

这个 skill 用于驱动 `dida365-openapi` 命令行工具。

## 适用场景

- 用户明确提到“滴答清单”“Dida365”“TickTick”
- 需要创建提醒、待办、周期任务
- 需要通过 OpenAPI 管理项目、任务、收集箱

## 家庭项目规则

- 提醒、定时任务、周期提醒默认必须创建滴答清单任务
- 默认优先用 `remind create`
- 没有明确项目时，默认放入收集箱
- `remind create` 默认是**单次准时提醒**
- 周期提醒通过 `--repeat-flag` 保留

## 安装 CLI

本 skill 假设仓库根目录是一个可安装的 Python CLI 项目。

本地开发：

```bash
uv tool install .
```

以后发布到 GitHub 后，可改为：

```bash
uv tool install git+https://github.com/<owner>/dida365-openapi.git
```

## 常用命令

```bash
dida365-openapi auth --manual
dida365-openapi remind create --title "两分钟后喝水" --at "2026-04-08 14:30:00"
dida365-openapi remind create --title "每月调仓" --at "2026-04-24 09:00:00" --repeat-flag "RRULE:FREQ=MONTHLY;INTERVAL=1;BYMONTHDAY=24"
dida365-openapi inbox list
dida365-openapi tasks list --project-id <project_id>
```

## 工作流

1. 检查 `.env` 或环境变量中的 Dida365 凭据
2. 若无 token，先执行 `dida365-openapi auth`
3. 如果用户意图是提醒，优先用 `dida365-openapi remind create`
4. 默认保留 `TRIGGER:PT0S` 单次准时提醒
5. 若用户要求周期，添加 `--repeat-flag`

## 参考资料

- 详细接口说明：`references/api_summary.md`
- CLI 项目说明：仓库根目录 `README.md`

