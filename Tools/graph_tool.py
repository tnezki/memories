# =============================================================================
# graph_tool.py - CANONICAL DISTRICT GRAPH TOOL
# =============================================================================
#
# STATUS: AUTHORITATIVE
# VERSION: district-graph-tool/1.0-unified
# DATE: 2026-09-20
#
# This file consolidates the formerly layered v12 -> v13 -> v14 graph tools.
# It is intentionally self-contained: no older graph-tool source file is needed
# at runtime. All district/course tools should resolve this file through
# Tools/MANIFEST.json rather than pinning a versioned graph-tool copy.
#
# Teacher-approved full-size Cartesian print weights:
#   grid:             0.6 pt  #aaaaaa
#   axes/arrows:      1.8 pt  #222222
#   plotted relation: 2.0 pt
#   major ticks:      1.2 pt
#   curve exit arrow: 1.5 pt
#
# Compact multi-panel graphs retain proportionally lighter styling.
# Do not override graph styling in generation blocks.
# =============================================================================

from fractions import Fraction
import os

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Canonical full-size Cartesian styling.
GRID_COLOR = "#aaaaaa"
AXIS_COLOR = "#222222"
GRID_WIDTH = 0.6
AXIS_WIDTH = 1.8
CURVE_WIDTH = 2.0
MAJOR_TICK_WIDTH = 1.2
MINOR_TICK_WIDTH = 0.8
CURVE_ARROW_WIDTH = 1.5
STANDARD_MIN = -10
STANDARD_MAX = 10
STANDARD_VIEW_PAD = 0.8
STANDARD_ARROW_LENGTH = 0.45

# Compact multi-panel styling inherited from the v13 layer.
COMPACT_GRID_WIDTH = 0.4
COMPACT_AXIS_WIDTH = 1.1
COMPACT_CURVE_WIDTH = 1.2
COMPACT_ARROW_WIDTH = 1.0


# -----------------------------------------------------------------------------
# Shared utilities
# -----------------------------------------------------------------------------

def _nice_grid_step(data_range, max_lines=20):
    raw = data_range / max_lines
    mag = 10 ** np.floor(np.log10(max(raw, 1e-9)))
    for nice in [1, 2, 2.5, 5, 10]:
        step = nice * mag
        if data_range / step <= max_lines:
            return step
    return mag * 10


def _label_every(n_lines):
    if n_lines <= 10:
        return 2
    if n_lines <= 15:
        return 3
    return 5


def _fmt(v):
    return str(int(v)) if v == int(v) else f"{v:g}"


def _find_key_points(functions, xmin, xmax, ymin, ymax):
    key_points = []
    x_check = np.linspace(xmin, xmax, 2000)
    if len(functions) >= 2:
        for i in range(len(functions)):
            for j in range(i + 1, len(functions)):
                try:
                    diff = functions[i]["expr"](x_check) - functions[j]["expr"](x_check)
                    for idx in np.where(np.diff(np.sign(diff)))[0]:
                        xr = np.interp(0, [diff[idx], diff[idx + 1]], [x_check[idx], x_check[idx + 1]])
                        yr = functions[i]["expr"](np.array([xr]))[0]
                        if ymin <= yr <= ymax:
                            key_points.append((xr, yr))
                except Exception:
                    pass
    for fn in functions:
        try:
            dy = fn["deriv"](x_check)
            for idx in np.where(np.diff(np.sign(dy)))[0]:
                xv = np.interp(0, [dy[idx], dy[idx + 1]], [x_check[idx], x_check[idx + 1]])
                yv = fn["expr"](np.array([xv]))[0]
                if ymin <= yv <= ymax:
                    key_points.append((xv, yv))
        except Exception:
            pass
    return key_points


def _score_corner(cx, cy, functions, key_points):
    score = 0
    for fn in functions:
        try:
            fy = fn["expr"](np.array([cx]))[0]
            score += abs(fy - cy) if np.isfinite(fy) else 20
        except Exception:
            score += 20
    for kx, ky in key_points:
        dist = np.sqrt((cx - kx) ** 2 + (cy - ky) ** 2)
        if dist < 3:
            score -= (3 - dist) * 50
    return score


def _draw_legend(ax, functions, key_points, xmin, xmax, ymin, ymax):
    if len(functions) <= 1:
        return
    handles = [
        mpatches.Patch(color=fn["color"], label=fn["label"])
        for fn in functions
        if fn.get("label")
    ]
    if not handles:
        return
    span_x = xmax - xmin
    span_y = ymax - ymin
    corners = {
        "upper right": (xmin + span_x * 0.7, ymin + span_y * 0.8),
        "upper left": (xmin + span_x * 0.2, ymin + span_y * 0.8),
        "lower right": (xmin + span_x * 0.7, ymin + span_y * 0.15),
        "lower left": (xmin + span_x * 0.2, ymin + span_y * 0.15),
    }
    best = max(corners, key=lambda c: _score_corner(*corners[c], functions, key_points))
    ax.legend(
        handles=handles,
        prop={"family": "Times New Roman", "size": 11, "weight": "bold"},
        loc=best,
        framealpha=0.9,
        edgecolor=GRID_COLOR,
        handlelength=1.2,
        borderpad=0.5,
        labelspacing=0.3,
    )


def _safe_scalar(value):
    arr = np.asarray(value)
    if arr.ndim == 0:
        return float(arr)
    return float(arr.ravel()[0])


def _function_segments(fn, xmin, xmax, ymin, ymax, samples=2200):
    x = np.linspace(xmin, xmax, samples)
    y = fn(x)
    finite = np.isfinite(y)
    mask = finite & (y >= ymin) & (y <= ymax)
    inds = np.where(mask)[0]
    if not len(inds):
        return x, y, []
    segments = np.split(inds, np.where(np.diff(inds) > 5)[0] + 1)
    return x, y, [seg for seg in segments if len(seg) > 1]


def _curve_exit_arrows(ax, f, fprime, color, xmin, xmax, ymin, ymax, arrow_length=None, lw=CURVE_ARROW_WIDTH):
    """Draw relation arrows at every visible window exit, including horizontal exits."""
    if arrow_length is None:
        arrow_length = STANDARD_ARROW_LENGTH
    x = np.linspace(xmin, xmax, 2200)
    y = f(x)

    # Left/right edges. Unlike v12/v13, a zero endpoint slope still gets a
    # horizontal arrow so linear/constant-like exits are never silently lost.
    for x_edge, direction in ((xmin, -1.0), (xmax, 1.0)):
        try:
            y_edge = _safe_scalar(f(np.array([x_edge])))
            slope = _safe_scalar(fprime(x_edge))
        except Exception:
            continue
        if not np.isfinite(y_edge) or not (ymin <= y_edge <= ymax):
            continue
        dx_d = direction
        dy_d = slope * direction
        mag = float(np.hypot(dx_d, dy_d))
        if mag < 1e-9:
            dx_d, dy_d, mag = direction, 0.0, 1.0
        dx_d /= mag
        dy_d /= mag
        ax.annotate(
            "",
            xy=(x_edge + dx_d * arrow_length, y_edge + dy_d * arrow_length),
            xytext=(x_edge, y_edge),
            arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=12),
            annotation_clip=False,
        )

    # Top/bottom edges.
    for edge_y, direction in ((ymin, -1.0), (ymax, 1.0)):
        vals = y - edge_y
        good = np.isfinite(vals[:-1]) & np.isfinite(vals[1:])
        crossings = np.where(good & (np.sign(vals[:-1]) != np.sign(vals[1:])))[0]
        for idx in crossings:
            xr = float(np.interp(0, [vals[idx], vals[idx + 1]], [x[idx], x[idx + 1]]))
            if xr <= xmin + 1e-4 or xr >= xmax - 1e-4:
                continue
            try:
                slope = _safe_scalar(fprime(xr))
            except Exception:
                continue
            if abs(slope) < 1e-9:
                continue
            dy_d = direction
            dx_d = dy_d / slope
            mag = float(np.hypot(dx_d, dy_d))
            dx_d /= mag
            dy_d /= mag
            ax.annotate(
                "",
                xy=(xr + dx_d * arrow_length, edge_y + dy_d * arrow_length),
                xytext=(xr, edge_y),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=12),
                annotation_clip=False,
            )


