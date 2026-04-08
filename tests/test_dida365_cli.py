import argparse
import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


def load_module():
    path = Path(__file__).resolve().parents[1] / "src" / "dida365_openapi" / "cli.py"
    spec = importlib.util.spec_from_file_location("dida365_cli", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Dida365CliTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_module()

    def test_normalize_datetime_with_local_timezone(self):
        value = self.mod.normalize_datetime("2026-04-08 14:31:30", "Asia/Shanghai")
        self.assertEqual(value, "2026-04-08T06:31:30+0000")

    def test_normalize_datetime_with_explicit_offset(self):
        value = self.mod.normalize_datetime("2026-04-08T14:31:30+08:00", "Asia/Shanghai")
        self.assertEqual(value, "2026-04-08T06:31:30+0000")

    def test_remind_payload_defaults_to_single_shot_reminder_and_inbox(self):
        class FakeClient:
            def resolve_inbox_project_id(self):
                return "inbox123"

        args = argparse.Namespace(
            title="测试提醒",
            at="2026-04-08 14:31:30",
            content="说明",
            desc=None,
            project_id=None,
            inbox=False,
            time_zone="Asia/Shanghai",
            priority=0,
            reminders=None,
            repeat_flag=None,
            all_day=False,
        )
        payload = self.mod.remind_payload_from_args(args, FakeClient())
        self.assertEqual(payload["projectId"], "")
        self.assertEqual(payload["reminders"], ["TRIGGER:PT0S"])
        self.assertEqual(payload["startDate"], "2026-04-08T06:31:30+0000")
        self.assertEqual(payload["dueDate"], "2026-04-08T06:31:30+0000")

    def test_remind_payload_keeps_repeat_flag(self):
        class FakeClient:
            def resolve_inbox_project_id(self):
                return "inbox123"

        args = argparse.Namespace(
            title="每月调仓",
            at="2026-04-24 09:00:00",
            content=None,
            desc=None,
            project_id=None,
            inbox=False,
            time_zone="Asia/Shanghai",
            priority=0,
            reminders=["TRIGGER:PT0S"],
            repeat_flag="RRULE:FREQ=MONTHLY;INTERVAL=1;BYMONTHDAY=24",
            all_day=False,
        )
        payload = self.mod.remind_payload_from_args(args, FakeClient())
        self.assertEqual(payload["repeatFlag"], "RRULE:FREQ=MONTHLY;INTERVAL=1;BYMONTHDAY=24")

    def test_load_dotenv_reads_user_config_then_cwd_with_cwd_override(self):
        with tempfile.TemporaryDirectory() as temp_home, tempfile.TemporaryDirectory() as temp_cwd:
            home_env = Path(temp_home) / ".config" / "dida365-openapi" / ".env"
            home_env.parent.mkdir(parents=True)
            home_env.write_text(
                "DIDA365_CLIENT_ID=home-client\nDIDA365_CLIENT_SECRET=home-secret\n",
                encoding="utf-8",
            )
            cwd_env = Path(temp_cwd) / ".env"
            cwd_env.write_text(
                "DIDA365_CLIENT_ID=cwd-client\nDIDA365_REDIRECT_URI=http://127.0.0.1:9999/callback\n",
                encoding="utf-8",
            )

            with mock.patch.object(self.mod.Path, "home", return_value=Path(temp_home)):
                with mock.patch.dict(os.environ, {}, clear=True):
                    original_cwd = Path.cwd()
                    try:
                        os.chdir(temp_cwd)
                        self.mod.load_dotenv()
                        self.assertEqual(os.environ["DIDA365_CLIENT_ID"], "cwd-client")
                        self.assertEqual(os.environ["DIDA365_CLIENT_SECRET"], "home-secret")
                        self.assertEqual(os.environ["DIDA365_REDIRECT_URI"], "http://127.0.0.1:9999/callback")
                    finally:
                        os.chdir(original_cwd)

    def test_load_dotenv_explicit_file_is_stable_across_workdirs(self):
        with tempfile.TemporaryDirectory() as temp_dir, tempfile.TemporaryDirectory() as temp_cwd:
            env_path = Path(temp_dir) / "agent.env"
            env_path.write_text("DIDA365_CLIENT_ID=explicit-client\n", encoding="utf-8")

            with mock.patch.dict(os.environ, {}, clear=True):
                original_cwd = Path.cwd()
                try:
                    os.chdir(temp_cwd)
                    self.mod.load_dotenv(str(env_path))
                    self.assertEqual(os.environ["DIDA365_CLIENT_ID"], "explicit-client")
                finally:
                    os.chdir(original_cwd)


if __name__ == "__main__":
    unittest.main()
