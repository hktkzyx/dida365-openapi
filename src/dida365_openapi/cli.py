#!/usr/bin/env python3
"""Dida365 / TickTick OpenAPI CLI."""

from __future__ import annotations

import argparse
import json
import os
import secrets
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from dataclasses import dataclass
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


DEFAULT_SCOPE = "tasks:read tasks:write"


def parse_dotenv(env_path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    if not env_path.exists():
        return data
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip().strip("'").strip('"')
    return data


def load_dotenv(env_file: str | None = None) -> None:
    original_env_keys = set(os.environ)
    merged: dict[str, str] = {}

    explicit_env_file = env_file or os.getenv("DIDA365_ENV_FILE")
    if explicit_env_file:
        env_paths = [Path(explicit_env_file).expanduser()]
    else:
        env_paths = [
            Path.home() / ".config" / "dida365-openapi" / ".env",
            Path.cwd() / ".env",
        ]

    for env_path in env_paths:
        merged.update(parse_dotenv(env_path))

    for key, value in merged.items():
        if key not in original_env_keys:
            os.environ[key] = value


def normalize_datetime(value: str | None, time_zone: str | None = None) -> str | None:
    if not value:
        return None
    value = value.strip()
    if not value:
        return None
    local_tz = ZoneInfo(time_zone or "Asia/Shanghai")
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(value, fmt).replace(tzinfo=local_tz)
            return dt.astimezone(ZoneInfo("UTC")).strftime("%Y-%m-%dT%H:%M:%S+0000")
        except ValueError:
            pass
    try:
        dt = datetime.fromisoformat(value)
    except ValueError:
        return value
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=local_tz)
    return dt.astimezone(ZoneInfo("UTC")).strftime("%Y-%m-%dT%H:%M:%S+0000")


def print_json(data: Any) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True))


@dataclass
class Config:
    service_type: str
    client_id: str
    client_secret: str
    redirect_uri: str
    scope: str
    token_file: Path

    @property
    def api_base(self) -> str:
        domain = "api.dida365.com" if self.service_type == "dida365" else "api.ticktick.com"
        return f"https://{domain}/open/v1"

    @property
    def auth_url(self) -> str:
        domain = "dida365.com" if self.service_type == "dida365" else "ticktick.com"
        return f"https://{domain}/oauth/authorize"

    @property
    def token_url(self) -> str:
        domain = "dida365.com" if self.service_type == "dida365" else "ticktick.com"
        return f"https://{domain}/oauth/token"