def _draw_standard_axes(ax, xmin, xmax, ymin, ymax, *, labels=True, compact=False):
    axis_width = COMPACT_AXIS_WIDTH if compact else AXIS_WIDTH
    mutation = 8 if compact else 14
    ax.spines["left"].set_position("zero")
    ax.spines["bottom"].set_position("zero")
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    for name in ("left", "bottom"):
        ax.spines[name].set_linewidth(axis_width)
        ax.spines[name].set_color(AXIS_COLOR)
    ax.spines["left"].set_bounds(ymin - 0.5, ymax + 0.5)
    ax.spines["bottom"].set_bounds(xmin - 0.5, xmax + 0.5)
    tri = dict(arrowstyle="-|>", color=AXIS_COLOR, lw=axis_width, mutation_scale=mutation)
    ax.annotate("", xy=(xmax + 0.6, 0), xytext=(xmax, 0), arrowprops=tri, annotation_clip=False)
    ax.annotate("", xy=(xmin - 0.6, 0), xytext=(xmin, 0), arrowprops=tri, annotation_clip=False)
    ax.annotate("", xy=(0, ymax + 0.6), xytext=(0, ymax), arrowprops=tri, annotation_clip=False)
    ax.annotate("", xy=(0, ymin - 0.6), xytext=(0, ymin), arrowprops=tri, annotation_clip=False)
    if labels:
        fs = 10 if compact else 14
        ax.text(xmax + (0.2 if compact else 0.35), 0.9 if compact else 0.4, "x",
                fontsize=fs, fontweight="bold", fontfamily="Times New Roman", ha="center", va="bottom")
        ax.text(0.6 if compact else 0.35, ymax + (0.2 if compact else 0.35), "y",
                fontsize=fs, fontweight="bold", fontfamily="Times New Roman", ha="left", va="center")


def _style_standard_plane(ax, xmin=-10, xmax=10, ymin=-10, ymax=10, *, compact=False, show_labels=True):
    grid_width = COMPACT_GRID_WIDTH if compact else GRID_WIDTH
    major_width = 0.9 if compact else MAJOR_TICK_WIDTH
    minor_width = 0.4 if compact else MINOR_TICK_WIDTH
    ax.set_xlim(xmin - (0.5 if not compact else 0.5), xmax + (0.5 if not compact else 0.5))
    ax.set_ylim(ymin - (0.5 if not compact else 0.5), ymax + (0.5 if not compact else 0.5))
    ax.set_xticks(np.arange(xmin, xmax + 1, 1), minor=True)
    ax.set_yticks(np.arange(ymin, ymax + 1, 1), minor=True)
    ax.grid(True, which="minor", color=GRID_COLOR, linewidth=grid_width)
    ax.set_xticks([-10, -5, 5, 10])
    ax.set_yticks([-10, -5, 5, 10])
    if compact:
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        offset = 1.0
        for val in [-10, -5, 5, 10]:
            ax.text(val, -offset, str(val), ha="center", va="top", fontsize=8.5,
                    fontfamily="Times New Roman", color="black", clip_on=False)
            ax.text(-offset, val, str(val), ha="right", va="center", fontsize=8.5,
                    fontfamily="Times New Roman", color="black", clip_on=False)
    else:
        ax.set_xticklabels(["-10", "-5", "5", "10"], fontfamily="Times New Roman", fontsize=11)
        ax.set_yticklabels(["-10", "-5", "5", "10"], fontfamily="Times New Roman", fontsize=11)
    ax.grid(True, which="major", color=GRID_COLOR, linewidth=grid_width)
    ax.tick_params(which="major", length=3.5 if compact else 5, width=major_width, color=AXIS_COLOR)
    ax.tick_params(which="minor", length=1.0 if compact else 2, width=minor_width, color="#555555")
    _draw_standard_axes(ax, xmin, xmax, ymin, ymax, labels=show_labels, compact=compact)


# -----------------------------------------------------------------------------
# Full-size Cartesian graphs
# -----------------------------------------------------------------------------

def make_standard_graph(ax, functions, title=""):
    xmin = ymin = STANDARD_MIN
    xmax = ymax = STANDARD_MAX
    for fn in functions:
        x, y, segments = _function_segments(fn["expr"], xmin, xmax, ymin, ymax)
        label = fn.get("label")
        for seg in segments:
            ax.plot(x[seg], y[seg], color=fn["color"], linewidth=CURVE_WIDTH, label=label, zorder=3)
            label = None
        _curve_exit_arrows(ax, fn["expr"], fn["deriv"], fn["color"], xmin, xmax, ymin, ymax)
    key_points = _find_key_points(functions, xmin, xmax, ymin, ymax)
    _draw_legend(ax, functions, key_points, xmin, xmax, ymin, ymax)
    _style_standard_plane(ax, xmin, xmax, ymin, ymax, compact=False)
    # v14 viewport pad ensures relation/axis exit arrows are actually visible.
    ax.set_xlim(xmin - STANDARD_VIEW_PAD, xmax + STANDARD_VIEW_PAD)
    ax.set_ylim(ymin - STANDARD_VIEW_PAD, ymax + STANDARD_VIEW_PAD)
    ax.set_title(title, fontfamily="Times New Roman", fontsize=12, pad=8)
    return ax


