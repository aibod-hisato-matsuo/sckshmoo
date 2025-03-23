import reflex as rx

from shmooapp.config import *
from shmooapp.states.filestate import FileState
from shmooapp.pages.common_func import *


def page01():
    color = "rgb(107,99,246)"
    return rx.vstack(
        rx.hstack(
            rx.text(f"『{FileState.file_paths}』を解析する",style=text_style_top),
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
            margin_left = "10px",
            spacing = "5"
        ),
        rx.divider(),
        rx.vstack(
            rx.hstack(
                rx.text("Step1 : ",size="5",color_scheme="indigo"),
                rx.button(
                    "ログファイルからテスト項目を取り出す",
                    on_click=FileState.run_process01_1,
                ),
            ),
            rx.hstack(
                rx.text("Step2 : ボタンをタップして各テストのPlotを表示する",size="5",color_scheme="indigo"),
            ),
            rx.vstack(
                rx.foreach(
                    FileState.subdirs,
                    lambda dir: rx.button(
                        dir,
                        #on_click=lambda dir=dir: FileState.p01_read_plots(dir),
                        on_click=lambda dir=dir: FileState.run_each_test(dir),
                        color=color,
                        style=button_style_child,
                    ),
                ),
                rx.text(f"--> 選択されたテスト：{FileState.curdir}",size="4",color_scheme="gray"),
                margin_left = "10px"
            ),
            #rx.hstack(
            #    rx.text("Step2 : ",size="5",color_scheme="indigo"),
            #    rx.button(
            #        "Calculate Range and Margin",
            #        on_click=FileState.run_each_test(),
            #    ),
            #),
            rx.vstack(
                rx.text("Margin",size="4",color_scheme="indigo"),
                rx.hstack(
                    show_margins("cyan"),
                ),
                rx.text("Plotファイル",size="4",color_scheme="indigo"),
                rx.hstack(
                    show_plotfiles("subfile","gray"),
                ),
                margin_left = "10px"
            ),
            margin_left = "10px",
        ),
        rx.vstack(
            rx.hstack(
                rx.text("-> テスト結果のAggregation : ",size="5",color_scheme="indigo"),
                #rx.button(
                #    "Aggregate Test Results -- OR, AND, MajorityVote",
                #    on_click=FileState.run_process02_1_calc,
                #),
            ),
            rx.vstack(
                rx.text("OR   モード : サイトに一つでもPがあるとPとなります。"),
                rx.text("AND  モード : サイトがすべてPのときPとなります。"),
                rx.text("多数決モード : サイト結果でPが多いときPとなります。"),
                spacing= "0",
                margin_left = "20px",
            ),
            rx.vstack(
                rx.text("Aggregationファイル",size="4",color_scheme="indigo"),
                rx.text(FileState.aggregation_file_or,color_scheme="gray"),
                rx.text(FileState.aggregation_file_and,color_scheme="gray"),
                rx.text(FileState.aggregation_file_mj,color_scheme="gray"),
                spacing= "0",
                margin_left = "10px"
            ),
            rx.vstack(
                rx.text("Aggregation Plotファイル",size="4",color_scheme="indigo"),
                rx.flex(
                    show_aggregation_labels("indigo"),
                ),
                rx.flex(
                    show_plotfiles("aggfile","gray"),
                ),
                margin_left = "10px"
            ),
            rx.hstack(
                rx.text("-> Aggregationと各サイトの差分を確認する : ",size="5",color_scheme="indigo"),
                rx.foreach(
                    FileState.aggregation_sets,
                    lambda agg: rx.button(
                        agg,
                        on_click=lambda dir=dir: FileState.run_process02_2_calc(agg),
                        width = "160px"
                    ),
                ),
            ),
            rx.vstack(
                rx.text(FileState.xordir),
                rx.text("XORプロット",size="4",color_scheme="indigo"),
                rx.flex(
                    show_plotfiles("xorfile","violet"),
                ),
                margin_left = "10px",
            ),
            margin_left = "10px",
        ),
        rx.divider(),
        #rx.link("ホームに戻る", href="/"),
        #rx.link("ALL Plotsへ", href="/page02"),
    )
