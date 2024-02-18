# Utility functions for the rims scheme drawer

import json
from pathlib import Path
from typing import Dict

import matplotlib

DEFAULT_SETTINGS = {
    "settings": {
        "plot_title": "",
        "fig_width": 5.0,
        "fig_height": 8.0,
        "fs_title": 14,
        "fs_axes": 12,
        "fs_axes_labels": 12,
        "fs_labels": 14,
        "headspace": 2000,
        "arrow_width": 0.2,
        "arrow_head_width": 0.6,
        "prec_wavelength": 3,
        "prec_level": 0,
        "line_breaks": False,
        "ip_label_pos": "Top",
        "show_forbidden_transitions": "x-out",
        "show_cm-1_axis": True,
        "show_eV_axis": True,
    },
    "scheme": {
        "gs_term": "",
        "ip_term": "",
    },
}


def json_reader(fin: Path) -> Dict:
    """Read a json file and return a dictionary.

    This can take old or new files and return the data that
    can be read by the program.

    :return: Dictionary with parameters for drawing the scheme.
    """
    with open(fin, "r") as f:
        data = json.load(f)

    # check for new file format
    if "rims_scheme" in data.keys():
        data = data["rims_scheme"]

    return data


def my_formatter(val: float, *args) -> str:
    """Format the axis labels for the left y-axis in scientific notation.

    :param val: Value to format, must be >= 0.
    :param args: Additional arguments - will be ignored.

    :return: Properly formatted string.
    """
    fform = matplotlib.ticker.ScalarFormatter(useOffset=False, useMathText=True)
    fform.set_scientific((0, 0))
    if val <= 1e-9:  # some reasonable cutoff
        val_ret = "$0$"
    else:
        val_ret = f"${fform.format_data(val)}$"

    return val_ret


def term_to_string(tstr: str):
    """
    Converts a term symbol string to a LaTeX enabled matplotlib string
    :param tstr:   Input string to convert
    :return:       Output string LaTeX enabled for Matplotlib
    """
    if tstr == "":
        return None

    # some exceptionslike AI and IP
    if tstr == "IP":
        return "IP"
    if tstr == "AI":
        return "AI"
    if tstr == "Rydberg":
        return "Rydberg"
    if tstr == "Ryd":
        return "Ryd"

    # if there is an equal sign in there, leave it as is
    if tstr.find("=") != -1:
        return tstr

    # find the first slash and start looking for the letter after that
    start = tstr.find("/") + 1
    letterind = -1
    for it in range(start, len(tstr)):
        try:
            float(tstr[it])
        except ValueError:
            letterind = it
            break
    # if / comes after the letter:
    if letterind == -1:
        start = 0
        letterind = -1
        for it in range(start, len(tstr)):
            try:
                float(tstr[it])
            except ValueError:
                letterind = it
                break
    if letterind == -1:
        return tstr

    # set up the three parts for the latex string
    tmp1 = "$^{" + tstr[0:letterind] + "}$"
    tmp2 = tstr[letterind]
    tmp3 = "$_{" + tstr[letterind + 1 :] + "}$"

    return tmp1 + tmp2 + tmp3
