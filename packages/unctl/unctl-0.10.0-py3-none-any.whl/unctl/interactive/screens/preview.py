import re
import textwrap
from typing import cast
from attr import dataclass
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, TextArea, Footer, Label, ListView, ListItem

from unctl.config.config import get_config_instance


@dataclass
class PreviewReturn:
    outputs: dict[str, str]
    send_data: bool


class PreviewScreen(Screen[PreviewReturn]):
    CSS_PATH = "preview.tcss"
    TITLE = "Preview commands output"

    BINDINGS = [
        ("s", "send", "Run LLM analysis"),
        ("f", "mask", "Mask current"),
        ("ctrl+f", "mask_all", "Mask all"),
        ("r", "revert", "Revert current"),
        ("ctrl+r", "revert_all", "Revert all"),
        ("escape", "back", "Back"),
    ]

    _selected_item: str
    _updated_commands: dict[str, str]

    def __init__(
        self,
        commands: dict[str, str],
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ):
        super().__init__(name, id, classes)
        self._original_commands = commands
        self._updated_commands = commands.copy()

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

        cmds = list(self._updated_commands.keys())
        if len(cmds) > 0:
            self._selected_item = cmds[0]

        yield TextArea(
            self._updated_commands[self._selected_item],
            id="command-output",
        )

        list_items = [
            ListItem(
                Label(textwrap.fill(cmd, 28), id=f"cmd{index}"),
                id=cmd,
                classes="command-item",
            )
            for (index, cmd) in enumerate(cmds)
        ]
        yield ListView(*list_items, id="command-list")

    def on_mount(self):
        self.action_mask_all()

    @property
    def output_body(self) -> TextArea:
        return cast(TextArea, self.query_one("#command-output"))

    def action_mask(self):
        for mask in get_config_instance().anonymisation.masks:
            masked_data = re.sub(
                mask.pattern,
                f"<masked_{mask.name}>",
                self._updated_commands[self._selected_item],
            )
            self._updated_commands[self._selected_item] = masked_data
            self.output_body.text = masked_data

            self.update_list_item(item_id=self._selected_item, tag="masked")

    def action_mask_all(self):
        for cmd in self._updated_commands.keys():
            for mask in get_config_instance().anonymisation.masks:
                masked_data = re.sub(
                    mask.pattern, f"<masked_{mask.name}>", self._updated_commands[cmd]
                )
                self._updated_commands[cmd] = masked_data
                if self._selected_item == cmd:
                    self.output_body.text = masked_data

                self.update_list_item(item_id=cmd, tag="masked")

    def action_send(self):
        self.dismiss(PreviewReturn(self._updated_commands, True))

    def on_list_view_selected(self, item_selected):
        self._selected_item = item_selected.item.id
        self.output_body.text = self._updated_commands[item_selected.item.id]

    def on_text_area_changed(self):
        self._updated_commands[self._selected_item] = self.output_body.text
        self.update_list_item(item_id=self._selected_item, tag="edited")

    def action_back(self):
        self.dismiss(PreviewReturn(self._original_commands, False))

    def update_list_item(self, item_id: str, tag: str = None):
        id = list(self._updated_commands.keys()).index(item_id)
        label = self.query_one(f"#cmd{id}")

        new_label = f"{item_id}"
        if tag is not None:
            new_label = f"{new_label} ({tag})"

        new_label = textwrap.fill(new_label, 28)
        new_label = new_label.replace(f"({tag})", f"[bold red]({tag})[/bold red]")

        label.update(new_label)

    def action_revert(self):
        self._updated_commands[self._selected_item] = self._original_commands[
            self._selected_item
        ]
        self.update_list_item(item_id=self._selected_item)
        self.output_body.text = self._updated_commands[self._selected_item]

    def action_revert_all(self):
        for key in list(self._updated_commands.keys()):
            self._updated_commands[key] = self._original_commands[key]
            self.update_list_item(item_id=key)

        self.output_body.text = self._updated_commands[self._selected_item]
