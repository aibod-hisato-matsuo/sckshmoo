import reflex as rx

# state related
PLOTSDIR = "out.plot"
ARCHIVEDIR = "out.archive"


# ref
# https://reflex.dev/docs/styling/overview/

color = "rgb(107,99,246)"

# global style
global_style = {
    # Set the selection highlight color globally.
    "::selection": {
        "background_color": "blue",
    },
    # Apply global css class styles.
    ".some-css-class": {
        "text_decoration": "underline",
    },
    # Apply global css id styles.
    "#special-input": {"width": "20vw"},
    # Apply styles to specific components.
    rx.text: {
        "font_family": "'MS Gothic', 'BIZ UDゴシック', monospace",
    },
    rx.divider: {
        "margin_bottom": "1em",
        "margin_top": "0.5em",
    },
    rx.heading: {
        "font_weight": "500",
    },
    rx.code: {
        "color": "green",
    },
}


#
text_style_top = {
    "color": "green",
    "font_family": "Comic Sans MS",
    "font_size": "1.2em",
    "font_weight": "bold",
    "box_shadow": "rgba(240, 46, 170, 0.4) 5px 5px, rgba(240, 46, 170, 0.3) 10px 10px",
}

button_style_child = {
    "textAlign": "left",
    "width": "800px",
    "marginLeft": "40px",
    "spacing": "0",
    "bg": "white",
    "border": f"1px solid {color}",
    "_hover": {"backgroundColor": "lightgray"},
    "_active": {"backgroundColor": "gray"},
}