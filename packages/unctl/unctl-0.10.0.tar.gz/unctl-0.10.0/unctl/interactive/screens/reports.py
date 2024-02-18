from textual import work
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header, Static
from unctl.interactive.screens.resolving import ResolvingScreen
import unctl.analytics as analytics
from unctl.lib.checks.check_report import CheckReport
from unctl.scanrkube import ResourceChecker
from textual.containers import Container


class ReportsTableScreen(Screen):
    TITLE = "Interactive remediation"

    BINDINGS = [
        ("r", "re_run_check", "Re-run checks"),
    ]

    def __init__(
        self,
        columns: list[str],
        items: list[CheckReport],
        checker: ResourceChecker,
        group=False,
        title=str,
        summary=str,
    ):
        super().__init__()
        self.columns = columns
        self._items = items
        self._checker = checker
        self._group = group
        self._title = title
        self._summary = summary

        if group:
            self._bindings.bind("escape", "app.pop_screen", "Back")

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

        if self._group:
            yield Container(
                Static("Group Failure", id="sidebar-title"),
                Static(f'\n  "Title":  "{self._title}"'),
                Static(f'\n  "Summary":  "{self._summary}"'),
                id="sidebar",
            )
        yield DataTable(zebra_stripes=True, cursor_type="row", id="table")

    def on_mount(self):
        data_table = self.query_one(DataTable)

        # TODO: set width for columns at definition
        for col in self.columns:
            if col == "Summary":
                data_table.add_column(col, width=50)
            elif col == "Check":
                data_table.add_column(col, width=30)
            elif col == "Object":
                data_table.add_column(col, width=20)
            else:
                data_table.add_column(col, width=10)

        for item in self._items:
            data_table.add_row(*item.display_row, height=None)

    def action_re_run_check(self):
        table = self.query_one(DataTable)
        table.loading = True

        self.re_run_checks()

    def update(self):
        table = self.query_one(DataTable)

        failing_reports = self._checker.failing_reports

        for item in self._items:
            if not any(
                report
                for report in failing_reports
                if report.object_id == item.object_id
            ):
                item.status = "PASS"

        table.rows = {}
        for item in self._items:
            table.add_row(*item.display_row, height=None)

        table.loading = False

    @work()
    async def re_run_checks(self):
        await self._checker.execute()

        self.update()

    def on_data_table_row_selected(self, row_selected):
        item: CheckReport = self._items[row_selected.cursor_row]
        index = self._items.index(item)

        if not self.app.is_screen_installed(item.object_id):
            self.app.install_screen(
                ResolvingScreen(item=item, checker=self._checker),
                item.object_id,
            )

        # Track event: Failed object selection
        app_type = "remediation" if self._group else "interactive"
        analytics.track_failure_selection(item.check_metadata.CheckID, index, app_type)
        self.app.push_screen(item.object_id)
