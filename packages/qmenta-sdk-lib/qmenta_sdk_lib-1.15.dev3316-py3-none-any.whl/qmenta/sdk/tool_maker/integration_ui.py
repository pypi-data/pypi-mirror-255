#! /usr/bin/env python

import os
import re
import textwrap

import PySimpleGUI as sg
from qmenta.core import platform

sg.theme("Dark Grey 15")
FONT = "Consolas"
FONTSIZE = 10

MIN = 0
MAX_CORES = 10
MAX_RAM = 16


def add_tooltip(message: str, width: int = 50) -> sg.PySimpleGUI.Text:
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
                "Fill the fields and click create to automatically publish a new tool to the platform.",
                font=f"{FONT} {FONTSIZE} bold",
            )
        ],
        [
            sg.T("(*) mandatory field."),
        ],
        [sg.Text()],
        [
            sg.T("QMENTA Platform credentials."),
        ],
        [
            sg.T("Username*"),
            sg.I(key="qmenta_user", size=(15, 1)),
            sg.T("Password*"),
            sg.I(key="qmenta_password", size=(15, 1), password_char='*')
        ],
        [sg.Text()],
        [sg.T("Select folder where the tool is stored*")],
        [
            sg.I(
                size=(50, 1),
                key="folder"
            ),
            sg.FolderBrowse(size=(10, 1)),
        ],
        [sg.T("Specify the tool name*"), sg.Input(key="name", size=(40, 1))],
        [
            sg.T("Version*              "),
            sg.Input(key="version", size=(9, 1)),
        ],
        [sg.Text()],
        [
            sg.T(f"How many cores does the tool require? (integer, max. {MAX_CORES})     "),
            sg.I(key="cores", default_text="1", size=(4, 1)),
        ],
        [
            sg.T(f"How many GB of RAM does the tool require? (integer, max. {MAX_RAM})"),
            sg.I(key="memory", default_text="1", size=(4, 1)),
        ],
        [sg.Text()],
        [
            sg.T("Docker image registry and credentials."),
            add_tooltip("Credentials need to be valid in order to be able to pull the Docker image from the registry")
        ],
        [
            sg.T("Image Name         "),
            sg.I(key="image_name", size=(40, 1)),
        ],
        [
            sg.T("Repository URL     "),
            sg.I(key="repository_url", default_text="hub.docker.com", size=(40, 1)),
        ],
        [
            sg.T("Repository User    "),
            sg.I(key="repository_user", size=(40, 1)),
        ],
        [
            sg.T("Repository Password"),
            sg.I(key="repository_password", size=(40, 1), password_char='*'),
        ],
        [sg.Text()],
        [sg.Push(), sg.Button("Publish"), sg.Button("Cancel"), sg.Push()],
    ]


def launch_gui():
    window = sg.Window("Tool Publisher", gui(), font=f"{FONT} {FONTSIZE} roman", margins=(20, 10, 20, 10))

    while True:
        event, values = window.read()
        if event == "Cancel" or event in (sg.WIN_CLOSED, "Exit"):
            return None
        if event == "Publish":
            # Do all checks
            try:
                assert values["folder"] != "", "Folder must be defined."
                assert os.path.exists(values["folder"]), "Folder must exist."
                values["code"] = os.path.basename(values["folder"])  # the folder stored has the tool id

                assert " " not in values["code"], "Tool ID can't have spaces."
                values["short_name"] = values["code"].lower().replace(" ", "_")  # must be lowercase

                assert isinstance(values["name"], str), "Tool name must be a string."
                assert values["name"] != "", "Tool name must be defined."

                assert values["version"] != "", "Tool version must be defined."
                assert re.search(r"^(\d+\.)?(\d+\.)?(\*|\d+)$", values["version"]), "Version format not valid."

                assert values["cores"], "Number of cores must be defined."
                assert values["cores"].isnumeric(), "Number of cores must be an integer."
                assert MAX_CORES >= int(values["cores"]) > MIN, (f"Number of cores must be between {MIN} "
                                                                 f"and {MAX_CORES}.")

                assert values["memory"], "RAM must be defined."
                assert values["memory"].isnumeric(), "RAM must be an integer."
                assert MAX_RAM >= int(values["memory"]) > MIN, f"RAM must be {MIN} and {MAX_RAM}."
                values["memory"] = int(values["memory"])
                values["image_name"] = values["image_name"] or values["code"] + ":" + values["version"]

                sg.popup_auto_close("Tool created published to the platform!")
                window.close()

                return values
            except AssertionError as e:
                sg.popup_error_with_traceback("An error happened. Here is the info:", e)


def main():
    content_build = launch_gui()
    if content_build:
        tools_fd = content_build["folder"]
        os.chdir(tools_fd)

        user = content_build["qmenta_user"]
        password = content_build["qmenta_password"]

        auth = platform.Auth.login(
            username=user,
            password=password,
            base_url='https://platform.qmenta.com',
            ask_for_2fa_input=True
        )

        # Get information from the advanced options file.
        with open(os.path.join(content_build["folder"], "settings.json")) as fr:
            content_build["advanced_options"] = fr.read()

        # Get information from the results configuration file.
        if os.path.exists(os.path.join(content_build["folder"], "results_configuration.json")):
            with open("results_configuration.json") as fr:
                content_build["results_configuration"] = fr.read()

        # Get information from the description file.
        with open(os.path.join(content_build["folder"], "description.html")) as fr:
            description = fr.read()

        content_build.update({
            "start_condition_code": "output={'OK': True, 'code': 1}",
            "description": description,
            "entry_point": "/root/entrypoint.sh",
            "tool_path": "tool:run"
        })

        # After creating the workflow, the ID of the workflow must be requested and added to the previous dictionary
        # otherwise it will keep creating new workflows on the platform creating conflicts.
        res = platform.post(
            auth, 'analysis_manager/upsert_user_tool',
            data=content_build
        )
        if res.json()["success"] == 1:
            print("Tool updated successfully!")
            print("Tool name:", content_build["name"], "(", content_build["code"], ":", content_build["version"], ")")
        else:
            print("ERROR setting the tool.")
            print(res.json())


if __name__ == "__main__":
    main()