class ApiClient:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.token = self._load_token()

    def _load_token(self) -> dict[str, Any] | None:
        if not self.config.token_file.exists():
            return None
        return json.loads(self.config.token_file.read_text(encoding="utf-8"))

    def _save_token(self, token_data: dict[str, Any]) -> None:
        self.config.token_file.parent.mkdir(parents=True, exist_ok=True)
        self.config.token_file.write_text(json.dumps(token_data, ensure_ascii=False, indent=2), encoding="utf-8")
        self.token = token_data

    def _update_token_metadata(self, **fields: Any) -> None:
        current = self.token.copy() if self.token else {}
        current.update(fields)
        self._save_token(current)

    def _access_token(self) -> str:
        token = os.getenv("DIDA365_ACCESS_TOKEN")
        if token:
            return token
        if self.token and self.token.get("access_token"):
            return self.token["access_token"]
        raise SystemExit("缺少 access token，请先执行 auth。")

    def _request(
        self,
        method: str,
        path: str,
        *,
        data: dict[str, Any] | None = None,
        auth: bool = True,
        form: bool = False,
        absolute_url: str | None = None,
    ) -> Any:
        url = absolute_url or f"{self.config.api_base}/{path.lstrip('/')}"
        headers = {"User-Agent": "dida365-openapi/0.1.0", "Accept": "application/json"}
        body = None
        if auth:
            headers["Authorization"] = f"Bearer {self._access_token()}"
        if data is not None:
            if form:
                headers["Content-Type"] = "application/x-www-form-urlencoded"
                body = urllib.parse.urlencode(data).encode("utf-8")
            else:
                headers["Content-Type"] = "application/json"
                body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(url, data=body, headers=headers, method=method.upper())
        try:
            with urllib.request.urlopen(request) as response:
                raw = response.read()
                if not raw:
                    return None
                return json.loads(raw.decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise SystemExit(f"API 请求失败: {exc.code} {detail}") from exc

    def exchange_code(self, code: str) -> dict[str, Any]:
        payload = {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.config.redirect_uri,
            "scope": self.config.scope,
        }
        token = self._request("POST", "", data=payload, auth=False, form=True, absolute_url=self.config.token_url)
        self._save_token(token)
        return token

    def get(self, path: str) -> Any:
        return self._request("GET", path)

    def post(self, path: str, data: dict[str, Any] | None = None) -> Any:
        return self._request("POST", path, data=data)

    def delete(self, path: str) -> Any:
        return self._request("DELETE", path)

    def get_cached_inbox_project_id(self) -> str | None:
        if self.token and self.token.get("inbox_project_id"):
            return self.token["inbox_project_id"]
        return None

    def resolve_inbox_project_id(self) -> str:
        cached = self.get_cached_inbox_project_id()
        if cached:
            return cached
        probe_title = f"__inbox_probe__{secrets.token_hex(4)}"
        created = self.post("task", {"projectId": "", "title": probe_title})
        inbox_project_id = created.get("projectId")
        task_id = created.get("id")
        if not inbox_project_id or not task_id:
            raise SystemExit("未能解析收集箱项目 ID。")
        self.delete(f"project/{inbox_project_id}/task/{task_id}")
        self._update_token_metadata(inbox_project_id=inbox_project_id)
        return inbox_project_id


def build_config(args: argparse.Namespace) -> Config:
    load_dotenv(args.env_file)
    service_type = (args.service_type or os.getenv("DIDA365_SERVICE_TYPE") or "dida365").strip().lower()
    if service_type not in {"dida365", "ticktick"}:
        raise SystemExit("DIDA365_SERVICE_TYPE 只能是 dida365 或 ticktick。")
    client_id = (os.getenv("DIDA365_CLIENT_ID") or "").strip()
    client_secret = (os.getenv("DIDA365_CLIENT_SECRET") or "").strip()
    redirect_uri = (os.getenv("DIDA365_REDIRECT_URI") or "http://127.0.0.1:8788/callback").strip()
    scope = (os.getenv("DIDA365_SCOPE") or DEFAULT_SCOPE).strip()
    if args.command != "auth" and not client_id:
        raise SystemExit("缺少 DIDA365_CLIENT_ID。")
    if args.command != "auth" and not client_secret:
        raise SystemExit("缺少 DIDA365_CLIENT_SECRET。")
    if args.command == "auth" and (not client_id or not client_secret):
        raise SystemExit("auth 需要先设置 DIDA365_CLIENT_ID 和 DIDA365_CLIENT_SECRET。")
    token_file = Path(
        args.token_file
        or os.getenv("DIDA365_TOKEN_FILE")
        or (Path.home() / ".config" / "dida365-openapi" / f"{service_type}-{client_id or 'default'}.json")
    )
    return Config(
        service_type=service_type,
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=scope,
        token_file=token_file,
    )


def compact_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if value is not None}


def task_payload_from_args(args: argparse.Namespace, require_title: bool) -> dict[str, Any]:
    payload = {
        "projectId": getattr(args, "project_id", None),
        "title": args.title,
        "content": args.content,
        "desc": args.desc,
        "isAllDay": args.all_day,
        "startDate": normalize_datetime(args.start_date, args.time_zone),
        "dueDate": normalize_datetime(args.due_date, args.time_zone),
        "timeZone": args.time_zone,
        "priority": args.priority,
        "reminders": getattr(args, "reminders", None),
        "repeatFlag": getattr(args, "repeat_flag", None),
    }
    if getattr(args, "task_id", None):
        payload["id"] = args.task_id
    payload = compact_payload(payload)
    if require_title and not payload.get("title"):
        raise SystemExit("tasks create 需要 --title。")
    return payload


