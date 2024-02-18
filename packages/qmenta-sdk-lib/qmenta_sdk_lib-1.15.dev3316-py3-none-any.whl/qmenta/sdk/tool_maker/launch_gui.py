#! /usr/bin/env python

import os
import textwrap

import PySimpleGUI as sg
import sys

from qmenta.sdk.tool_maker.make_files import (
    build_local_dockerfile,
    build_local_requirements,
    build_script,
    build_test, build_description,
)

sg.theme("DefaultNoMoreNagging")
FONT = "Consolas"
FONTSIZE = 10

MIN = 0
MAX_CORES = 50
MAX_RAM = 150

FOLDER = "local_tools"
sys.path.append(FOLDER)


def add_tooltip(message: str, width: int = 40) -> sg.PySimpleGUI.Text:
    """

    Parameters
    ----------
    message : str
        Text to put in the tool tip
    width: int
       How many characters per line of tool tip
    Returns
    -------
    The final tool tip string

    """
    return sg.T(
        " ? ", background_color="navy", text_color="white", tooltip="\n".join(textwrap.wrap(message, width=width))
    )


def gui():
    return [
        [
            sg.Image(os.path.join(os.path.dirname(__file__), "qmenta.png"), key="image")
        ],
        [
            sg.T(
                "Fill the fields and click on `Create` to automatically generate a new tool file structure.",
                font=f"{FONT} {FONTSIZE} bold",
            ),
            sg.T("(*) mandatory field.", font=f"{FONT} {FONTSIZE}"),
        ],
        [
            [sg.T("Specify the tool ID.*     ", justification="center"), sg.I(key="code", size=(15, 1))],
            [sg.T("Specify the tool version.*", justification="center"), sg.I(key="tool_version", size=(5, 1))],
        ],
        [sg.Push(), sg.Button("Create"), sg.Button("Cancel"), sg.Push()],
    ]


def launch_gui():
    window = sg.Window("Tool Maker", gui(), font=f"{FONT} {FONTSIZE} roman")

    while True:
        event, values = window.read()
        if event == "Cancel" or event in (sg.WIN_CLOSED, "Exit"):
            return None
        if event == "Create":
            # Do all checks
            try:
                assert isinstance(values["code"], str), "Tool ID must be a string."
                assert values["code"] != "", "Tool ID must be defined."
                assert " " not in values["code"], "Tool ID can't have spaces."
                values["code"] = values["code"].lower()  # must be lowercase
                if os.path.exists(os.path.join(FOLDER, values["code"])):
                    sg.popup_error(
                        f"AN EXCEPTION OCCURRED! The tool {values['code']} "
                        f"already exists. Choose a different ID."
                    )
                    continue
                sg.popup_auto_close(f"Tool created in folder {os.getcwd()} called {values['code']}")
                return values
            except AssertionError as e:
                sg.popup_error(f"AN EXCEPTION OCCURRED! {e}")

    window.close()


def main():
    content_build = launch_gui()
    if not content_build:
        exit()

    os.makedirs(os.path.join(FOLDER, content_build["code"]), exist_ok=True)
    os.chdir(os.path.join(FOLDER, content_build["code"]))
    build_description()
    build_script(code=content_build["code"])

    os.makedirs("local", exist_ok=True)
    os.chdir("local")

    build_local_requirements()
    build_local_dockerfile()
    build_test(
        content_build["code"],
        FOLDER,
        content_build["tool_version"],
    )


if __name__ == "__main__":
    main()