def make_window_graph(ax, functions, xmin, xmax, ymin, ymax, title="", xlabel="x", ylabel="y"):
    """Canonical full-size Cartesian graph on any two-sided window.

    Passing an empty functions list intentionally creates an answer-neutral
    blank construction surface with the exact district graph styling.
    """
    x_range = xmax - xmin
    y_range = ymax - ymin
    x_step = _nice_grid_step(x_range, max_lines=16)
    y_step = _nice_grid_step(y_range, max_lines=16)
    x_ticks = np.arange(np.ceil(xmin / x_step) * x_step, xmax + x_step * 0.01, x_step)
    y_ticks = np.arange(np.ceil(ymin / y_step) * y_step, ymax + y_step * 0.01, y_step)
    x_pad = x_step * 0.55
    y_pad = y_step * 0.55
    ax.set_xlim(xmin - x_pad, xmax + x_pad)
    ax.set_ylim(ymin - y_pad, ymax + y_pad)

    for xt in x_ticks:
        ax.plot([xt, xt], [ymin, ymax], color=GRID_COLOR, linewidth=GRID_WIDTH, zorder=0)
    for yt in y_ticks:
        ax.plot([xmin, xmax], [yt, yt], color=GRID_COLOR, linewidth=GRID_WIDTH, zorder=0)

    arrow_length = min(x_step, y_step) * 0.45
    for fn in functions:
        x, y, segments = _function_segments(fn["expr"], xmin, xmax, ymin, ymax)
        label = fn.get("label")
        for seg in segments:
            ax.plot(x[seg], y[seg], color=fn["color"], linewidth=CURVE_WIDTH, label=label, zorder=3)
            label = None
        _curve_exit_arrows(ax, fn["expr"], fn["deriv"], fn["color"], xmin, xmax, ymin, ymax,
                           arrow_length=arrow_length)

    tri = dict(arrowstyle="-|>", color=AXIS_COLOR, lw=AXIS_WIDTH, mutation_scale=13)
    if ymin <= 0 <= ymax:
        ax.plot([xmin, xmax], [0, 0], color=AXIS_COLOR, linewidth=AXIS_WIDTH, zorder=2)
        ax.annotate("", xy=(xmax + x_pad * 0.8, 0), xytext=(xmax, 0), arrowprops=tri, annotation_clip=False)
        ax.annotate("", xy=(xmin - x_pad * 0.8, 0), xytext=(xmin, 0), arrowprops=tri, annotation_clip=False)
        ax.text(xmax + x_pad * 0.62, y_step * 0.22, xlabel, fontsize=12, fontweight="bold",
                fontfamily="Times New Roman", ha="center", va="bottom")
    if xmin <= 0 <= xmax:
        ax.plot([0, 0], [ymin, ymax], color=AXIS_COLOR, linewidth=AXIS_WIDTH, zorder=2)
        ax.annotate("", xy=(0, ymax + y_pad * 0.8), xytext=(0, ymax), arrowprops=tri, annotation_clip=False)
        ax.annotate("", xy=(0, ymin - y_pad * 0.8), xytext=(0, ymin), arrowprops=tri, annotation_clip=False)
        ax.text(x_step * 0.20, ymax + y_pad * 0.62, ylabel, fontsize=12, fontweight="bold",
                fontfamily="Times New Roman", ha="left", va="center")

    x_lab_every = _label_every(len(x_ticks))
    y_lab_every = _label_every(len(y_ticks))
    x_labeled = [t for i, t in enumerate(x_ticks) if i % x_lab_every == 0]
    y_labeled = [t for i, t in enumerate(y_ticks) if i % y_lab_every == 0]
    ax.set_xticks(x_labeled)
    ax.set_yticks(y_labeled)
    ax.set_xticklabels([_fmt(t) for t in x_labeled], fontfamily="Times New Roman", fontsize=9)
    ax.set_yticklabels([_fmt(t) for t in y_labeled], fontfamily="Times New Roman", fontsize=9)
    ax.tick_params(which="major", length=3, width=MAJOR_TICK_WIDTH, color="#444444")
    for spine in ax.spines.values():
        spine.set_visible(False)
    key_points = _find_key_points(functions, xmin, xmax, ymin, ymax)
    _draw_legend(ax, functions, key_points, xmin, xmax, ymin, ymax)
    ax.set_title(title, fontfamily="Times New Roman", fontsize=12, pad=8)
    return ax


def make_context_graph(ax, functions, xmin, xmax, ymin, ymax, xlabel="x", ylabel="y", title=""):
    x_range = xmax - xmin
    y_range = ymax - ymin
    x_step = _nice_grid_step(x_range)
    y_step = _nice_grid_step(y_range)
    x_ticks = np.arange(xmin, xmax + x_step * 0.01, x_step)
    y_ticks = np.arange(ymin, ymax + y_step * 0.01, y_step)
    if len(x_ticks) > 20:
        x_step = _nice_grid_step(x_range, max_lines=10)
        x_ticks = np.arange(xmin, xmax + x_step * 0.01, x_step)
    if len(y_ticks) > 20:
        y_step = _nice_grid_step(y_range, max_lines=10)
        y_ticks = np.arange(ymin, ymax + y_step * 0.01, y_step)

    x_stub = x_step * 0.35
    y_stub = y_step * 0.35
    x_arrow_pad = x_step * 0.25
    y_arrow_pad = y_step * 0.25
    ax.set_xlim(xmin, xmax + x_stub)
    ax.set_ylim(ymin, ymax + y_stub)
    for xt in x_ticks:
        ax.plot([xt, xt], [ymin, ymax], color=GRID_COLOR, linewidth=GRID_WIDTH, zorder=0, clip_on=True)
    for yt in y_ticks:
        ax.plot([xmin, xmax], [yt, yt], color=GRID_COLOR, linewidth=GRID_WIDTH, zorder=0, clip_on=True)

    arrow_length = min(x_step, y_step) * 0.45
    for fn in functions:
        x, y, segments = _function_segments(fn["expr"], xmin, xmax, ymin, ymax)
        label = fn.get("label")
        for seg in segments:
            ax.plot(x[seg], y[seg], color=fn["color"], linewidth=CURVE_WIDTH, label=label, zorder=3)
            label = None
        _curve_exit_arrows(ax, fn["expr"], fn["deriv"], fn["color"], xmin, xmax, ymin, ymax,
                           arrow_length=arrow_length)

    key_points = _find_key_points(functions, xmin, xmax, ymin, ymax)
    _draw_legend(ax, functions, key_points, xmin, xmax, ymin, ymax)
    x_every = _label_every(len(x_ticks))
    y_every = _label_every(len(y_ticks))
    x_labeled = [t for i, t in enumerate(x_ticks) if i % x_every == 0]
    y_labeled = [t for i, t in enumerate(y_ticks) if i % y_every == 0]
    ax.set_xticks(x_labeled)
    ax.set_yticks(y_labeled)
    ax.set_xticklabels([_fmt(t) for t in x_labeled], fontfamily="Times New Roman", fontsize=11)
    ax.set_yticklabels([_fmt(t) for t in y_labeled], fontfamily="Times New Roman", fontsize=11)
    ax.tick_params(which="major", length=4, width=MAJOR_TICK_WIDTH, color="#444444")
    ax.spines["left"].set_linewidth(AXIS_WIDTH)
    ax.spines["left"].set_color(AXIS_COLOR)
    ax.spines["bottom"].set_linewidth(AXIS_WIDTH)
    ax.spines["bottom"].set_color(AXIS_COLOR)
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    tri = dict(arrowstyle="-|>", color=AXIS_COLOR, lw=AXIS_WIDTH, mutation_scale=14)
    ax.annotate("", xy=(xmax + x_stub + x_arrow_pad, ymin), xytext=(xmax, ymin), arrowprops=tri, annotation_clip=False)
    ax.annotate("", xy=(xmin, ymax + y_stub + y_arrow_pad), xytext=(xmin, ymax), arrowprops=tri, annotation_clip=False)
    ax.set_xlabel(xlabel, fontfamily="Times New Roman", fontsize=13, fontweight="bold", labelpad=6)
    ax.set_ylabel(ylabel, fontfamily="Times New Roman", fontsize=13, fontweight="bold", labelpad=6, rotation=90)
    ax.set_title(title, fontfamily="Times New Roman", fontsize=12, pad=8)
    return ax


