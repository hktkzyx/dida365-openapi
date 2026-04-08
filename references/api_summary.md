# Dida365 OpenAPI 摘要

这份摘要只保留创建 skill 需要的最小事实。

## 官方来源

- 开发者后台: `https://developer.dida365.com/manage`
- API 文档入口: `https://developer.dida365.com/api#/openapi`

当前抓取环境对文档页返回 `403`，但开发者后台页面和静态资源可访问，能确认这是官方开发者站。

## 已确认的官方事实

- 开发者后台文案说明使用 OAuth 2.0
- 开发者后台支持创建应用、编辑应用、配置 OAuth Redirect URL、重置 Client Secret
- Dida365 的授权端点为 `https://dida365.com/oauth/authorize`
- Dida365 的换 token 端点为 `https://dida365.com/oauth/token`
- Dida365 的 API 主域名为 `https://api.dida365.com`
- 业务接口路径前缀为 `/open/v1/`

对应 TickTick 国际版时，域名替换为：

- `https://ticktick.com/oauth/authorize`
- `https://ticktick.com/oauth/token`
- `https://api.ticktick.com/open/v1/`

## 参考实现里出现的接口路径

这些路径与官方文档入口一致，由现成客户端实现反查得到，可作为脚本的最小操作集：

- `GET /open/v1/project`
- `POST /open/v1/project`
- `GET /open/v1/project/{projectId}`
- `GET /open/v1/project/{projectId}/data`
- `POST /open/v1/project/{projectId}`
- `DELETE /open/v1/project/{projectId}`
- `POST /open/v1/task`
- `GET /open/v1/project/{projectId}/task/{taskId}`
- `POST /open/v1/task/{taskId}`
- `POST /open/v1/project/{projectId}/task/{taskId}/complete`
- `DELETE /open/v1/project/{projectId}/task/{taskId}`

## 已确认的常见字段

项目：

- `id`
- `name`
- `color`
- `viewMode`: `list` / `kanban` / `timeline`
- `kind`: `TASK` / `NOTE`

任务：

- `id`
- `projectId`
- `title`
- `content`
- `desc`
- `isAllDay`
- `startDate`
- `dueDate`
- `timeZone`
- `priority`: `0` / `1` / `3` / `5`
- `status`: `0` 正常，`2` 已完成
- `items`

## OAuth 建议

- 默认 redirect URI 可用 `http://127.0.0.1:8788/callback`
- 默认 scope 用 `tasks:read tasks:write`
- 对于无浏览器或 headless 场景，可以用“打印授权链接 + 手动粘贴回调 URL / code”的方式完成授权
- 本 skill 当前实现只依赖 access token；如果后续需要 refresh token，再补刷新逻辑

## 收集箱说明

- 收集箱是特殊项目，不会出现在 `GET /open/v1/project` 的普通项目列表中
- 可以通过创建任务时传空字符串 `projectId=""` 写入收集箱
- 创建成功返回的任务对象里，`projectId` 会带回真实的 inbox 项目 ID
- 本 skill 现在会自动探测并缓存该 inbox 项目 ID，然后用 `GET /open/v1/project/{inboxProjectId}/data` 读取收集箱任务
