import reflex as rx

from shmooapp.config import *
from shmooapp.states.filestate import FileState


'''def render_subdirs() -> rx.Component:
    paths = FileState.subdirs
    """Render the list of selected folders."""
    return rx.vstack([
        rx.foreach(
            paths,
            lambda path: rx.text(path),
        )
    ])'''

def show_plotfiles(filelist:str,colorname:str) -> rx.Component:
    if filelist == "subfile":
        items = FileState.subfile_texts
    elif filelist == "aggfile":
        items = FileState.aggfile_texts
    elif filelist == "xorfile":
        items = FileState.xorfile_texts
    else:
        item = []
    return rx.foreach(
        items,
        lambda text:
            rx.box(
                rx.text(
                    text,
                    size="1",
                    white_space="pre-wrap",
                    font_family="'MS Gothic', 'BIZ UDゴシック', monospace",
                ),
                width="500px",
                #background_color="var(--plum-3)",
                background_color=f"var(--{colorname}-3)",
                margin="5px",
                boader="1px solid #ccc"
            ),
    )

def show_margins(colorname:str) -> rx.Component:
    return rx.foreach(
        FileState.margin_sets,
        lambda margin:
            rx.box(
                rx.text(f"OpCenter X: {margin[0]} -> Margin X: {margin[2]}"),
                rx.text(f"OpCenter Y: {margin[1]} -> Margin Y: {margin[3]}"),
                width="500px",
                background_color=f"var(--{colorname}-3)",
                margin="5px",
                boader="1px solid #ccc"
            ),
    )

def show_aggregation_labels(colorname:str) -> rx.Component:
    return rx.foreach(
        FileState.aggregation_sets,
        lambda agg:
            rx.box(
                rx.text(agg,color_scheme="indigo",align="center"),
                width="500px",
                background_color=f"var(--{colorname}-3)",
                margin="5px",
                boader="1px solid #ccc",
            ),
    )