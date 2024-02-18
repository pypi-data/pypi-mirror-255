from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import ModalScreen
from textual.widgets import Button, Label, TextArea


class ExecutionConfirm(ModalScreen[list[str]]):
    CSS_PATH = "confirm.tcss"

    def __init__(
        self,
        commands: list[str],
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ):
        super().__init__(name, id, classes)
        self.commands = commands

    def compose(self) -> ComposeResult:
        yield Container(
            Label(
                "Are you sure you want to execute next commands?",
                id="question",
            ),
            TextArea(
                "\n".join(self.commands),
                language="python",
                id="content",
            ),
            Container(
                Button("Execute", variant="success", id="execute"),
                Button("Cancel", variant="primary", id="cancel"),
                classes="buttons",
            ),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "execute":
            text_area: TextArea = self.query_one("#content")
            actual_commands = text_area.text.split("\n")
            self.dismiss(actual_commands)
        else:
            self.app.pop_screen()