def remind_payload_from_args(args: argparse.Namespace, client: ApiClient) -> dict[str, Any]:
    fake_args = argparse.Namespace(
        project_id=args.project_id,
        title=args.title,
        content=args.content,
        desc=args.desc,
        all_day=args.all_day,
        start_date=args.at,
        due_date=args.at,
        time_zone=args.time_zone,
        priority=args.priority,
        reminders=args.reminders or ["TRIGGER:PT0S"],
        repeat_flag=args.repeat_flag,
        task_id=None,
    )
    payload = task_payload_from_args(fake_args, require_title=True)
    if args.inbox or not args.project_id:
        payload["projectId"] = ""
        client.resolve_inbox_project_id()
    return payload


def command_auth(client: ApiClient, config: Config, args: argparse.Namespace) -> None:
    state = secrets.token_urlsafe(16)
    params = {
        "client_id": config.client_id,
        "scope": config.scope,
        "state": state,
        "redirect_uri": config.redirect_uri,
        "response_type": "code",
    }
    authorize_url = f"{config.auth_url}?{urllib.parse.urlencode(params)}"
    if args.manual:
        print("打开下面的授权链接：")
        print(authorize_url)
        print("")
        print("授权完成后，把浏览器最终跳转地址里的 code 粘贴回来。")
        print("例如：http://127.0.0.1:8788/callback?code=xxx&state=yyy")
        pasted = input("请粘贴完整回调 URL 或直接粘贴 code: ").strip()
        if not pasted:
            raise SystemExit("未提供 code。")
        if "://" in pasted or pasted.startswith("/"):
            parsed_callback = urllib.parse.urlparse(pasted)
            query = urllib.parse.parse_qs(parsed_callback.query)
            code = query.get("code", [""])[0]
            returned_state = query.get("state", [""])[0]
            if returned_state and returned_state != state:
                raise SystemExit("state 校验失败，已终止。")
        else:
            code = pasted
        if not code:
            raise SystemExit("未从输入中解析出 code。")
        print_json(client.exchange_code(code))
        return

    parsed = urllib.parse.urlparse(config.redirect_uri)
    if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost"} or not parsed.port:
        raise SystemExit("当前 auth 回调模式要求 DIDA365_REDIRECT_URI 使用本地 http 回调，例如 http://127.0.0.1:8788/callback；无浏览器场景请改用 --manual。")

    callback: dict[str, str] = {}

    class CallbackHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            callback["code"] = query.get("code", [""])[0]
            callback["state"] = query.get("state", [""])[0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("授权成功，可以回到终端。".encode("utf-8"))

        def log_message(self, fmt: str, *args: Any) -> None:
            return

    server = HTTPServer((parsed.hostname, parsed.port), CallbackHandler)
    print("打开浏览器进行授权：")
    print(authorize_url)
    if not args.no_browser:
        webbrowser.open(authorize_url)
    deadline = time.time() + args.timeout
    while time.time() < deadline and "code" not in callback:
        server.timeout = 1
        server.handle_request()
    server.server_close()
    code = callback.get("code")
    if not code:
        raise SystemExit("授权超时，未收到回调 code。")
    if callback.get("state") != state:
        raise SystemExit("state 校验失败，已终止。")
    print_json(client.exchange_code(code))


def command_exchange_code(client: ApiClient, _config: Config, args: argparse.Namespace) -> None:
    print_json(client.exchange_code(args.code))


def command_projects(client: ApiClient, _config: Config, args: argparse.Namespace) -> None:
    if args.projects_command == "list":
        print_json(client.get("project"))
        return
    if args.projects_command == "get":
        print_json(client.get(f"project/{args.project_id}"))
        return
    if args.projects_command == "data":
        print_json(client.get(f"project/{args.project_id}/data"))
        return
    if args.projects_command == "create":
        print_json(client.post("project", compact_payload({"name": args.name, "color": args.color, "viewMode": args.view_mode, "kind": args.kind})))
        return
    if args.projects_command == "update":
        print_json(client.post(f"project/{args.project_id}", compact_payload({"id": args.project_id, "name": args.name, "color": args.color, "viewMode": args.view_mode, "kind": args.kind})))
        return
    if args.projects_command == "delete":
        print_json({"deleted": True, "projectId": args.project_id, "response": client.delete(f"project/{args.project_id}")})
        return
    raise SystemExit("不支持的 projects 子命令。")


def command_tasks(client: ApiClient, _config: Config, args: argparse.Namespace) -> None:
    if args.tasks_command == "list":
        print_json(client.get(f"project/{args.project_id}/data").get("tasks", []))
        return
    if args.tasks_command == "get":
        print_json(client.get(f"project/{args.project_id}/task/{args.task_id}"))
        return
    if args.tasks_command == "create":
        print_json(client.post("task", task_payload_from_args(args, require_title=True)))
        return
    if args.tasks_command == "update":
        print_json(client.post(f"task/{args.task_id}", task_payload_from_args(args, require_title=False)))
        return
    if args.tasks_command == "complete":
        print_json({"completed": True, "taskId": args.task_id, "response": client.post(f"project/{args.project_id}/task/{args.task_id}/complete")})
        return
    if args.tasks_command == "delete":
        print_json({"deleted": True, "taskId": args.task_id, "response": client.delete(f"project/{args.project_id}/task/{args.task_id}")})
        return
    raise SystemExit("不支持的 tasks 子命令。")


def command_inbox(client: ApiClient, _config: Config, args: argparse.Namespace) -> None:
    inbox_project_id = client.resolve_inbox_project_id()
    if args.inbox_command == "id":
        print_json({"projectId": inbox_project_id})
        return
    if args.inbox_command == "list":
        print_json(client.get(f"project/{inbox_project_id}/data").get("tasks", []))
        return
    if args.inbox_command == "create":
        payload = task_payload_from_args(args, require_title=True)
        payload["projectId"] = ""
        print_json(client.post("task", payload))
        return
    raise SystemExit("不支持的 inbox 子命令。")


def command_remind(client: ApiClient, _config: Config, args: argparse.Namespace) -> None:
    if args.remind_command == "create":
        print_json(client.post("task", remind_payload_from_args(args, client)))
        return
    raise SystemExit("不支持的 remind 子命令。")


def add_common_config(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--env-file", help="覆盖 .env 文件路径；默认依次尝试 ~/.config/dida365-openapi/.env 和当前工作目录 .env")
    parser.add_argument("--service-type", choices=["dida365", "ticktick"], help="覆盖 DIDA365_SERVICE_TYPE")
    parser.add_argument("--token-file", help="覆盖 token 文件路径")


def add_task_fields(parser: argparse.ArgumentParser, require_task_id: bool) -> None:
    parser.add_argument("--title")
    parser.add_argument("--content")
    parser.add_argument("--desc")
    parser.add_argument("--start-date")
    parser.add_argument("--due-date")
    parser.add_argument("--time-zone")
    parser.add_argument("--priority", type=int, choices=[0, 1, 3, 5])
    parser.add_argument("--reminder", dest="reminders", action="append", help="提醒触发器，例如 TRIGGER:PT0S（开始时提醒）")
    parser.add_argument("--repeat-flag", help="重复规则，例如 RRULE:FREQ=DAILY")
    parser.add_argument("--all-day", action="store_true")
    if require_task_id:
        parser.add_argument("--task-id", required=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Operate Dida365/TickTick via official OpenAPI.")
    add_common_config(parser)
    subparsers = parser.add_subparsers(dest="command", required=True)

    auth_parser = subparsers.add_parser("auth", help="Run OAuth2 authorization flow")
    add_common_config(auth_parser)
    auth_parser.add_argument("--timeout", type=int, default=180, help="等待浏览器回调的秒数")
    auth_parser.add_argument("--no-browser", action="store_true", help="只打印链接，不自动打开浏览器")
    auth_parser.add_argument("--manual", action="store_true", help="只打印授权链接，并手动粘贴回调 URL 或 code")

    exchange_parser = subparsers.add_parser("exchange-code", help="Exchange an authorization code")
    add_common_config(exchange_parser)
    exchange_parser.add_argument("--code", required=True)

    projects_parser = subparsers.add_parser("projects", help="Project operations")
    add_common_config(projects_parser)
    projects_sub = projects_parser.add_subparsers(dest="projects_command", required=True)
    projects_sub.add_parser("list")
    get_project = projects_sub.add_parser("get")
    get_project.add_argument("--project-id", required=True)
    project_data = projects_sub.add_parser("data")
    project_data.add_argument("--project-id", required=True)
    create_project = projects_sub.add_parser("create")
    create_project.add_argument("--name", required=True)
    create_project.add_argument("--color")
    create_project.add_argument("--view-mode", choices=["list", "kanban", "timeline"])
    create_project.add_argument("--kind", choices=["TASK", "NOTE"])
    update_project = projects_sub.add_parser("update")
    update_project.add_argument("--project-id", required=True)
    update_project.add_argument("--name")
    update_project.add_argument("--color")
    update_project.add_argument("--view-mode", choices=["list", "kanban", "timeline"])
    update_project.add_argument("--kind", choices=["TASK", "NOTE"])
    delete_project = projects_sub.add_parser("delete")
    delete_project.add_argument("--project-id", required=True)

    tasks_parser = subparsers.add_parser("tasks", help="Task operations")
    add_common_config(tasks_parser)
    tasks_sub = tasks_parser.add_subparsers(dest="tasks_command", required=True)
    list_tasks = tasks_sub.add_parser("list")
    list_tasks.add_argument("--project-id", required=True)
    get_task = tasks_sub.add_parser("get")
    get_task.add_argument("--project-id", required=True)
    get_task.add_argument("--task-id", required=True)
    create_task = tasks_sub.add_parser("create")
    create_task.add_argument("--project-id", required=True)
    add_task_fields(create_task, require_task_id=False)
    update_task = tasks_sub.add_parser("update")
    update_task.add_argument("--project-id", required=True)
    update_task.add_argument("--task-id", required=True)
    add_task_fields(update_task, require_task_id=False)
    complete_task = tasks_sub.add_parser("complete")
    complete_task.add_argument("--project-id", required=True)
    complete_task.add_argument("--task-id", required=True)
    delete_task = tasks_sub.add_parser("delete")
    delete_task.add_argument("--project-id", required=True)
    delete_task.add_argument("--task-id", required=True)

    inbox_parser = subparsers.add_parser("inbox", help="Inbox operations")
    add_common_config(inbox_parser)
    inbox_sub = inbox_parser.add_subparsers(dest="inbox_command", required=True)
    inbox_sub.add_parser("id")
    inbox_sub.add_parser("list")
    inbox_create = inbox_sub.add_parser("create")
    add_task_fields(inbox_create, require_task_id=False)

    remind_parser = subparsers.add_parser("remind", help="Reminder-oriented task operations")
    add_common_config(remind_parser)
    remind_sub = remind_parser.add_subparsers(dest="remind_command", required=True)
    remind_create = remind_sub.add_parser("create")
    remind_create.add_argument("--title", required=True)
    remind_create.add_argument("--at", required=True, help="提醒时间，本地时间按 --time-zone 解释")
    remind_create.add_argument("--content")
    remind_create.add_argument("--desc")
    remind_create.add_argument("--project-id", help="指定项目；默认放入收集箱")
    remind_create.add_argument("--inbox", action="store_true", help="强制放入收集箱")
    remind_create.add_argument("--time-zone", default="Asia/Shanghai")
    remind_create.add_argument("--priority", type=int, choices=[0, 1, 3, 5], default=0)
    remind_create.add_argument("--reminder", dest="reminders", action="append", help="提醒触发器；默认 TRIGGER:PT0S")
    remind_create.add_argument("--repeat-flag", help="重复规则，例如 RRULE:FREQ=DAILY")
    remind_create.add_argument("--all-day", action="store_true")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    config = build_config(args)
    client = ApiClient(config)

    if args.command == "auth":
        command_auth(client, config, args)
        return
    if args.command == "exchange-code":
        command_exchange_code(client, config, args)
        return
    if args.command == "projects":
        command_projects(client, config, args)
        return
    if args.command == "tasks":
        command_tasks(client, config, args)
        return
    if args.command == "inbox":
        command_inbox(client, config, args)
        return
    if args.command == "remind":
        command_remind(client, config, args)
        return
    raise SystemExit("未知命令。")
