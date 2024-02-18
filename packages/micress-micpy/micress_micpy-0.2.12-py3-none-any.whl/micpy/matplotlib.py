import os
from distutils.version import LooseVersion


try:
    import matplotlib
    from matplotlib import pyplot

except ImportError:
    matplotlib = None
    pyplot = None


def _register_colormaps():
    colors = [
        "#1102d8",
        "#3007ba",
        "#500b9d",
        "#6f0e81",
        "#8d1364",
        "#ac1748",
        "#cb1b2b",
        "#ea1e0f",
        "#f83605",
        "#fa600f",
        "#fb8817",
        "#fdb120",
        "#ffda29",
        "#ffed4d",
        "#fff380",
        "#fffbb4",
    ]

    version = LooseVersion(matplotlib.__version__) >= LooseVersion("3.7")

    create = matplotlib.colors.LinearSegmentedColormap.from_list

    colormap = create(name="micpy", colors=colors, N=1024)
    colormap_r = create(name="micpy_r", colors=colors[::-1], N=1024)

    if version:
        register = matplotlib.colormaps.register
        register(colormap)
        register(colormap_r)
    else:
        register = matplotlib.cm.register_cmap
        register("micpy", colormap)
        register("micpy_r", colormap_r)


def _set_aixvipmap_font():
    font = "IBM Plex Sans"
    if font in matplotlib.font_manager.get_font_names():
        pyplot.rcParams["font.family"] = font


def _set_aixvipmap_colors():
    colors = [
        "#00549F",
        "#F6A800",
        "#57AB27",
        "#CC071E",
        "#612158",
        "#006165",
        "#E30066",
        "#0098A1",
        "#BDCD00",
        "#0098A1",
    ]
    pyplot.rcParams["axes.prop_cycle"] = pyplot.cycler(color=colors)


def configure():
    if not matplotlib:
        return

    try:
        _register_colormaps()
    except ValueError:
        pass

    if "AIXVIPMAP_HOME" in os.environ:
        _set_aixvipmap_font()
        _set_aixvipmap_colors()
