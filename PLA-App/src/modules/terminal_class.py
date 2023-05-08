from textual.app import App, ComposeResult, RenderResult
from textual.widgets import Button, Header, Footer, Static
from textual.containers import Container, Horizontal, VerticalScroll, HorizontalScroll
from textual.reactive import reactive
import multiprocessing

from .database_orders_class import Database, Orders

from time import monotonic


def calculate_piece_cost():
    pass

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
        self.set_interval(56, self.update_day)
        self.day = 0

    def update_time(self):
        """Method to update the time to the current time."""
        self.time = monotonic() - self.start_time

    def update_day(self):
        """Method to update the time to the current time."""
        # _, seconds = divmod(time, 60)
        # if seconds >= 10.99:
        self.day += 1

    def watch_day(self, day: int) -> None:
        """Called when the day attribute changes."""
        self.update(f"Day: {day}")


class Plans(Static):
    """Display Plan Widget"""

    def render(self) -> RenderResult:
        return "Plans"


class OrdersWidget(Static):
    """Display Orders Widget"""

    order = None

    def set_order(self, order):
        self.order = order

    def render(self) -> RenderResult:
        return self.order


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
                db = Database()
                pending_orders_obj = Orders()
                pending_orders = pending_orders_obj.read_All_Orders()
                for order in pending_orders:
                    orders_widget_instance = OrdersWidget()  # Create an instance of the OrdersWidget class
                    orders_widget_instance.set_order(order)  # Call the set_order method on the instance
                    yield orders_widget_instance
            with Horizontal(id="top-right"):
                yield TimeDisplay()
                yield DayDisplay()
            with VerticalScroll(id="finished-orders-pane"):
                for _ in range(30):
                    pass
                    #yield Orders()
            with HorizontalScroll(id="bottom-right"):
                for _ in range(30):
                    yield Plans()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark
