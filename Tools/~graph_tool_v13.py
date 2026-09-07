# =============================================================================
# ~graph_tool_v13.py — AUTHORITATIVE GRAPH ENTRYPOINT
# =============================================================================
#
# v13 preserves graph-tool v12 behavior and reduces visual line weight for
# coordinate/modeling graphs. The v12 file remains the behavior base and MUST
# be staged beside this file when this entrypoint is copied to a build folder.
#
# v13 styling rule:
#   standard/context grid lines: 0.6 -> 0.4
#   standard/context axes:      1.8 -> 1.2
#   standard/context curves:    2.0 -> 1.5
#   standard/context arrows:    1.5/1.8 -> 1.2
#   compact multi-graph axes/grids are reduced proportionally.
#
# Do not manually override graph styling in generation blocks.
# =============================================================================

from pathlib import Path
import importlib.util
import os


def _find_v12():
    here = Path(__file__).resolve()
    candidates = [here.with_name('~graph_tool_v12.py')]

    env_root = os.environ.get('CURRICULUM_MEMORIES_ROOT')
    if env_root:
        candidates.append(Path(env_root) / 'Tools' / '~graph_tool_v12.py')

    candidates.append(Path.home() / 'Documents' / 'GitHub' / 'memories' / 'Tools' / '~graph_tool_v12.py')

    for parent in here.parents:
        candidates.append(parent / 'Tools' / '~graph_tool_v12.py')
        candidates.append(parent / 'memories' / 'Tools' / '~graph_tool_v12.py')

    seen = set()
    for candidate in candidates:
        candidate = candidate.expanduser()
        key = str(candidate)
        if key in seen:
            continue
        seen.add(key)
        if candidate.exists():
            return candidate

    raise FileNotFoundError(
        'Graph tool v13 requires Tools/~graph_tool_v12.py as its behavior base. '
        'Stage v12 beside v13 or set CURRICULUM_MEMORIES_ROOT.'
    )


_BASE_PATH = _find_v12()
_spec = importlib.util.spec_from_file_location('_curriculum_graph_tool_v12', str(_BASE_PATH))
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)

# Re-export the v12 public surface so v13 remains a drop-in graph tool.
for _name in dir(_base):
    if not _name.startswith('__'):
        globals()[_name] = getattr(_base, _name)


def _thin_coordinate_axis(ax, *, compact=False):
    grid_width = 0.4
    axis_width = 1.1 if compact else 1.2
    curve_width = 1.2 if compact else 1.5
    arrow_width = 1.0 if compact else 1.2

    for line in list(ax.get_xgridlines()) + list(ax.get_ygridlines()):
        line.set_linewidth(grid_width)

    for spine_name in ('left', 'bottom'):
        spine = ax.spines.get(spine_name)
        if spine is not None and spine.get_visible():
            spine.set_linewidth(axis_width)

    for line in ax.lines:
        try:
            color = line.get_color()
            width = float(line.get_linewidth())
        except Exception:
            continue
        if color == '#aaaaaa':
            line.set_linewidth(grid_width)
        elif width >= 1.9:
            line.set_linewidth(curve_width)
        elif compact and width >= 1.45:
            line.set_linewidth(curve_width)

    for child in ax.get_children():
        arrow_patch = getattr(child, 'arrow_patch', None)
        if arrow_patch is None:
            continue
        try:
            if float(arrow_patch.get_linewidth()) >= 1.4:
                arrow_patch.set_linewidth(arrow_width)
        except Exception:
            pass


_v12_make_standard_graph = _base.make_standard_graph
_v12_make_context_graph = _base.make_context_graph


def make_standard_graph(ax, functions, title=''):
    result = _v12_make_standard_graph(ax, functions, title=title)
    _thin_coordinate_axis(ax, compact=False)
    return result


def make_context_graph(ax, functions, xmin, xmax, ymin, ymax,
                       xlabel='x', ylabel='y', title=''):
    result = _v12_make_context_graph(
        ax, functions, xmin, xmax, ymin, ymax,
        xlabel=xlabel, ylabel=ylabel, title=title
    )
    _thin_coordinate_axis(ax, compact=False)
    return result


if hasattr(_base, 'make_2x2_grid'):
    _v12_make_2x2_grid = _base.make_2x2_grid

    def make_2x2_grid(functions_list, titles=None):
        fig = _v12_make_2x2_grid(functions_list, titles=titles)
        for ax in fig.axes:
            _thin_coordinate_axis(ax, compact=True)
        return fig


if hasattr(_base, 'make_3x1_grid'):
    _v12_make_3x1_grid = _base.make_3x1_grid

    def make_3x1_grid(functions_list, titles=None):
        fig = _v12_make_3x1_grid(functions_list, titles=titles)
        for ax in fig.axes:
            _thin_coordinate_axis(ax, compact=True)
        return fig


if hasattr(_base, 'make_4x1_grid'):
    _v12_make_4x1_grid = _base.make_4x1_grid

    def make_4x1_grid(functions_list, titles=None):
        fig = _v12_make_4x1_grid(functions_list, titles=titles)
        for ax in fig.axes:
            _thin_coordinate_axis(ax, compact=True)
        return fig


# All number-line and non-coordinate helpers are inherited unchanged from v12.
# =============================================================================
