import math
import random


def _esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;")
    )


def _hex_to_rgb(hex_color: str) -> tuple:
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return r, g, b


def _build_wave_path(
    width: int,
    height: int,
    amplitude: float,
    frequency: float,
    phase: float = 0.0,
    points: int = 100,
    fill_bottom: bool = True,
    y_offset: float = 0.5,
    inverted: bool = False,
) -> str:
    """
    Build an SVG path for a sine-based wave.
    y_offset: 0=top, 0.5=middle, 1=bottom of the SVG height
    """
    mid_y = height * y_offset

    coords = []
    for i in range(points + 1):
        x = (i / points) * width
        direction = -1 if inverted else 1
        y = mid_y + direction * amplitude * math.sin(2 * math.pi * frequency * (i / points) + phase)
        coords.append((x, y))

    path = f"M {coords[0][0]:.2f} {coords[0][1]:.2f} "
    path += " ".join(f"L {x:.2f} {y:.2f}" for x, y in coords[1:])

    if fill_bottom:
        path += f" L {width} {height} L 0 {height} Z"
    else:
        path += f" L {width} 0 L 0 0 Z"

    return path


def _build_smooth_wave_path(
    width: int,
    height: int,
    amplitude: float,
    frequency: float,
    phase: float = 0.0,
    points: int = 60,
    fill_bottom: bool = True,
    y_offset: float = 0.5,
    inverted: bool = False,
) -> str:
    """Smooth cubic bezier wave path."""
    mid_y = height * y_offset
    step = width / points

    coords = []
    for i in range(points + 1):
        x = i * step
        direction = -1 if inverted else 1
        y = mid_y + direction * amplitude * math.sin(2 * math.pi * frequency * (i / points) + phase)
        coords.append((x, y))

    path = f"M {coords[0][0]:.2f} {coords[0][1]:.2f} "
    for i in range(1, len(coords)):
        x0, y0 = coords[i - 1]
        x1, y1 = coords[i]
        cx = (x0 + x1) / 2
        path += f"C {cx:.2f} {y0:.2f} {cx:.2f} {y1:.2f} {x1:.2f} {y1:.2f} "

    if fill_bottom:
        path += f"L {width} {height} L 0 {height} Z"
    else:
        path += f"L {width} 0 L 0 0 Z"

    return path


def _build_zigzag_path(
    width: int,
    height: int,
    amplitude: float,
    frequency: float,
    fill_bottom: bool = True,
    y_offset: float = 0.5,
    inverted: bool = False,
) -> str:
    mid_y = height * y_offset
    peaks = max(2, int(frequency * 12))
    step = width / peaks

    points = []
    for i in range(peaks + 1):
        x = i * step
        y = mid_y + (-amplitude if i % 2 == 0 else amplitude) if inverted else mid_y + (amplitude if i % 2 == 0 else -amplitude)
        points.append((x, y))

    path = f"M {points[0][0]:.2f} {points[0][1]:.2f} "
    path += " ".join(f"L {x:.2f} {y:.2f}" for x, y in points[1:])
    if fill_bottom:
        path += f" L {width} {height} L 0 {height} Z"
    else:
        path += f" L {width} 0 L 0 0 Z"
    return path


def _build_bump_path(
    width: int,
    height: int,
    amplitude: float,
    frequency: float,
    fill_bottom: bool = True,
    y_offset: float = 0.5,
    inverted: bool = False,
) -> str:
    mid_y = height * y_offset
    bumps = max(1, int(frequency * 6))
    bw = width / bumps

    if inverted:
        mid_y = height * y_offset

    path = f"M 0 {mid_y:.2f} "
    for i in range(bumps):
        x0 = i * bw
        x1 = x0 + bw / 2
        x2 = x0 + bw
        cy = mid_y - amplitude if not inverted else mid_y + amplitude
        path += f"C {x0:.2f} {mid_y:.2f} {x1 - bw * 0.1:.2f} {cy:.2f} {x1:.2f} {cy:.2f} "
        path += f"C {x1 + bw * 0.1:.2f} {cy:.2f} {x2:.2f} {mid_y:.2f} {x2:.2f} {mid_y:.2f} "

    if fill_bottom:
        path += f"L {width} {height} L 0 {height} Z"
    else:
        path += f"L {width} 0 L 0 0 Z"
    return path


