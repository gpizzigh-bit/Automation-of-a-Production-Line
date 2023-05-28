from lib2to3.pgen2.driver import Driver
from typing import Type

from textual.app import App, ComposeResult, RenderResult, CSSPathType
from textual.widgets import Button, Header, Footer, Static
from textual.containers import Container, Horizontal, VerticalScroll, HorizontalScroll
from textual.reactive import reactive
import multiprocessing

from .database_orders_class import Database, Orders, Concluded
from .MPS import Scheduler

from time import monotonic


def calculate_piece_cost():
    pass


def list_to_string(lst):
    str_lst = [str(elem) for elem in lst]
    return "\n".join(str_lst)


class ErrorHandling(Static):
    def render(self) -> RenderResult:
        return "Running Scheduler..."


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
        # self.set_interval(56, self.update_day)
        self.day = 0  # 0

    def update_time(self):
        """Method to update the time to the current time."""
        self.time = monotonic() - self.start_time

    def update_day(self, day):
        """Method to update the time to the current time."""
        # _, seconds = divmod(time, 60)
        # if seconds >= 10.99:
        # self.day += 1
        self.day = day

    def watch_day(self, day: int) -> None:
        """Called when the day attribute changes."""
        self.update(f"Day: {day}")


class Plans(Static):
    """Display Plan Widget"""

    plan = None

    def set_plan(self, plan):
        self.plan = plan

    def render(self) -> RenderResult:
        return self.plan


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

    # mps = Scheduler()
    # print(mps.get_plans_list())
    # for plans in mps.get_plans_list():
    #     plans_obj = Plans()
    #     print(plans)

    def __init__(
            self,
            driver_class: Type[Driver] | None = None,
            css_path: CSSPathType | None = None,
            watch_css: bool = False,
    ):
        super().__init__(driver_class, css_path, watch_css)
        self.erp_day = None
        self.mps_obj = None

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        with Container(id="app-grid"):
            with VerticalScroll(id="pending-orders-pane"):
                pending_orders_obj = Orders()
                pending_orders = pending_orders_obj.read_All_Orders()
                for order in pending_orders:
                    orders_widget_instance = OrdersWidget()  # Create an instance of the OrdersWidget class
                    orders_widget_instance.set_order(order)  # Call the set_order method on the instance
                    yield orders_widget_instance
            with Horizontal(id="top-right"):
                yield TimeDisplay()
                day_obj = DayDisplay()
                day_obj.update_day(self.erp_day)
                yield day_obj
            with VerticalScroll(id="finished-orders-pane"):
                concluded_orders = Concluded()
                concluded_orders = concluded_orders.read_All_Concluded()
                for order in concluded_orders:
                    orders_widget_instance = OrdersWidget()  # Create an instance of the OrdersWidget class
                    orders_widget_instance.set_order(order)  # Call the set_order method on the instance
                    yield orders_widget_instance
            with HorizontalScroll(id="bottom-right"):
                if self.mps_obj is not None:
                    mps = self.mps_obj
                    if mps.get_plans_list() is not None:
                        for plans in mps.get_plans_list():
                            plans_obj = Plans()
                            if plans == "P1 and P2 restock":
                                plans_obj.set_plan(
                                    list_to_string(plans) + "\nSupplier for P1: " + mps.get_suppliers()[0] +
                                    "\n Supplier for P2: " + mps.get_suppliers()[1])
                            elif plans == "P1 restock":
                                plans_obj.set_plan(
                                    list_to_string(plans) + "\nSupplier for P1: " + mps.get_suppliers()[0])

                            elif plans == "P2 restock":
                                plans_obj.set_plan(
                                    list_to_string(plans) + "\nSupplier for P2: " + mps.get_suppliers()[1])
                            else:
                                plans_obj.set_plan(list_to_string(plans))
                            yield plans_obj
                else:
                    yield ErrorHandling()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    def show_new_plans(self, mps_obj):
        self.mps_obj = mps_obj

    def change_day(self, day):
        self.erp_day = day