# -----------------------------------------------------------------------------
# Number lines
# -----------------------------------------------------------------------------

def _draw_number_line_base(ax, xmin, xmax):
    x_range = xmax - xmin
    margin = x_range * 0.07
    ticks = np.arange(xmin, xmax + 0.5)
    line_y = 0.0
    tick_h = 0.12
    right_tip = xmax + margin * 0.95
    left_tip = xmin - margin * 0.95
    props = dict(arrowstyle="->", color="black", lw=1.8, mutation_scale=14, shrinkA=0, shrinkB=0)
    ax.annotate("", xy=(right_tip, line_y), xytext=(left_tip, line_y), arrowprops=props)
    ax.annotate("", xy=(left_tip, line_y), xytext=(right_tip, line_y), arrowprops=props)
    for t in ticks:
        ax.plot([t, t], [line_y - tick_h, line_y + tick_h], color="black", linewidth=1.2, zorder=3)
    for t in ticks:
        tv = int(round(t))
        if tv == 0 or tv % 2 == 0:
            ax.text(t, line_y - tick_h - 0.10, str(tv), ha="center", va="top",
                    fontfamily="Times New Roman", fontsize=11, color="black")
    return margin, right_tip, left_tip


def _nl_dot(ax, x, y, open_dot, color, size=8):
    if open_dot:
        ax.plot(x, y, "o", markersize=size, markerfacecolor="white", markeredgecolor=color,
                markeredgewidth=2.5, zorder=6, clip_on=False)
    else:
        ax.plot(x, y, "o", markersize=size, markerfacecolor=color, markeredgecolor=color,
                markeredgewidth=2, zorder=6, clip_on=False)


def make_number_line(ax, intervals, xmin=-10, xmax=10):
    x_range = xmax - xmin
    line_y = 0.0
    seg_y = 0.55
    ax.set_xlim(xmin - x_range * 0.07, xmax + x_range * 0.07)
    ax.set_ylim(-0.5, 0.9)
    ax.set_aspect("auto")
    ax.axis("off")
    ax.set_facecolor("white")
    _, right_tip, left_tip = _draw_number_line_base(ax, xmin, xmax)
    for iv in intervals:
        color = iv.get("color", "steelblue")
        start = iv["start"]
        end = iv["end"]
        direction = iv.get("direction")
        _nl_dot(ax, start, line_y, iv.get("start_open", False), color)
        if direction == "right":
            ax.plot([start, start], [line_y + 0.06, seg_y], color=color, linewidth=1.8, zorder=2)
            ax.annotate("", xy=(right_tip * 0.98, seg_y), xytext=(start, seg_y),
                        arrowprops=dict(arrowstyle="->", color=color, lw=1.8, mutation_scale=14, shrinkA=0, shrinkB=0))
        elif direction == "left":
            ax.plot([start, start], [line_y + 0.06, seg_y], color=color, linewidth=1.8, zorder=2)
            ax.annotate("", xy=(left_tip * 0.98, seg_y), xytext=(start, seg_y),
                        arrowprops=dict(arrowstyle="->", color=color, lw=1.8, mutation_scale=14, shrinkA=0, shrinkB=0))
        else:
            _nl_dot(ax, end, line_y, iv.get("end_open", False), color)
            ax.plot([start, start], [line_y + 0.06, seg_y], color=color, linewidth=1.8, zorder=2)
            ax.plot([end, end], [line_y + 0.06, seg_y], color=color, linewidth=1.8, zorder=2)
            ax.plot([start, end], [seg_y, seg_y], color=color, linewidth=1.8, zorder=2)
    return ax


def make_number_line_blank(ax, label=None, xmin=-10, xmax=10):
    x_range = xmax - xmin
    ax.set_xlim(xmin - x_range * 0.07, xmax + x_range * 0.07)
    ax.set_ylim(-0.5, 2.5)
    ax.set_aspect("auto")
    ax.axis("off")
    ax.set_facecolor("white")
    _draw_number_line_base(ax, xmin, xmax)
    if label:
        ax.text(0, 2.2, label, ha="center", va="top", fontfamily="Times New Roman", fontsize=12, color="black")
    return ax


def save_graph(fig, filename):
    path = os.path.join(OUTPUT_DIR, filename)
    fig.savefig(path, dpi=144, bbox_inches="tight")
    print(f"Saved: {path}")
    return path


# -----------------------------------------------------------------------------
# Compact Cartesian grids
# -----------------------------------------------------------------------------

def _make_compact_grid(functions_list, titles, rows, cols, figsize):
    fig, axes = plt.subplots(rows, cols, figsize=figsize)
    axes_flat = np.atleast_1d(axes).flatten()
    fig.subplots_adjust(hspace=0.35 if rows > 1 else 0.2, wspace=0.30 if cols < 4 else 0.35)
    for ax, functions, title in zip(axes_flat, functions_list, titles):
        for fn in functions:
            x, y, segments = _function_segments(fn["expr"], -10, 10, -10, 10)
            label = fn.get("label")
            for seg in segments:
                ax.plot(x[seg], y[seg], color=fn["color"], linewidth=COMPACT_CURVE_WIDTH, label=label)
                label = None
            _curve_exit_arrows(ax, fn["expr"], fn["deriv"], fn["color"], -10, 10, -10, 10,
                               arrow_length=0.45, lw=COMPACT_ARROW_WIDTH)
        _style_standard_plane(ax, compact=True)
        if title:
            ax.set_title(title, fontsize=11, pad=4)
    return fig


def make_2x2_grid(functions_list, titles=None):
    return _make_compact_grid(functions_list, titles or ["", "", "", ""], 2, 2, (3.5, 3.5))


def make_2x1_grid(functions_list, titles=None):
    return _make_compact_grid(functions_list, titles or ["", ""], 1, 2, (7.0, 3.5))


def make_3x1_grid(functions_list, titles=None):
    return _make_compact_grid(functions_list, titles or ["", "", ""], 1, 3, (6.25, 2.08))


def make_4x1_grid(functions_list, titles=None):
    return _make_compact_grid(functions_list, titles or ["", "", "", ""], 1, 4, (6.25, 1.56))


# -----------------------------------------------------------------------------
# Instructional diagrams/models
# -----------------------------------------------------------------------------

def make_rectangle_model(row_labels, col_labels, cell_values, filename="rectangle_model.png"):
    n_rows = len(row_labels)
    n_cols = len(col_labels)
    cell_w, cell_h, margin = 0.75, 0.50, 0.40
    fig_w = margin + n_cols * cell_w + margin
    fig_h = margin + n_rows * cell_h + margin
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.set_xlim(0, fig_w)
    ax.set_ylim(0, fig_h)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    grid_x, grid_y = margin, margin * 0.5
    for r in range(n_rows):
        for c in range(n_cols):
            left = grid_x + c * cell_w
            bottom = grid_y + (n_rows - 1 - r) * cell_h
            ax.add_patch(mpatches.Rectangle((left, bottom), cell_w, cell_h, linewidth=1.2,
                                             edgecolor="black", facecolor="white"))
            val = cell_values[r][c]
            if val:
                ax.text(left + cell_w / 2, bottom + cell_h / 2, val, ha="center", va="center",
                        fontsize=13, fontfamily="Times New Roman")
    for c, lbl in enumerate(col_labels):
        ax.text(grid_x + c * cell_w + cell_w / 2, grid_y + n_rows * cell_h + 0.10, lbl,
                ha="center", va="bottom", fontsize=13, fontfamily="Times New Roman")
    for r, lbl in enumerate(row_labels):
        ax.text(grid_x - 0.10, grid_y + (n_rows - 1 - r) * cell_h + cell_h / 2, lbl,
                ha="right", va="center", fontsize=13, fontfamily="Times New Roman")
    return save_graph(fig, filename)


