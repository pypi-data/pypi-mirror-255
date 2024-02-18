"""Entry point for the GUI."""

import sys

try:
    from qtpy import QtWidgets
except ImportError as e:
    raise ImportError(
        "No GUI environment found. Please install rimsschemedrawer with option [gui]."
    ) from e

from rimsschemedrawer.gui import SchemeDrawer


def run_gui():
    """Launch the GUI."""
    application = QtWidgets.QApplication(sys.argv)
    window = SchemeDrawer()
    window.show()
    application.exec()


if __name__ == "__main__":
    run_gui()
