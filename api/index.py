import os
import sys

# Vercel executes this file directly, so relative imports are not available.
# Add the api directory to sys.path so importing wavegen works.
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, Response, request
from wavegen import generate_wave_svg

app = Flask(__name__)


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
    wave_type = request.args.get("type", "smooth").lower()
    width     = min(max(int(request.args.get("width", 1200)), 200), 2400)
    height    = min(max(int(request.args.get("height", 80)), 20), 200)
    color_top = "#" + request.args.get("color_top", "0d1117").lstrip("#")
    color_bot = "#" + request.args.get("color_bottom", "161b22").lstrip("#")
    amplitude = min(max(float(request.args.get("amplitude", 20)), 1), 100)
    frequency = min(max(float(request.args.get("frequency", 1)), 0.5), 8)
    layers    = min(max(int(request.args.get("layers", 1)), 1), 3)
    flip      = request.args.get("flip", "false").lower() == "true"
    gradient  = request.args.get("gradient", "false").lower() == "true"
    mirror    = request.args.get("mirror", "false").lower() == "true"
    opacity   = min(max(float(request.args.get("opacity", 1)), 0.1), 1)
    animate   = request.args.get("animate", "false").lower() == "true"
    speed     = min(max(float(request.args.get("speed", 6)), 1), 20)
    text      = request.args.get("text", "")[:120]
    text_bottom = request.args.get("text_bottom", "")[:120]
    text_color = "#" + request.args.get("text_color", "ffffff").lstrip("#")
    text_bottom_color = "#" + request.args.get("text_bottom_color", "a5b4fc").lstrip("#")
    text_size = min(max(int(request.args.get("text_size", 28)), 8), 180)
    text_bottom_size = min(max(int(request.args.get("text_bottom_size", 22)), 8), 180)
    text_style = request.args.get("text_style", "normal").lower()
    text_stroke_color = "#" + request.args.get("text_stroke_color", "000000").lstrip("#")
    text_stroke_width = min(max(float(request.args.get("text_stroke_width", 0)), 0), 20)
    text_scale_x = min(max(float(request.args.get("text_scale_x", 100)), 50), 200)
    text_scale_y = min(max(float(request.args.get("text_scale_y", 100)), 50), 200)
    text_x    = min(max(float(request.args.get("text_x", 50)), 0), 100)
    text_y    = min(max(float(request.args.get("text_y", 45)), 0), 100)
    text_gap  = min(max(float(request.args.get("text_gap", 26)), 0), 200)
    text_align = request.args.get("text_align", "middle").lower()

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
