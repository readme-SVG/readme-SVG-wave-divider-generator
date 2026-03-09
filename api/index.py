import os
import re
import sys

# Vercel executes this file directly, so relative imports are not available.
# Add the api directory to sys.path so importing wavegen works.
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, Response, request
from wavegen import generate_wave_svg

app = Flask(__name__)

HEX_COLOR_RE = re.compile(r"^[0-9a-fA-F]{3}([0-9a-fA-F]{3})?$")


def _parse_bool_arg(name: str, default: bool = False) -> bool:
    value = request.args.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_int_arg(name: str, default: int, min_value: int, max_value: int) -> int:
    raw = request.args.get(name)
    try:
        value = int(raw) if raw is not None else default
    except (TypeError, ValueError):
        value = default
    return min(max(value, min_value), max_value)


def _parse_float_arg(name: str, default: float, min_value: float, max_value: float) -> float:
    raw = request.args.get(name)
    try:
        value = float(raw) if raw is not None else default
    except (TypeError, ValueError):
        value = default
    return min(max(value, min_value), max_value)


def _parse_color_arg(name: str, default: str) -> str:
    raw = request.args.get(name)
    if not raw:
        return default
    normalized = raw.strip().lstrip("#")
    if HEX_COLOR_RE.fullmatch(normalized):
        return f"#{normalized.lower()}"
    return default


def _parse_enum_arg(name: str, default: str, allowed: set[str]) -> str:
    raw = request.args.get(name)
    if raw is None:
        return default
    normalized = raw.strip().lower()
    return normalized if normalized in allowed else default


@app.route("/")
def index():
    html_path = os.path.join(os.path.dirname(__file__), "..", "index.html")
    with open(os.path.abspath(html_path), "r", encoding="utf-8") as f:
        content = f.read()
    return Response(content, mimetype="text/html")


@app.route("/styles.css")
def styles():
    css_path = os.path.join(os.path.dirname(__file__), "..", "styles.css")
    with open(os.path.abspath(css_path), "r", encoding="utf-8") as f:
        content = f.read()
    return Response(content, mimetype="text/css")


@app.route("/app.js")
def app_js():
    js_path = os.path.join(os.path.dirname(__file__), "..", "app.js")
    with open(os.path.abspath(js_path), "r", encoding="utf-8") as f:
        content = f.read()
    return Response(content, mimetype="application/javascript")


@app.route("/wave")
def wave():
    wave_type = _parse_enum_arg("type", "smooth", {"smooth", "sine", "bump", "zigzag", "triangle"})
    width = _parse_int_arg("width", 1200, 200, 2400)
    height = _parse_int_arg("height", 80, 20, 200)
    color_top = _parse_color_arg("color_top", "#0d1117")
    color_bot = _parse_color_arg("color_bottom", "#161b22")
    amplitude = _parse_float_arg("amplitude", 20.0, 1.0, 100.0)
    frequency = _parse_float_arg("frequency", 1.0, 0.5, 8.0)
    layers = _parse_int_arg("layers", 1, 1, 3)
    flip = _parse_bool_arg("flip", False)
    gradient = _parse_bool_arg("gradient", False)
    mirror = _parse_bool_arg("mirror", False)
    opacity = _parse_float_arg("opacity", 1.0, 0.1, 1.0)
    animate = _parse_bool_arg("animate", False)
    speed = _parse_float_arg("speed", 6.0, 1.0, 20.0)
    text      = request.args.get("text", "")[:120]
    text_bottom = request.args.get("text_bottom", "")[:120]
    text_color = _parse_color_arg("text_color", "#ffffff")
    text_bottom_color = _parse_color_arg("text_bottom_color", "#a5b4fc")
    text_size = _parse_int_arg("text_size", 28, 8, 180)
    text_bottom_size = _parse_int_arg("text_bottom_size", 22, 8, 180)
    text_style = _parse_enum_arg("text_style", "normal", {"normal", "italic", "bold", "bolditalic"})
    text_stroke_color = _parse_color_arg("text_stroke_color", "#000000")
    text_stroke_width = _parse_float_arg("text_stroke_width", 0.0, 0.0, 20.0)
    text_scale_x = _parse_float_arg("text_scale_x", 100.0, 50.0, 200.0)
    text_scale_y = _parse_float_arg("text_scale_y", 100.0, 50.0, 200.0)
    text_x = _parse_float_arg("text_x", 50.0, 0.0, 100.0)
    text_y = _parse_float_arg("text_y", 45.0, 0.0, 100.0)
    text_gap = _parse_float_arg("text_gap", 26.0, 0.0, 200.0)
    text_align = _parse_enum_arg("text_align", "middle", {"start", "middle", "end"})

    svg = generate_wave_svg(
        wave_type=wave_type,
        width=width,
        height=height,
        color_top=color_top,
        color_bottom=color_bot,
        amplitude=amplitude,
        frequency=frequency,
        layers=layers,
        flip=flip,
        gradient=gradient,
        mirror=mirror,
        opacity=opacity,
        animate=animate,
        speed=speed,
        text=text,
        text_bottom=text_bottom,
        text_color=text_color,
        text_bottom_color=text_bottom_color,
        text_size=text_size,
        text_bottom_size=text_bottom_size,
        text_style=text_style,
        text_stroke_color=text_stroke_color,
        text_stroke_width=text_stroke_width,
        text_scale_x=text_scale_x,
        text_scale_y=text_scale_y,
        text_x=text_x,
        text_y=text_y,
        text_gap=text_gap,
        text_align=text_align,
    )

    return Response(
        svg,
        mimetype="image/svg+xml",
        headers={
            "Cache-Control": "public, max-age=3600",
            "Access-Control-Allow-Origin": "*",
        },
    )
