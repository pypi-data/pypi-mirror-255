from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header
from unctl.interactive.headers import HEADERS
from unctl.interactive.screens.reports import ReportsTableScreen
import unctl.analytics as analytics
import shutil
from unctl.lib.models.remediations import FailureGroup
from unctl.scanrkube import ResourceChecker
from textual.events import Resize


class GroupsTableScreen(Screen):
    TITLE = "Triaged errors"

    BINDINGS = []

    _current_group: ReportsTableScreen

    def __init__(self, checker: ResourceChecker, provider: str):
        super().__init__()
        self._checker = checker
        self._provider = provider
        self._resize_called = False
        self._initial_terminal_size = shutil.get_terminal_size()

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield DataTable(zebra_stripes=True, cursor_type="row", id="group-table")

    def on_mount(self):
        data_table = self.query_one(DataTable)
        term_width, _ = shutil.get_terminal_size()
        self._prev_width = term_width
        data_table.add_column("Group", width=40)
        data_table.add_column("Failed Objects", width=15)
        data_table.add_column("Summary", key="summary", width=round(term_width - 60))

        self._render_rows()

    def _on_resize(self, event: Resize):
        if self._prev_width == event.size.width:
            return

        data_table = self.query_one(DataTable)

        # Ensure there is at least one column
        if data_table.columns:
            data_table.columns["summary"].width = round(event.size.width - 60)

            if data_table.row_count > 0:
                data_table.rows.clear()
            self._render_rows()

        self._prev_width = event.size.width

    def _render_rows(self):
        data_table = self.query_one(DataTable)
        for item in self._checker.failure_groups:
            cells = [item.title, item.failed_count, item.summary]
            data_table.add_row(*cells, height=None)

    def on_data_table_row_selected(self, row_selected):
        group: FailureGroup = self._checker.failure_groups[row_selected.cursor_row]
        index = row_selected.cursor_row
        title = group.title
        summary = group.summary

        self._current_group = ReportsTableScreen(
            columns=HEADERS[self._provider],
            items=group.objects,
            checker=self._checker,
            group=True,
            title=title,
            summary=summary,
        )

        # Track event: Selected group
        analytics.track_group_selection(index, group.title)

        self.app.push_screen(self._current_group)

    def update(self):
        self._current_group.update()
