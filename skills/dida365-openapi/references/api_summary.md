# Dida365 OpenAPI 摘要

这份摘要只保留 skill 执行时最需要的最小事实。

## 官方来源

- 开发者后台: `https://developer.dida365.com/manage`
- API 文档入口: `https://developer.dida365.com/api#/openapi`

## 已确认的官方事实

- Dida365 授权端点为 `https://dida365.com/oauth/authorize`
- Dida365 换 token 端点为 `https://dida365.com/oauth/token`
- Dida365 API 主域名为 `https://api.dida365.com`
- 业务接口前缀为 `/open/v1/`

## 常用端点

- `GET /open/v1/project`
- `GET /open/v1/project/{projectId}/data`
- `POST /open/v1/task`
- `GET /open/v1/project/{projectId}/task/{taskId}`
- `POST /open/v1/task/{taskId}`
- `POST /open/v1/project/{projectId}/task/{taskId}/complete`
- `DELETE /open/v1/project/{projectId}/task/{taskId}`

## 收集箱

- 收集箱不会出现在普通项目列表里
- 创建任务时传空字符串 `projectId=""` 可以写入收集箱
- 返回的任务对象会带回真实的 inbox `projectId`

