import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]


class SystemdUnitTest(unittest.TestCase):
    def test_service_is_one_shot_and_runs_daily_command(self) -> None:
        service = (ROOT / "systemd" / "wallpaper-app.service").read_text()

        self.assertIn("Type=oneshot", service)
        self.assertIn("ExecStart=%h/Projects/Wallpaper_app/.venv/bin/wallpaper-app daily", service)
        self.assertIn("Environment=WALLHAVEN_QUERY=nature", service)
        self.assertNotIn("while True", service)
        self.assertNotIn("sleep", service)

    def test_timer_has_calendar_and_persistence(self) -> None:
        timer = (ROOT / "systemd" / "wallpaper-app.timer").read_text()

        self.assertIn("OnCalendar=*-*-* 09:00:00", timer)
        self.assertIn("Persistent=true", timer)
        self.assertIn("Unit=wallpaper-app.service", timer)

    def test_network_dispatcher_starts_only_for_connected_state(self) -> None:
        dispatcher = (ROOT / "systemd" / "90-wallpaper-app-network-dispatcher").read_text()

        self.assertIn('[ "${2:-}" = "up" ] || exit 0', dispatcher)
        self.assertIn('systemctl --user --machine="${user_name}@.host" start wallpaper-app.service', dispatcher)
        self.assertNotIn("while true", dispatcher.lower())
        self.assertNotIn("sleep", dispatcher.lower())


if __name__ == "__main__":
    unittest.main()