def make_diamond(top, left, right, bottom, filename="diamond.png"):
    fig, ax = plt.subplots(figsize=(2.5, 2.5))
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor("white")
    r = 0.85
    top_pt, right_pt, bottom_pt, left_pt = (0, r), (r, 0), (0, -r), (-r, 0)
    ax.add_patch(plt.Polygon([top_pt, right_pt, bottom_pt, left_pt], closed=True, linewidth=1.4,
                             edgecolor="black", facecolor="white", zorder=2))
    ax.plot([-r / 2, r / 2], [r / 2, -r / 2], color="black", linewidth=1.0, zorder=3)
    ax.plot([r / 2, -r / 2], [r / 2, -r / 2], color="black", linewidth=1.0, zorder=3)
    positions = {"top": (0, 0.38), "bottom": (0, -0.38), "left": (-0.38, 0), "right": (0.38, 0)}
    for cell, val in (("top", top), ("bottom", bottom), ("left", left), ("right", right)):
        if val:
            ax.text(*positions[cell], val, ha="center", va="center", fontsize=16,
                    fontfamily="Times New Roman", zorder=4)
    return save_graph(fig, filename)


# -----------------------------------------------------------------------------
# Piecewise and unit-circle graphs
# -----------------------------------------------------------------------------

def _pw_dot(ax, x, y, open_dot, color, size=7, dot_scale=0.65):
    size *= dot_scale
    if open_dot:
        ax.plot(x, y, "o", markersize=size, markerfacecolor="white", markeredgecolor=color,
                markeredgewidth=2, zorder=6, clip_on=False)
    else:
        ax.plot(x, y, "o", markersize=size, markerfacecolor=color, markeredgecolor=color,
                markeredgewidth=2, zorder=6, clip_on=False)


def make_piecewise_graph(ax, pieces, title="", dot_scale=0.65):
    for piece in pieces:
        f = piece["expr"]
        fprime = piece["deriv"]
        color = "steelblue"
        a, b = piece["domain"]
        x_seg = np.linspace(a, b, 1000)
        y_seg = f(x_seg)
        mask = np.isfinite(y_seg) & (y_seg >= -10) & (y_seg <= 10)
        if mask.any():
            ax.plot(x_seg[mask], y_seg[mask], color=color, linewidth=1.7, zorder=3)
        ya, yb = _safe_scalar(f(a)), _safe_scalar(f(b))
        if not piece.get("arrow_left", False) and -10 <= ya <= 10:
            _pw_dot(ax, a, ya, not piece.get("include_left", True), color, dot_scale=dot_scale)
        if not piece.get("arrow_right", False) and -10 <= yb <= 10:
            _pw_dot(ax, b, yb, not piece.get("include_right", True), color, dot_scale=dot_scale)
        for endpoint, direction, enabled in ((a, -1.0, piece.get("arrow_left", False)),
                                             (b, 1.0, piece.get("arrow_right", False))):
            if not enabled:
                continue
            try:
                y_end = _safe_scalar(f(endpoint))
                slope = _safe_scalar(fprime(endpoint))
            except Exception:
                continue
            if not (-10 <= y_end <= 10):
                continue
            dx_d, dy_d = direction, slope * direction
            mag = float(np.hypot(dx_d, dy_d))
            if mag < 1e-9:
                dx_d, dy_d, mag = direction, 0.0, 1.0
            dx_d /= mag; dy_d /= mag
            ax.annotate("", xy=(endpoint + dx_d * 0.45, y_end + dy_d * 0.45),
                        xytext=(endpoint, y_end),
                        arrowprops=dict(arrowstyle="-|>", color=color, lw=CURVE_ARROW_WIDTH, mutation_scale=12),
                        annotation_clip=False)

        # Preserve exit arrows when a piece leaves through the top/bottom of the
        # standard window inside its declared domain.
        for edge_y, direction in ((-10, -1.0), (10, 1.0)):
            vals = y_seg - edge_y
            good = np.isfinite(vals[:-1]) & np.isfinite(vals[1:])
            for idx in np.where(good & (np.sign(vals[:-1]) != np.sign(vals[1:])))[0]:
                xr = float(np.interp(0, [vals[idx], vals[idx + 1]], [x_seg[idx], x_seg[idx + 1]]))
                try:
                    slope = _safe_scalar(fprime(xr))
                except Exception:
                    continue
                if abs(slope) < 1e-9:
                    continue
                dy_d = direction; dx_d = dy_d / slope
                mag = float(np.hypot(dx_d, dy_d)); dx_d /= mag; dy_d /= mag
                ax.annotate("", xy=(xr + dx_d * 0.45, edge_y + dy_d * 0.45),
                            xytext=(xr, edge_y),
                            arrowprops=dict(arrowstyle="-|>", color=color, lw=CURVE_ARROW_WIDTH, mutation_scale=12),
                            annotation_clip=False)
    _style_standard_plane(ax, compact=False)
    ax.set_xlim(-10 - STANDARD_VIEW_PAD, 10 + STANDARD_VIEW_PAD)
    ax.set_ylim(-10 - STANDARD_VIEW_PAD, 10 + STANDARD_VIEW_PAD)
    ax.set_title(title, fontfamily="Times New Roman", fontsize=12, pad=8)
    return ax


ANGLE_DATA = {
    0: (1, 0), 30: (np.sqrt(3) / 2, 0.5), 45: (np.sqrt(2) / 2, np.sqrt(2) / 2),
    60: (0.5, np.sqrt(3) / 2), 90: (0, 1), 120: (-0.5, np.sqrt(3) / 2),
    135: (-np.sqrt(2) / 2, np.sqrt(2) / 2), 150: (-np.sqrt(3) / 2, 0.5),
    180: (-1, 0), 210: (-np.sqrt(3) / 2, -0.5), 225: (-np.sqrt(2) / 2, -np.sqrt(2) / 2),
    240: (-0.5, -np.sqrt(3) / 2), 270: (0, -1), 300: (0.5, -np.sqrt(3) / 2),
    315: (np.sqrt(2) / 2, -np.sqrt(2) / 2), 330: (np.sqrt(3) / 2, -0.5),
}
COORD_LABELS = {
    0: r"$(1, 0)$", 30: r"$\left(\frac{\sqrt{3}}{2}, \frac{1}{2}\right)$",
    45: r"$\left(\frac{\sqrt{2}}{2}, \frac{\sqrt{2}}{2}\right)$",
    60: r"$\left(\frac{1}{2}, \frac{\sqrt{3}}{2}\right)$", 90: r"$(0, 1)$",
    120: r"$\left(-\frac{1}{2}, \frac{\sqrt{3}}{2}\right)$",
    135: r"$\left(-\frac{\sqrt{2}}{2}, \frac{\sqrt{2}}{2}\right)$",
    150: r"$\left(-\frac{\sqrt{3}}{2}, \frac{1}{2}\right)$", 180: r"$(-1, 0)$",
    210: r"$\left(-\frac{\sqrt{3}}{2}, -\frac{1}{2}\right)$",
    225: r"$\left(-\frac{\sqrt{2}}{2}, -\frac{\sqrt{2}}{2}\right)$",
    240: r"$\left(-\frac{1}{2}, -\frac{\sqrt{3}}{2}\right)$", 270: r"$(0, -1)$",
    300: r"$\left(\frac{1}{2}, -\frac{\sqrt{3}}{2}\right)$",
    315: r"$\left(\frac{\sqrt{2}}{2}, -\frac{\sqrt{2}}{2}\right)$",
    330: r"$\left(\frac{\sqrt{3}}{2}, -\frac{1}{2}\right)$",
}


