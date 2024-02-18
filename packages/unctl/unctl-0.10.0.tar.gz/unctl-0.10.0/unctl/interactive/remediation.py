from textual.app import App
from unctl.interactive.screens.groups import GroupsTableScreen

from unctl.interactive.screens.quit_confirm import QuitConfirm

from unctl.scanrkube import ResourceChecker


class RemediationApp(App):
    TABLE_ID = "table"
    CSS_PATH = "styles.tcss"
    BINDINGS = [
        ("q", "request_quit", "Quit"),
    ]

    def __init__(self, provider: str, checker: ResourceChecker):
        super().__init__()
        self._checker = checker
        self._provider = provider

    def on_mount(self):
        table = GroupsTableScreen(checker=self._checker, provider=self._provider)
        self.install_screen(table, self.TABLE_ID)
        self.push_screen(self.TABLE_ID)

    def action_request_quit(self):
        self.push_screen(QuitConfirm())

    def update(self):
        self.get_screen(self.TABLE_ID).update()
