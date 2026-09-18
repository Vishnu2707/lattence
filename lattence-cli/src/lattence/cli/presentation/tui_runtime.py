import select
import sys
import termios
import tty

from lattence.evidence import SecurityPresentation

from .tui import TuiState, handle_presentation_key, render_tui

_ARROW_KEYS = {"A": "up", "B": "down", "C": "right", "D": "left"}


def _read_key() -> str:
    first = sys.stdin.read(1)
    if first in {"\r", "\n"}:
        return "enter"
    if first != "\x1b":
        return first
    ready, _, _ = select.select([sys.stdin], [], [], 0.03)
    if not ready:
        return "escape"
    second = sys.stdin.read(1)
    if second != "[":
        return "escape"
    ready, _, _ = select.select([sys.stdin], [], [], 0.03)
    return _ARROW_KEYS.get(sys.stdin.read(1), "escape") if ready else "escape"


def run_tui(presentation: SecurityPresentation, *, color: bool) -> None:
    descriptor = sys.stdin.fileno()
    previous = termios.tcgetattr(descriptor)
    state = TuiState()
    try:
        tty.setcbreak(descriptor)
        sys.stdout.write("\x1b[?1049h")
        while not state.quit_requested:
            sys.stdout.write("\x1b[2J\x1b[H")
            sys.stdout.write(render_tui(presentation, state, color=color))
            sys.stdout.flush()
            state = handle_presentation_key(presentation, state, _read_key())
    finally:
        termios.tcsetattr(descriptor, termios.TCSADRAIN, previous)
        sys.stdout.write("\x1b[?1049l")
        sys.stdout.flush()