def _draw_unit_circle_base(ax, show_angle_lines=False):
    theta = np.linspace(0, 2 * np.pi, 1000)
    ax.plot(np.cos(theta), np.sin(theta), color="black", linewidth=2.0, zorder=3)
    ax.plot([-1.3, 1.3], [0, 0], color=AXIS_COLOR, linewidth=0.6, zorder=1)
    ax.plot([0, 0], [-1.3, 1.3], color=AXIS_COLOR, linewidth=0.6, zorder=1)
    tri = dict(arrowstyle="-|>", color=AXIS_COLOR, lw=0.6, mutation_scale=10)
    for xy, xytext in [((1.38, 0), (1.22, 0)), ((-1.38, 0), (-1.22, 0)),
                       ((0, 1.38), (0, 1.22)), ((0, -1.38), (0, -1.22))]:
        ax.annotate("", xy=xy, xytext=xytext, arrowprops=tri)
    ax.text(1.44, 0, "x", ha="left", va="center", fontsize=8, fontfamily="Times New Roman", color=AXIS_COLOR)
    ax.text(0, 1.44, "y", ha="center", va="bottom", fontsize=8, fontfamily="Times New Roman", color=AXIS_COLOR)
    if show_angle_lines:
        for deg in ANGLE_DATA:
            rad = np.radians(deg)
            ax.plot([0, np.cos(rad)], [0, np.sin(rad)], color=GRID_COLOR, linewidth=0.6, zorder=2)
    ax.set_xlim(-1.6, 1.6)
    ax.set_ylim(-1.6, 1.6)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_facecolor("white")


def _uc_save(fig, filename):
    path = os.path.join(OUTPUT_DIR, filename)
    fig.savefig(path, dpi=144)
    print(f"Saved: {path}")
    return path


def make_unit_circle_blank(filename="unit_circle_blank.png"):
    fig, ax = plt.subplots(figsize=(2.5, 2.5))
    fig.patch.set_facecolor("white")
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    _draw_unit_circle_base(ax, show_angle_lines=False)
    return _uc_save(fig, filename)


def make_unit_circle_angles(ax_angle_deg=None, show_coord=True, filename="unit_circle_angles.png"):
    fig, ax = plt.subplots(figsize=(2.5, 2.5))
    fig.patch.set_facecolor("white")
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    _draw_unit_circle_base(ax, show_angle_lines=True)
    if ax_angle_deg is not None:
        blue = "#1a4f8a"
        rad = np.radians(ax_angle_deg)
        px, py = np.cos(rad), np.sin(rad)
        ax.plot([0, px], [0, py], color=blue, linewidth=1.8, zorder=4)
        ax.plot(px, py, "o", markersize=5, color=blue, zorder=5)
        if show_coord and ax_angle_deg in COORD_LABELS:
            lx, ly = px * 1.12, py * 1.12
            ha = "left" if px > 0.15 else "right" if px < -0.15 else "center"
            va = "bottom" if py > 0.15 else "top" if py < -0.15 else "center"
            ax.text(lx, ly, COORD_LABELS[ax_angle_deg], ha=ha, va=va, fontsize=12,
                    color=blue, fontfamily="Times New Roman", zorder=6)
    return _uc_save(fig, filename)


# -----------------------------------------------------------------------------
# Inequalities, trig, and statistics
# -----------------------------------------------------------------------------

def make_inequality_graph(ax, inequalities, title=""):
    xmin, xmax, ymin, ymax = -11, 11, -11, 11
    x = np.linspace(xmin, xmax, 2000)
    regions = []
    for ineq in inequalities:
        f, fprime = ineq["expr"], ineq["deriv"]
        color = ineq["color"]
        y = f(x)
        y_clip = np.clip(y, ymin, ymax)
        regions.append({"y": y_clip, "shade": ineq["shade"], "color": color})
        line_style = "-" if ineq.get("inclusive", True) else "--"
        mask = np.isfinite(y) & (y >= ymin) & (y <= ymax)
        inds = np.where(mask)[0]
        if len(inds):
            for seg in np.split(inds, np.where(np.diff(inds) > 5)[0] + 1):
                if len(seg) > 1:
                    ax.plot(x[seg], y[seg], color=color, linewidth=CURVE_WIDTH, linestyle=line_style, zorder=4)
        _curve_exit_arrows(ax, f, fprime, color, xmin, xmax, ymin, ymax, arrow_length=0.55)
    for region in regions:
        if region["shade"] == "above":
            ax.fill_between(x, region["y"], ymax, where=(region["y"] <= ymax), color=region["color"], alpha=0.15, zorder=2)
        else:
            ax.fill_between(x, ymin, region["y"], where=(region["y"] >= ymin), color=region["color"], alpha=0.15, zorder=2)
    if len(regions) == 2:
        a, b = regions
        a_top = np.full(len(x), ymax) if a["shade"] == "above" else a["y"]
        a_bot = a["y"] if a["shade"] == "above" else np.full(len(x), ymin)
        b_top = np.full(len(x), ymax) if b["shade"] == "above" else b["y"]
        b_bot = b["y"] if b["shade"] == "above" else np.full(len(x), ymin)
        top = np.minimum(a_top, b_top)
        bot = np.maximum(a_bot, b_bot)
        overlap = top > bot
        if overlap.any():
            ax.fill_between(x, bot, top, where=overlap, color="mediumpurple", alpha=0.45, zorder=3)
    _style_standard_plane(ax, compact=False)
    ax.set_xlim(-10.5, 10.5)
    ax.set_ylim(-10.5, 10.5)
    ax.set_title(title, fontfamily="Times New Roman", fontsize=12, pad=22)
    return ax