def _build_animated_wave_values(
    builder,
    width: int,
    height: int,
    amplitude: float,
    frequency: float,
    fill_bottom: bool,
    base_phase: float,
    frame_count: int = 5,
    **kwargs,
) -> str:
    """Build semicolon-separated animated path values for a wave-like morph."""
    values = []
    for frame in range(frame_count):
        # full cycle split across N-1 steps; last frame equals first for seamless loop
        phase = base_phase + (2 * math.pi * frame / (frame_count - 1))
        values.append(
            builder(
                width,
                height,
                amplitude,
                frequency,
                phase=phase,
                fill_bottom=fill_bottom,
                y_offset=0.5,
                **kwargs,
            )
        )
    return ";".join(values)


def _build_animated_amplitude_values(
    builder,
    width: int,
    height: int,
    amplitude: float,
    frequency: float,
    fill_bottom: bool,
    y_offset: float = 0.5,
    frame_count: int = 5,
    **kwargs,
) -> str:
    """Build animated path values by pulsating amplitude (for non-phase wave types)."""
    values = []
    for frame in range(frame_count):
        phase = 2 * math.pi * frame / (frame_count - 1)
        amp = max(1.0, amplitude * (0.72 + 0.28 * (math.sin(phase) + 1) / 2))
        values.append(
            builder(
                width,
                height,
                amp,
                frequency,
                fill_bottom=fill_bottom,
                y_offset=y_offset,
                **kwargs,
            )
        )
    return ";".join(values)


