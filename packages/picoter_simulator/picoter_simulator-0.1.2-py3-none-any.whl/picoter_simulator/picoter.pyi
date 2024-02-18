from typing import Callable
from picoter_simulator.button import Button
from picoter_simulator.display import Display

class Picoter:
    def __init__(
        self,
        display: Display,
        buttons: list[Button],
    ) -> None: ...
    def start(self, mainfunc: Callable[[], None]) -> None: ...