def make_trig_graph(ax, functions, title=""):
    max_amp = max(abs(fn.get("a", 1)) + abs(fn.get("d", 0)) for fn in functions)
    y_max = max(np.ceil(max_amp * 1.3), 2)
    min_b = min(abs(fn.get("b", 1)) for fn in functions)
    period = 2 * np.pi / min_b
    x_max = period
    x = np.linspace(-x_max, x_max, 3000)
    for fn in functions:
        a, b, c, d = fn.get("a", 1), fn.get("b", 1), fn.get("c", 0), fn.get("d", 0)
        y = a * (np.sin(b * (x - c)) if fn.get("type", "sin") == "sin" else np.cos(b * (x - c))) + d
        ax.plot(x, y, color=fn.get("color", "steelblue"), linewidth=CURVE_WIDTH, zorder=3)
    ax.set_ylim(-y_max - 0.3, y_max + 0.3)
    ax.set_xlim(-x_max - 0.2, x_max + 0.2)
    step = np.pi / (4 * min_b)
    ticks = np.arange(-x_max, x_max + step * 0.01, step)

    def pi_label(v):
        v_pi = round(v / np.pi * 8) / 8
        if v_pi == 0:
            return "0"
        frac = Fraction(v_pi).limit_denominator(8)
        num, den = frac.numerator, frac.denominator
        if den == 1:
            if num == 1:
                return r"$\pi$"
            if num == -1:
                return r"$-\pi$"
            return rf"${num}\pi$"
        if num == 1:
            return rf"$\frac{{\pi}}{{{den}}}$"
        if num == -1:
            return rf"$-\frac{{\pi}}{{{den}}}$"
        if num < 0:
            return rf"$-\frac{{{abs(num)}\pi}}{{{den}}}$"
        return rf"$\frac{{{num}\pi}}{{{den}}}$"

    ax.set_xticks(ticks)
    ax.set_xticklabels([pi_label(t) if i % 2 == 0 else "" for i, t in enumerate(ticks)],
                       fontfamily="Times New Roman", fontsize=10)
    y_ticks = np.arange(-int(y_max), int(y_max) + 1, 1)
    ax.set_yticks(y_ticks)
    ax.set_yticklabels([str(int(t)) if t != 0 else "" for t in y_ticks], fontfamily="Times New Roman", fontsize=10)
    ax.grid(True, color=GRID_COLOR, linewidth=GRID_WIDTH, zorder=0)
    ax.tick_params(which="major", length=4, width=1.0, color=AXIS_COLOR)
    ax.spines["left"].set_position("zero")
    ax.spines["bottom"].set_position("zero")
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_linewidth(AXIS_WIDTH)
        ax.spines[s].set_color(AXIS_COLOR)
    ax.spines["left"].set_bounds(-y_max, y_max)
    ax.spines["bottom"].set_bounds(-x_max, x_max)
    tri = dict(arrowstyle="-|>", color=AXIS_COLOR, lw=AXIS_WIDTH, mutation_scale=14)
    ax.annotate("", xy=(x_max + 0.3, 0), xytext=(x_max, 0), arrowprops=tri, annotation_clip=False)
    ax.annotate("", xy=(-x_max - 0.3, 0), xytext=(-x_max, 0), arrowprops=tri, annotation_clip=False)
    ax.annotate("", xy=(0, y_max + 0.4), xytext=(0, y_max), arrowprops=tri, annotation_clip=False)
    ax.annotate("", xy=(0, -y_max - 0.4), xytext=(0, -y_max), arrowprops=tri, annotation_clip=False)
    ax.text(x_max + 0.35, 0.15, "x", fontsize=13, fontweight="bold", fontfamily="Times New Roman", ha="left", va="bottom")
    ax.text(0.15, y_max + 0.3, "y", fontsize=13, fontweight="bold", fontfamily="Times New Roman", ha="left", va="center")
    ax.set_title(title, fontfamily="Times New Roman", fontsize=12, pad=8)
    return ax


def make_bar_chart(ax, categories, values, title="", colors=None, ylabel="Frequency", xlabel=""):
    colors = "steelblue" if colors is None else colors
    x = np.arange(len(categories))
    ax.bar(x, values, color=colors, width=0.6, edgecolor="white", linewidth=0.8, zorder=3)
    ax.yaxis.grid(True, color=GRID_COLOR, linewidth=GRID_WIDTH, zorder=0)
    ax.set_axisbelow(True)
    ax.set_ylim(0, max(values) * 1.15 if values else 1)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontfamily="Times New Roman", fontsize=11)
    ax.set_xlim(-0.5, len(categories) - 0.5)
    for label in ax.get_yticklabels():
        label.set_fontfamily("Times New Roman")
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.spines["left"].set_linewidth(1.5)
    ax.spines["bottom"].set_linewidth(1.5)
    ax.set_xlabel(xlabel, fontfamily="Times New Roman", fontsize=12, fontweight="bold", labelpad=6)
    ax.set_ylabel(ylabel, fontfamily="Times New Roman", fontsize=12, fontweight="bold", labelpad=6)
    ax.set_title(title, fontfamily="Times New Roman", fontsize=12, pad=8)
    return ax


def make_histogram(ax, data, bins=10, title="", color="steelblue", ylabel="Frequency", xlabel="Value"):
    counts, _, _ = ax.hist(data, bins=bins, color=color, edgecolor="white", linewidth=0.8, zorder=3)
    ax.yaxis.grid(True, color=GRID_COLOR, linewidth=GRID_WIDTH, zorder=0)
    ax.set_axisbelow(True)
    ax.set_ylim(0, max(counts) * 1.15 if len(counts) else 1)
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.spines["left"].set_linewidth(1.5)
    ax.spines["bottom"].set_linewidth(1.5)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontfamily("Times New Roman")
    ax.set_xlabel(xlabel, fontfamily="Times New Roman", fontsize=12, fontweight="bold", labelpad=6)
    ax.set_ylabel(ylabel, fontfamily="Times New Roman", fontsize=12, fontweight="bold", labelpad=6)
    ax.set_title(title, fontfamily="Times New Roman", fontsize=12, pad=8)
    return ax


def make_scatter_plot(ax, x_data, y_data, xmin, xmax, ymin, ymax, color="steelblue", point_size=25,
                      point_scale=0.65, line_of_best_fit=False, xlabel="x", ylabel="y", title=""):
    x_data = np.asarray(x_data, dtype=float)
    y_data = np.asarray(y_data, dtype=float)
    ax.scatter(x_data, y_data, color=color, s=point_size * point_scale, zorder=4, clip_on=True)
    if line_of_best_fit and len(x_data) >= 2:
        m, b = np.polyfit(x_data, y_data, 1)
        fn = lambda x: m * x + b
        deriv = lambda x: np.asarray(x) * 0 + m
        x_ext, y_ext, segments = _function_segments(fn, xmin, xmax, ymin, ymax, samples=1000)
        for seg in segments:
            ax.plot(x_ext[seg], y_ext[seg], color="firebrick", linewidth=CURVE_WIDTH, zorder=3)
        _curve_exit_arrows(ax, fn, deriv, "firebrick", xmin, xmax, ymin, ymax,
                           arrow_length=(xmax - xmin) * 0.04)
    x_range = xmax - xmin
    y_range = ymax - ymin
    mx, my = x_range * 0.06, y_range * 0.06
    ax.set_xlim(xmin, xmax + mx)
    ax.set_ylim(ymin, ymax + my)
    x_step, y_step = _nice_grid_step(x_range), _nice_grid_step(y_range)
    x_ticks = np.arange(xmin, xmax + x_step * 0.01, x_step)
    y_ticks = np.arange(ymin, ymax + y_step * 0.01, y_step)
    for xt in x_ticks:
        ax.plot([xt, xt], [ymin, ymax], color=GRID_COLOR, linewidth=GRID_WIDTH, zorder=0, clip_on=True)
    for yt in y_ticks:
        ax.plot([xmin, xmax], [yt, yt], color=GRID_COLOR, linewidth=GRID_WIDTH, zorder=0, clip_on=True)
    x_every, y_every = _label_every(len(x_ticks)), _label_every(len(y_ticks))
    xl = [t for i, t in enumerate(x_ticks) if i % x_every == 0]
    yl = [t for i, t in enumerate(y_ticks) if i % y_every == 0]
    ax.set_xticks(xl)
    ax.set_yticks(yl)
    ax.set_xticklabels([_fmt(t) for t in xl], fontfamily="Times New Roman", fontsize=11)
    ax.set_yticklabels([_fmt(t) for t in yl], fontfamily="Times New Roman", fontsize=11)
    ax.tick_params(which="major", length=5, width=MAJOR_TICK_WIDTH, color=AXIS_COLOR)
    for s in ("left", "bottom"):
        ax.spines[s].set_linewidth(AXIS_WIDTH)
        ax.spines[s].set_color(AXIS_COLOR)
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.spines["left"].set_bounds(ymin, ymax)
    ax.spines["bottom"].set_bounds(xmin, xmax)
    tri = dict(arrowstyle="-|>", color=AXIS_COLOR, lw=AXIS_WIDTH, mutation_scale=14)
    ax.annotate("", xy=(xmax + mx, ymin), xytext=(xmax, ymin), arrowprops=tri, annotation_clip=False)
    ax.annotate("", xy=(xmin, ymax + my), xytext=(xmin, ymax), arrowprops=tri, annotation_clip=False)
    ax.set_xlabel(xlabel, fontfamily="Times New Roman", fontsize=13, fontweight="bold", labelpad=6)
    ax.set_ylabel(ylabel, fontfamily="Times New Roman", fontsize=13, fontweight="bold", labelpad=6, rotation=90)
    ax.set_title(title, fontfamily="Times New Roman", fontsize=12, pad=8)
    return ax


