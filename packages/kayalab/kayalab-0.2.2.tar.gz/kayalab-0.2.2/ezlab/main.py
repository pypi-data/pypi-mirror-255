#!/usr/bin/env python3
"""
Copyright 2023 Erdinc Kaya
DESCRIPTION:
    Deploy VMs on my lab and configure them for Ezmeral
USAGE EXAMPLE:
    > ezlab
"""

import json
import logging
import secrets
# import sys
from nicegui import ui, app, native
# sys.stdout = open("ezlogs.txt", "w")  # divert stdout to logs.txt file

from ezlab.app import LogElementHandler, ezmeral_menu, infra_menu, settings_menu

from ezlab.parameters import DF, SUPPORTED_HVES, UA

logger = logging.getLogger("ezlab")

# Initialize
# Top-level keys in config
for key in ["target", "ezui", "config", UA, DF, *SUPPORTED_HVES]:
    if not key in app.storage.general.keys():
        app.storage.general[key] = {}

app.storage.general["target"]["connected"] = False
app.native.start_args["debug"] = True

# Index page
@ui.page("/")
def main():
    # initial status
    app.storage.user["busy"] = False

    # Config show dialog
    with ui.dialog() as config_show, ui.card().classes("w-full h-full"):
        code_text = ui.code(
            json.dumps(app.storage.general, indent=2), language="json"
        ).classes("w-full text-wrap")

    def save_config(val: str, dialog):
        try:
            for key, value in json.loads(val.replace("\n", "")).items():
                app.storage.general[key] = value
            for menu in (settings_menu, ezmeral_menu, infra_menu):
                menu.refresh()
            dialog.close()
            ui.notify("Settings loaded", type="positive")
        except (TypeError, json.decoder.JSONDecodeError, ValueError) as error:
            ui.notify("Not a valid json", type="negative")
            print(error)

    # Config load dialog
    with ui.dialog() as config_set, ui.card().classes("w-full h-full"):
        jsontext = (
            ui.textarea()
            .props("stack-label=json autogrow filled")
            .classes("h-dvh w-full text-wrap")
        )
        ui.button("Save", on_click=lambda _: save_config(jsontext.value, config_set))

    # Header
    with ui.header(elevated=True).classes("items-center justify-between") as header:
        # home button
        ui.label("Ezlab").classes("text-bold text-lg")

        ui.space()

        with ui.row().classes("items-center"):
            ui.label("Settings")
            ui.button(icon="download", on_click=config_show.open)
            ui.button(icon="upload", on_click=config_set.open)

    # Footer
    with ui.footer() as footer:
        with ui.row().classes("w-full"):
            ui.label("Log")
            ui.space()
            ui.spinner("ios", size="2em", color="red").bind_visibility_from(
                app.storage.user, "busy"
            )
            ui.icon("check_circle", size="2em", color="green").bind_visibility_from(
                app.storage.user, "busy", lambda x: not x
            )
        log = ui.log().classes("w-full h-48 text-teal-400")
        logger.addHandler(LogElementHandler(log))

    # Content

    # Settings
    settings_menu()

    ui.separator()

    # Infrastructure
    infra_menu()

    ui.separator()

    # Ezmeral Products
    ezmeral_menu()

ezmeral_icon = """
<svg width="48" height="24" viewBox="0 0 48 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M7 8H41V16H7V8Z" fill="#01A982"/>
    <path d="M1 8H7V16H1V8Z" fill="#00775B"/>
    <path d="M41 8H47V16H41V8Z" fill="#00775B"/>
    <path d="M7 16H41V22H7V16Z" fill="#00775B"/>
    <path d="M7 2H41V8H7V2Z" fill="#00C781"/>
    <path d="M1 8L7 2V8H1Z" fill="#01A982"/>
    <path d="M1 16L7 22V16H1Z" fill="#01A982"/>
    <path d="M47 8L41 2V8H47Z" fill="#01A982"/>
    <path d="M47 16L41 22V16H47Z" fill="#01A982"/>
</svg>
"""

def enter():
    # ui.run(
    #     title="Ezlab",
    #     dark=None,
    #     favicon=ezmeral_icon,
    #     storage_secret=secrets.token_urlsafe(),
    #     show=True,
    #     # reload=False,
    # )
    ui.run(
        title="Ezlab",
        dark=None,
        native=True,
        window_size=(1024, 1024),
        # frameless=True,
        storage_secret=secrets.token_urlsafe(),
        reload=False,
        port=native.find_open_port(),
    )
