from textual.app import App
from unctl.interactive.headers import HEADERS

from unctl.interactive.screens.reports import ReportsTableScreen
from unctl.interactive.screens.quit_confirm import QuitConfirm

from unctl.scanrkube import ResourceChecker


class InteractiveApp(App):
    TABLE_ID = "table"
    CSS_PATH = "styles.tcss"
    BINDINGS = [
        ("q", "request_quit", "Quit"),
    ]

    def __init__(
        self,
        provider: str,
        checker: ResourceChecker,
    ):
        super().__init__()
        self._checker = checker
        self._provider = provider

    def on_mount(self):
        table = ReportsTableScreen(
            columns=HEADERS[self._provider],
            items=self._checker.failing_reports,
            checker=self._checker,
        )

        self.install_screen(table, self.TABLE_ID)
        self.push_screen(self.TABLE_ID)

    def action_request_quit(self):
        self.push_screen(QuitConfirm())

    def update(self):
        self.get_screen(self.TABLE_ID).update()
