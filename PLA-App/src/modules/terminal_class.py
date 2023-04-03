from textual.app import App, ComposeResult, RenderResult
from textual.widgets import Button, Header, Footer, Static
from textual.containers import Container, Horizontal, VerticalScroll, HorizontalScroll
from textual.reactive import reactive

from time import monotonic


class TimeDisplay(Static):
    """A widget to display elapsed time."""

    start_time = reactive(monotonic())
    time = reactive(0.0)

    def _on_mount(self) -> None:
        """Event handler called when widget is added to the app."""
        self.set_interval(1 / 60, self.update_time)

    def update_time(self):
        """Method to update the time to the current time."""
        self.time = monotonic() - self.start_time

    def watch_time(self, time: float) -> None:
        """Called when the time attribute changes."""
        _, seconds = divmod(time, 60)
        self.update(f"Day Time: {seconds:.2f}")


class DayDisplay(Static):
    """A widget to display the Day."""

    start_time = reactive(monotonic())
    time = reactive(0.0)

    day = reactive(0)

    def _on_mount(self) -> None:
        """Event handler called when widget is added to the app."""
        self.set_interval(1 / 60, self.update_time)
        self.day = 0

    def update_time(self):
        """Method to update the time to the current time."""
        self.time = monotonic() - self.start_time

    def update_day(self, time: float):
        """Method to update the time to the current time."""
        _, seconds = divmod(time, 60)
        if seconds >= 10.99:
            self.day += 1

    def watch_day(self, day: int) -> None:
        """Called when the day attribute changes."""
        self.update(f"Day: {day}")


class Plans(Static):
    """Display Plan Widget"""

    def render(self) -> RenderResult:
        return "Plans"


class Orders(Static):
    """Display Orders Widget"""

    def render(self) -> RenderResult:
        return "Orders"


class ErpTerminal(App):
    """Applications main terminal"""

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]
    CSS_PATH = ".././css/erp_terminal.css"
    TITLE = "Enterprise Management Terminal"

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        with Container(id="app-grid"):
            with VerticalScroll(id="pending-orders-pane"):
                for _ in range(30):
                    yield Orders()
            with Horizontal(id="top-right"):
                yield TimeDisplay()
                yield DayDisplay()
            with VerticalScroll(id="finished-orders-pane"):
                for _ in range(30):
                    yield Orders()
            with HorizontalScroll(id="bottom-right"):
                for _ in range(30):
                    yield Plans()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark
