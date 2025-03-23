import reflex as rx

from shmooapp.config import *
from shmooapp.states.filestate import FileState
from shmooapp.pages.common_func import *


def page02():
    return rx.vstack(
        rx.hstack(
            rx.text("ログのPlotを見る",style=text_style_top),
            rx.link(
                rx.button(
                    "ホームに戻る",
                    on_click=FileState.clear_vars,
                    color="indigo",
                    bg="white",
                    border=f"1px solid {color}",
                ),
                href="/",
                is_external=False,
            ),
        ),
        rx.divider(),
        rx.vstack(
            rx.text(f"選択されたログ: {FileState.pathstr}",size="5",color_scheme="indigo"),
            rx.vstack(
                rx.foreach(
                    FileState.subdirs,
                    lambda dir: rx.button(
                        dir,
                        on_click=lambda dir=dir: FileState.set_plots_vars(dir),
                        color=color,
                        style=button_style_child,
                    ),
                ),
                rx.text(f"--> 選択されたテスト：{FileState.curdir}",size="4",color_scheme="gray"),
                margin_left = "10px"
            ),
        ),
        rx.vstack(
            rx.vstack(
                rx.text("Original Plots",size="4",color_scheme="indigo"),
                rx.flex(
                    show_margins("cyan"),
                ),
                rx.flex(
                    show_plotfiles("subfile","gray"),
                ),
                rx.text("Aggregated Plots",size="4",color_scheme="indigo"),
                rx.flex(
                    show_aggregation_labels("indigo"),
                ),
                rx.flex(
                    show_plotfiles("aggfile","gray"),
                ),
            ),
        ),
        rx.divider(),
        rx.link("ホームに戻る", href="/"),
        rx.link("Plotへ戻る", href="/proc01"),
        margin_left = "10px"
    )