# -----------------------------------------------------------------------------
# Elementary / algebra visual models
# -----------------------------------------------------------------------------

def make_hundred_grid(shaded_cells=0, shaded_color="steelblue", filename="hundred_grid.png"):
    fig, ax = plt.subplots(figsize=(2.5, 2.5))
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_aspect("equal")
    ax.axis("off")
    for row in range(10):
        for col in range(10):
            filled = row * 10 + col < shaded_cells
            ax.add_patch(mpatches.Rectangle((col, 9 - row), 1, 1, linewidth=0.8, edgecolor="#555555",
                                             facecolor=shaded_color if filled else "white"))
    return save_graph(fig, filename)


def make_fraction_bar(n_parts, n_shaded=0, shaded_color="steelblue", label_parts=True,
                      filename="fraction_bar.png"):
    bar_w, bar_h, margin = 4.0, 0.75, 0.3
    fig_w, fig_h = bar_w + margin * 2, bar_h + margin * 2
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, fig_w)
    ax.set_ylim(0, fig_h)
    ax.axis("off")
    part_w = bar_w / n_parts
    for i in range(n_parts):
        left = margin + i * part_w
        filled = i < n_shaded
        ax.add_patch(mpatches.Rectangle((left, margin), part_w, bar_h, linewidth=1.2, edgecolor="black",
                                         facecolor=shaded_color if filled else "white"))
        if label_parts:
            ax.text(left + part_w / 2, margin + bar_h / 2, rf"$\frac{{1}}{{{n_parts}}}$",
                    ha="center", va="center", fontsize=11, fontfamily="Times New Roman",
                    color="white" if filled else "black")
    return save_graph(fig, filename)


def make_algebra_tiles(expression, filename="algebra_tiles.png"):
    colors = {
        "x2": "#5bacd6", "neg_x2": "#e05c5c", "y2": "#5bacd6", "neg_y2": "#e05c5c",
        "xy": "#4dab82", "neg_xy": "#e05c5c", "x": "#5bacd6", "neg_x": "#e05c5c",
        "y": "#9b59b6", "neg_y": "#e05c5c", "one": "#3a3ab0", "neg_one": "#e05c5c",
    }
    labels = {
        "x2": r"$x^2$", "neg_x2": r"$-x^2$", "y2": r"$y^2$", "neg_y2": r"$-y^2$",
        "xy": r"$x \cdot y$", "neg_xy": r"$-x \cdot y$", "x": r"$x$", "neg_x": r"$-x$",
        "y": r"$y$", "neg_y": r"$-y$", "one": r"$1$", "neg_one": r"$-1$",
    }
    dims = {
        "x2": (1, 1), "neg_x2": (1, 1), "y2": (1, 1), "neg_y2": (1, 1),
        "xy": (0.75, 0.75), "neg_xy": (0.75, 0.75), "x": (0.28, 1), "neg_x": (0.28, 1),
        "y": (0.28, 1), "neg_y": (0.28, 1), "one": (0.28, 0.28), "neg_one": (0.28, 0.28),
    }
    order = ["x2", "neg_x2", "y2", "neg_y2", "xy", "neg_xy", "x", "neg_x", "y", "neg_y", "one", "neg_one"]
    tiles = [kind for kind in order for _ in range(expression.get(kind, 0))]
    if not tiles:
        return None
    gap, pad, max_row_w = 0.15, 0.35, 5.5
    rows, row, row_w = [], [], 0.0
    for kind in tiles:
        width = dims[kind][0]
        if row and row_w + width + gap > max_row_w:
            rows.append(row)
            row, row_w = [kind], width + gap
        else:
            row.append(kind)
            row_w += width + gap
    if row:
        rows.append(row)
    row_heights = [max(dims[k][1] for k in r) for r in rows]
    total_h = sum(row_heights) + gap * (len(rows) - 1) + pad * 2
    total_w = max_row_w + pad * 2
    fig, ax = plt.subplots(figsize=(total_w, total_h))
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, total_w)
    ax.set_ylim(0, total_h)
    ax.axis("off")
    y_cursor = total_h - pad
    for ridx, row in enumerate(rows):
        rh = row_heights[ridx]
        y_cursor -= rh
        x_cursor = pad
        for kind in row:
            tw, th = dims[kind]
            ax.add_patch(mpatches.FancyBboxPatch((x_cursor, y_cursor + (rh - th) / 2), tw, th,
                                                  boxstyle="round,pad=0.02", linewidth=2.0,
                                                  edgecolor="white", facecolor=colors[kind]))
            ax.text(x_cursor + tw / 2, y_cursor + (rh - th) / 2 + th / 2, labels[kind],
                    ha="center", va="center", fontsize=13 if tw >= 0.7 else 9,
                    color="white", fontfamily="Times New Roman", style="italic")
            x_cursor += tw + gap
        y_cursor -= gap
    return save_graph(fig, filename)


# -----------------------------------------------------------------------------
# Capability metadata for tools that want to validate the runtime.
# -----------------------------------------------------------------------------
PUBLIC_GRAPH_FUNCTIONS = [
    "make_standard_graph", "make_window_graph", "make_context_graph",
    "make_number_line", "make_number_line_blank", "save_graph",
    "make_2x2_grid", "make_2x1_grid", "make_3x1_grid", "make_4x1_grid",
    "make_rectangle_model", "make_diamond", "make_piecewise_graph",
    "make_unit_circle_blank", "make_unit_circle_angles", "make_inequality_graph",
    "make_trig_graph", "make_bar_chart", "make_histogram", "make_scatter_plot",
    "make_hundred_grid", "make_fraction_bar", "make_algebra_tiles",
]
