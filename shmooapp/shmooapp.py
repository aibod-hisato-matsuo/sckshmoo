"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx

from rxconfig import config
from shmooapp.config import *
from shmooapp.states.filestate import FileState
from shmooapp.pages.page01 import page01
from shmooapp.pages.page02 import page02


def shmoo_main() -> rx.Component:
    color = "rgb(107,99,246)"
    return rx.vstack(
        rx.text("Step1 : SHMOOログファイルを選択してください",size="5",color_scheme="indigo"),
        rx.upload(
            rx.vstack(
                rx.button(
                    "Select SHMOO log file",
                    color=color,
                    bg="white",
                    border=f"1px solid {color}",
                ),
                rx.text(
                    "Drag and drop folders here or click to select a folder"
                ),
            ),
            id="upload1",
            border=f"1px dotted {color}",
            padding="5em",
            # Enable directory selection
            #directory=True,  # This enables folder selection
            #multiple=True,    # Allows multiple folders if needed
            #on_drop=State.handle_upload,  # Attach the upload handler
        ),
        rx.hstack(
            rx.foreach(
                rx.selected_files("upload1"), rx.text
            )
        ),
        rx.vstack(
            rx.text("Step2 : 選択したログファイルの登録",size="5",color_scheme="indigo"),
            rx.button(
                "選択したログファイルを登録する",
                on_click=FileState.handle_upload(
                    rx.upload_files(upload_id="upload1")
                ),
            ),
        ),
        rx.text("登録されたSHMOOログ"),
        rx.hstack(
            rx.foreach(
                FileState.file_paths, rx.text
            ),
        ),
        rx.hstack(
            rx.vstack(
                rx.text("Step3 : すべてのPlotを生成する",size="5",color_scheme="indigo"),
                rx.button(
                    "すべてのSHMOOプロットを生成する！",
                    on_click=FileState.run_all_tests,
                ),
                rx.text("登録されたログファイルをアーカイブする"),
                rx.button(
                    "Archive plots",
                    color=color,
                    bg="white",
                    border=f"1px solid {color}",
                    on_click=FileState.run_archive,
                ),
            ),
            rx.text("または"),
            rx.vstack(
                rx.text("Step3 : ログファイルのPlotを見る",size="5",color_scheme="indigo"),
                rx.hstack(
                    rx.link(
                        rx.button(
                            "SHMOO Plotを見る！",
                            on_click=FileState.handle_upload(
                                rx.upload_files(upload_id="upload1")
                            ),
                        ),
                        href="/page01",
                        is_external=False,
                    ),
                    rx.text("    ページを移動します"),
                ),
            rx.text("登録されたログのPlot情報を削除する"),
            rx.button(
                "Clear Vars",
                color=color,
                bg="white",
                border=f"1px solid {color}",
                on_click=FileState.clear_vars,
            ),
            ),
        ),
        rx.divider(),
        rx.vstack(
            rx.text("Step4 : アーカイブされたログを読み込む",size="5",color_scheme="indigo"),
            rx.button(
                "Collect Archived logs",
                on_click=FileState.get_archived_log,
            ),
            rx.foreach(
                FileState.archived_logs,
                lambda log: rx.link(
                    rx.button(
                        log,
                        on_click=lambda log=log: FileState.set_archived_log_for_view(log),
                        color=color,
                        style=button_style_child,
                    ),
                    href="/page02",
                    is_external=False,
                ),
            ),
            rx.text(f"--> 選択されたテスト：{FileState.curdir}",size="4",color_scheme="gray"),
        ),
    )

def sample_main() -> rx.Component:
    return rx.vstack(
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            rx.heading("Welcome to Reflex!", size="9"),
            rx.text(
                "Get started by editing ",
                rx.code(f"{config.app_name}/{config.app_name}.py"),
                size="5",
            ),
            rx.link(
                rx.button("Check out our docs!"),
                href="https://reflex.dev/docs/getting-started/introduction/",
                is_external=True,
            ),
            spacing="5",
            justify="center",
            min_height="5vh",
        ),
        rx.logo(),
    )


def index() -> rx.Component:
    # Welcome Page (Index)
    return rx.container(
        #sample_main(),
        shmoo_main(),
    )


app = rx.App()
app.add_page(index)
app.add_page(page01,route="/page01")
app.add_page(page02,route="/page02")