def generate_wave_svg(
    wave_type: str = "sine",
    width: int = 1200,
    height: int = 80,
    color_top: str = "#0d1117",
    color_bottom: str = "#161b22",
    amplitude: float = 20.0,
    frequency: float = 1.0,
    layers: int = 1,
    flip: bool = False,
    gradient: bool = False,
    opacity: float = 1.0,
    mirror: bool = False,
    animate: bool = False,
    speed: float = 6.0,
    smooth: bool = True,
    text: str = "",
    text_bottom: str = "",
    text_color: str = "#ffffff",
    text_bottom_color: str = "#a5b4fc",
    text_size: int = 28,
    text_bottom_size: int = 22,
    text_style: str = "normal",
    text_stroke_color: str = "#000000",
    text_stroke_width: float = 0.0,
    text_scale_x: float = 100.0,
    text_scale_y: float = 100.0,
    text_x: float = 50.0,
    text_y: float = 45.0,
    text_gap: float = 26.0,
    text_align: str = "middle",
) -> str:
    """
    Generate an SVG wave divider.

    wave_type: sine | smooth | zigzag | bump | triangle
    """
    amplitude = min(max(amplitude, 1), height * 0.45)
    frequency = min(max(frequency, 0.5), 8.0)
    layers = min(max(layers, 1), 3)
    opacity = min(max(opacity, 0.1), 1.0)
    speed = min(max(speed, 1.0), 20.0)
    text_size = min(max(int(text_size), 8), 180)
    text_bottom_size = min(max(int(text_bottom_size), 8), 180)
    text_scale_x = min(max(float(text_scale_x), 50.0), 200.0)
    text_scale_y = min(max(float(text_scale_y), 50.0), 200.0)
    text_x = min(max(float(text_x), 0.0), 100.0)
    text_y = min(max(float(text_y), 0.0), 100.0)
    text_gap = min(max(float(text_gap), 0.0), 200.0)
    text_align = text_align if text_align in ("start", "middle", "end") else "middle"
    text_style = text_style if text_style in ("normal", "bold", "italic", "bold_italic") else "normal"
    text_stroke_width = min(max(float(text_stroke_width), 0.0), 20.0)
    text = text.strip()
    text_bottom = text_bottom.strip()

    r1, g1, b1 = _hex_to_rgb(color_top)
    r2, g2, b2 = _hex_to_rgb(color_bottom)

    defs = ""
    grad_id = "wg"
    if gradient:
        defs = f"""
  <defs>
    <linearGradient id="{grad_id}" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{_esc(color_top)}"/>
      <stop offset="100%" stop-color="{_esc(color_bottom)}"/>
    </linearGradient>
  </defs>"""
        fill_color = f"url(#{grad_id})"
    else:
        fill_color = _esc(color_bottom)

    paths_svg = ""

    for layer_idx in range(layers):
        frac = layer_idx / max(layers, 1)
        phase_offset = frac * math.pi * 0.8
        amp_scale = 1.0 - frac * 0.35
        layer_amp = amplitude * amp_scale
        layer_opacity = opacity * (1.0 - frac * 0.35) if layers > 1 else opacity

        # interpolated color for multi-layer
        if layers > 1 and not gradient:
            t = layer_idx / (layers - 1) if layers > 1 else 0
            lr = int(r2 + (r1 - r2) * (1 - t))
            lg = int(g2 + (g1 - g2) * (1 - t))
            lb = int(b2 + (b1 - b2) * (1 - t))
            layer_color = f"rgb({lr},{lg},{lb})"
        else:
            layer_color = fill_color

        fill_bottom_flag = not flip

        if wave_type == "sine":
            path_d = _build_wave_path(
                width, height, layer_amp, frequency,
                phase=phase_offset,
                fill_bottom=fill_bottom_flag,
                y_offset=0.5,
                inverted=flip,
            )
        elif wave_type == "smooth":
            path_d = _build_smooth_wave_path(
                width, height, layer_amp, frequency,
                phase=phase_offset,
                fill_bottom=fill_bottom_flag,
                y_offset=0.5,
                inverted=flip,
            )
        elif wave_type == "zigzag":
            path_d = _build_zigzag_path(
                width, height, layer_amp, frequency,
                fill_bottom=fill_bottom_flag,
                y_offset=0.5,
                inverted=flip,
            )
        elif wave_type == "bump":
            path_d = _build_bump_path(
                width, height, layer_amp, frequency,
                fill_bottom=fill_bottom_flag,
                y_offset=0.5,
                inverted=flip,
            )
        elif wave_type == "triangle":
            path_d = _build_zigzag_path(
                width, height, layer_amp, frequency * 0.7,
                fill_bottom=fill_bottom_flag,
                y_offset=0.5,
            )
        else:
            path_d = _build_smooth_wave_path(
                width, height, layer_amp, frequency,
                phase=phase_offset,
                fill_bottom=fill_bottom_flag,
                y_offset=0.5,
            )

        animation_svg = ""
        if animate:
            layer_duration = speed + layer_idx * 1.1
            if wave_type in ("sine", "smooth"):
                builder = _build_wave_path if wave_type == "sine" else _build_smooth_wave_path
                anim_values = _build_animated_wave_values(
                    builder,
                    width,
                    height,
                    layer_amp,
                    frequency,
                    fill_bottom_flag,
                    phase_offset,
                    inverted=flip,
                )
                animation_svg = (
                    f'<animate attributeName="d" values="{anim_values}" '
                    f'dur="{layer_duration:.2f}s" repeatCount="indefinite"/>'
                )
            elif wave_type == "zigzag":
                anim_values = _build_animated_amplitude_values(
                    _build_zigzag_path,
                    width,
                    height,
                    layer_amp,
                    frequency,
                    fill_bottom_flag,
                    inverted=flip,
                )
                animation_svg = (
                    f'<animate attributeName="d" values="{anim_values}" '
                    f'dur="{layer_duration:.2f}s" repeatCount="indefinite"/>'
                )
            elif wave_type in ("bump", "triangle"):
                bump_builder = _build_bump_path if wave_type == "bump" else _build_zigzag_path
                bump_freq = frequency if wave_type == "bump" else frequency * 0.7
                bump_kwargs = {"inverted": flip} if wave_type == "bump" else {}
                anim_values = _build_animated_amplitude_values(
                    bump_builder,
                    width,
                    height,
                    layer_amp,
                    bump_freq,
                    fill_bottom_flag,
                    **bump_kwargs,
                )
                animation_svg = (
                    f'<animate attributeName="d" values="{anim_values}" '
                    f'dur="{layer_duration:.2f}s" repeatCount="indefinite"/>'
                )
            else:
                layer_shift = width * (0.02 + layer_idx * 0.01)
                animation_svg = (
                    f'<animateTransform attributeName="transform" type="translate" '
                    f'values="0 0; {-layer_shift:.2f} 0; 0 0" dur="{layer_duration:.2f}s" '
                    f'repeatCount="indefinite"/>'
                )

        paths_svg += (
            f'  <path d="{path_d}" fill="{layer_color}" fill-opacity="{layer_opacity:.2f}">'
            f'{animation_svg}</path>\n'
        )

    # Mirror layer
    if mirror:
        if wave_type in ("sine",):
            mirror_path = _build_wave_path(
                width, height, amplitude, frequency,
                phase=math.pi,
                fill_bottom=not flip,
                y_offset=0.5,
                inverted=flip,
            )
        else:
            mirror_path = _build_smooth_wave_path(
                width, height, amplitude, frequency,
                phase=math.pi,
                fill_bottom=not flip,
                y_offset=0.5,
                inverted=flip,
            )
        mirror_anim = ""
        if animate:
            if wave_type in ("sine", "smooth"):
                builder = _build_wave_path if wave_type == "sine" else _build_smooth_wave_path
                mirror_values = _build_animated_wave_values(
                    builder,
                    width,
                    height,
                    amplitude,
                    frequency,
                    not flip,
                    math.pi,
                    inverted=flip,
                )
                mirror_anim = (
                    f'<animate attributeName="d" values="{mirror_values}" '
                    f'dur="{speed + 1.5:.2f}s" repeatCount="indefinite"/>'
                )
            elif wave_type == "zigzag":
                mirror_values = _build_animated_amplitude_values(
                    _build_zigzag_path,
                    width,
                    height,
                    amplitude,
                    frequency,
                    not flip,
                    inverted=flip,
                )
                mirror_anim = (
                    f'<animate attributeName="d" values="{mirror_values}" '
                    f'dur="{speed + 1.5:.2f}s" repeatCount="indefinite"/>'
                )
            elif wave_type in ("bump", "triangle"):
                mirror_builder = _build_bump_path if wave_type == "bump" else _build_zigzag_path
                mirror_freq = frequency if wave_type == "bump" else frequency * 0.7
                mirror_kwargs = {"inverted": flip} if wave_type == "bump" else {}
                mirror_values = _build_animated_amplitude_values(
                    mirror_builder,
                    width,
                    height,
                    amplitude,
                    mirror_freq,
                    not flip,
                    **mirror_kwargs,
                )
                mirror_anim = (
                    f'<animate attributeName="d" values="{mirror_values}" '
                    f'dur="{speed + 1.5:.2f}s" repeatCount="indefinite"/>'
                )
            else:
                mirror_anim = (
                    f'<animateTransform attributeName="transform" type="translate" '
                    f'values="0 0; {width * 0.03:.2f} 0; 0 0" dur="{speed + 1.5:.2f}s" '
                    f'repeatCount="indefinite"/>'
                )
        paths_svg += (
            f'  <path d="{mirror_path}" fill="{fill_color}" fill-opacity="{opacity * 0.4:.2f}">'
            f'{mirror_anim}</path>\n'
        )

    text_svg = ""
    if text or text_bottom:
        font_weight = "700" if text_style in ("bold", "bold_italic") else "400"
        font_style = "italic" if text_style in ("italic", "bold_italic") else "normal"
        text_pos_x = width * text_x / 100
        text_pos_y = height * text_y / 100
        text_bottom_pos_y = text_pos_y + text_gap
        scale_x = text_scale_x / 100
        scale_y = text_scale_y / 100
        if text:
            text_svg += (
                f'  <text x="0" y="0" transform="translate({text_pos_x:.2f} {text_pos_y:.2f}) scale({scale_x:.2f} {scale_y:.2f})" '
                f'fill="{_esc(text_color)}" font-size="{text_size}" text-anchor="{text_align}" '
                f'font-weight="{font_weight}" font-style="{font_style}" '
                f'font-family="Inter,Segoe UI,Roboto,Arial,sans-serif" dominant-baseline="middle" '
                f'stroke="{_esc(text_stroke_color)}" stroke-width="{text_stroke_width:.2f}" '
                f'paint-order="stroke fill">'
                f'{_esc(text)}</text>\n'
            )
        if text_bottom:
            text_svg += (
                f'  <text x="0" y="0" transform="translate({text_pos_x:.2f} {text_bottom_pos_y:.2f}) scale({scale_x:.2f} {scale_y:.2f})" '
                f'fill="{_esc(text_bottom_color)}" font-size="{text_bottom_size}" text-anchor="{text_align}" '
                f'font-weight="{font_weight}" font-style="{font_style}" '
                f'font-family="Inter,Segoe UI,Roboto,Arial,sans-serif" dominant-baseline="middle" '
                f'stroke="{_esc(text_stroke_color)}" stroke-width="{text_stroke_width:.2f}" '
                f'paint-order="stroke fill">'
                f'{_esc(text_bottom)}</text>\n'
            )

    return f"""<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 {width} {height}" width="{width}" height="{height}"
     preserveAspectRatio="none"
     role="img" aria-label="Wave divider">
{defs}
  <g>
{paths_svg}  </g>
{text_svg}
</svg>"""
