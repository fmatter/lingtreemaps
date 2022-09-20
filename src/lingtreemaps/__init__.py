"""Top-level package for lingtreemaps."""
import logging
import sys
import warnings
from io import StringIO
import colorlog
import contextily as cx
import geopandas as gpd
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import requests
import seaborn as sns
import shapely
import shapely.geometry
import yaml
from Bio import Phylo
from matplotlib import patheffects
from matplotlib.patches import Patch
from shapely.errors import ShapelyDeprecationWarning


warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning)

handler = colorlog.StreamHandler(None)
handler.setFormatter(
    colorlog.ColoredFormatter("%(log_color)s%(levelname)-7s%(reset)s %(message)s")
)
log = logging.getLogger(__name__)
log.propagate = True
log.setLevel(logging.INFO)
log.addHandler(handler)

__author__ = "Florian Matter"
__email__ = "florianmatter@gmail.com"
__version__ = "0.0.3"


try:
    from importlib.resources import files  # pragma: no cover
except ImportError:  # pragma: no cover
    from importlib_resources import files  # pragma: no cover

data_path = files("lingtreemaps") / "data"
plt.rcParams.update({"hatch.color": "white"})


def download_glottolog_tree(root, df=None):
    newick_url = f"https://glottolog.org/resource/languoid/id/{root}.newick.txt"
    handle = StringIO(requests.get(newick_url, timeout=20).text)
    tree = Phylo.read(handle, "newick")
    for clade in tree.find_clades():
        glottocode = clade.name.split("[")[1].split("]")[0]
        clade.name = glottocode
        if df is not None:
            if glottocode in list(df["ID"]) and not clade.is_terminal():
                for leaf in clade.get_terminals()[0:-1]:
                    tree.prune(leaf)
                clade.get_terminals()[0].name = f" [{glottocode}]"
        clade.branch_length = 1

    for clade in tree.find_clades():
        if clade.name == root:
            tree = clade
    return tree


def get_glottolog_csv(glottocode):
    try:
        from cldfbench.catalogs import Glottolog  # pylint: disable=import-outside-toplevel
        from cldfbench.catalogs import pyglottolog  # pylint: disable=import-outside-toplevel
    except ImportError:
        log.error("Please run pip install cldfbench[glottolog]")
        sys.exit()
    glottolog = pyglottolog.Glottolog(Glottolog.from_config().repo.working_dir)
    target = glottolog.languoid(glottocode)
    out = []
    for x in target.iter_descendants():
        if x.level.id == "language":
            out.append(
                {
                    "ID": x.id,
                    "Latitude": x.latitude,
                    "Longitude": x.longitude,
                    "Name": x.name,
                }
            )
    df = pd.DataFrame.from_dict(out)
    df = df[~(pd.isnull(df["Latitude"]))]
    return df


def plot(lg_df, tree, feature_df=None, text_df=None, **kwargs):
    with open(data_path / "default_config.yaml", "r", encoding="utf-8") as f:
        conf = yaml.load(f, Loader=yaml.SafeLoader)
    if isinstance(text_df, str):
        text_df = pd.read_csv(text_df, keep_default_na=False)
    conf.update(**kwargs)
    plot_map(lg_df, tree, feature_df, text_df, **conf)


def plot_map(  # noqa: MC0001
    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-locals
    # pylint: disable=too-many-branches
    # pylint: disable=too-many-statements
    # everything for a green linting badge
    lg_df,
    tree,
    feature_df,
    text_df,
    id_col,
    label_column,
    filename,
    file_format,
    tree_map_padding,
    tree_sort_mode,
    tree_depth,
    tree_lw,
    internal_map_padding,
    seaborn_palette,
    color_dict,
    hatch_dict,
    legend_position,
    leaf_marker_size,
    leaf_lw,
    map_marker_size,
    map_marker_lw,
    connection_lw,
    external_map_padding,
    font_size,
    print_labels,
    nonterminal_nodes,
    color_tree,
    hatching,
    text_x_offset,
    text_y_offset,
    base_padding,
    legend_size,
    rotation,
    ax,
    background,
    attribution_position,
    cx_provider,
    debug,
    **kwargs,
):
    land_color = "white"
    water_color = "lightgray"
    default_color = "orange"
    if feature_df is not None:
        if "Clade" not in feature_df.columns or "Value" not in feature_df.columns:
            raise ValueError(
                "Feature dataframe has to have columns 'Clade' and 'Value'"
            )
        lg_df = pd.merge(
            lg_df, feature_df, left_on=id_col, right_on="Clade", how="outer"
        )  # insert feature values into language table
        lg_df[id_col] = lg_df.apply(
            lambda x: x["Clade"] if pd.isnull(x[id_col]) else x[id_col], axis=1
        )
        values = []
        for x in list(feature_df["Value"]):
            if x not in values:
                values.append(x)
        if color_dict is None:
            palette = sns.color_palette(
                seaborn_palette, len(values)
            )  # generate palette
            value_color_dic = dict(
                zip(values, palette.as_hex())
            )  # what value corresponds to what color?
        else:
            value_color_dic = color_dict
        if hatching and hatch_dict is None:
            value_hatch_dic = dict(
                zip(
                    values,
                    [
                        "///",
                        "\\\\\\",
                        "|||",
                        "---",
                        "+++",
                        "xxx",
                        "ooo",
                        "O00",
                        "...",
                        "***",
                    ],
                )
            )
            hatch_dict = {}
        else:
            value_hatch_dic = hatch_dict
        lg_df["color"] = lg_df["Value"].apply(
            lambda x: value_color_dic.get(x, (0, 0, 0, 0))
        )  # use transparent color for missing values
        color_dic = dict(
            zip(lg_df[id_col], lg_df["color"])
        )  # what (leaf) name corresponds to what color?

    else:
        lg_df["color"] = default_color
        color_dic = {}
        value_color_dic = {}

    gdf = gpd.GeoDataFrame(
        lg_df, geometry=gpd.points_from_xy(lg_df.Longitude, lg_df.Latitude)
    )  # convert to a geodataframe

    gdf.dropna(inplace=True, subset=["Latitude", "Longitude"])

    bounds = gdf.geometry.total_bounds  # outer boundaries of the language points
    rect = shapely.geometry.box(*bounds)  # as a shapely entity
    gdf["geometry"] = gdf["geometry"].rotate(
        rotation, origin=rect.centroid
    )  # rotate entire dataframe around center of box
    gdf["y"] = gdf["geometry"].apply(lambda x: x.y)  # get "y" value for later sorting

    def get_clade_extreme(clade, df, tree_sort_mode=tree_sort_mode):
        """Returns the smallest/largest "y" value of any child in the clade"""
        leaf_names = [x.name for x in clade.get_terminals()]
        if tree_sort_mode == "min":
            return df[df[id_col].isin(leaf_names)]["y"].min()
        if tree_sort_mode == "max":
            return df[df[id_col].isin(leaf_names)]["y"].max()
        raise ValueError("Specify min or max.")

    def sort_clade(clade, df, tree_sort_mode=tree_sort_mode, **kwargs):
        """Sorts the children of a clade according to their "y" value"""
        del kwargs
        children = clade.clades
        children = sorted(
            children, key=lambda x: get_clade_extreme(x, df, tree_sort_mode)
        )
        clade.clades = children

    def sort_tree(tree, df, **kwargs):
        for clade in tree.find_clades(order="level"):
            if len(clade.get_terminals()) > 1:
                sort_clade(clade, df, **kwargs)

    sort_tree(tree, gdf, **kwargs)

    def get_max_depth(clade):
        """How deep does a clade go?"""
        depths = clade.depths()
        if not max(depths.values()):
            depths = clade.depths(unit_branch_lengths=True)
        return max(depths.values()) * tree_depth / actual_tree_depth

    # start plotting
    if not ax:
        fig = plt.figure()
        ax = fig.add_axes([0, 0, 1, 1])

    if not cx_provider:
        if "countries" in background:
            # load shapefiles
            world = gpd.read_file(data_path / "world-administrative-boundaries.shp")
            waters = gpd.read_file(data_path / "MajorRivers.shp")

            # rotate the background, too
            world["geometry"] = world["geometry"].rotate(rotation, origin=rect.centroid)
            waters["geometry"] = waters["geometry"].rotate(
                rotation, origin=rect.centroid
            )
            world.plot(
                ax=ax,
                color=land_color,
                edgecolor="gray",
                lw=0.7,
                linestyle="--",
                zorder=0,
            )
        if "rivers" in background:
            fig.set_facecolor(water_color)
            waters.plot(ax=ax, color=water_color, edgecolor="black", lw=1, zorder=1)

    leaf_count = len(tree.get_terminals())
    map_height = abs(gdf.geometry.total_bounds[1] - gdf.geometry.total_bounds[3])
    leaf_spacing = map_height / leaf_count

    bounds = gdf.geometry.total_bounds  # tight box around the points
    internal_map_padding = internal_map_padding or leaf_spacing * 0.5
    data_rect = shapely.geometry.box(*bounds)

    # how deep is the entire tree?
    tree_depth = tree_depth or (bounds[2] - bounds[0]) / 3

    actual_tree_depth = tree.depths()
    if not max(actual_tree_depth.values()):
        actual_tree_depth = tree.depths(unit_branch_lengths=True)
    actual_tree_depth = max(actual_tree_depth.values())

    tree_map_padding = tree_map_padding or tree_depth * 0.2

    visible_map = [
        bounds[0] - internal_map_padding,
        bounds[1] - internal_map_padding,
        bounds[2] + internal_map_padding,
        bounds[3] + internal_map_padding,
    ]  # larger padding box
    visible_map_rect = shapely.geometry.box(*visible_map)

    base_padding = base_padding or tree_depth * 0.05

    if debug:
        external_map_padding = base_padding

    outer_bounds = [
        visible_map[0]
        - external_map_padding
        - tree_depth
        - base_padding
        - tree_map_padding,  # make space for the tree
        visible_map[1] - external_map_padding,
        visible_map[2] + external_map_padding,
        visible_map[3] + external_map_padding,
    ]  # bounds of the whole image including the tree
    picture_rect = shapely.geometry.box(*outer_bounds)

    # cut out visible map box, creating a mask
    mask = picture_rect.difference(visible_map_rect)
    mask = gpd.GeoSeries(mask)

    outer_rect = gpd.GeoSeries(picture_rect)

    xlim = [outer_bounds[0], outer_bounds[2]]
    ylim = [outer_bounds[1], outer_bounds[3]]
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)

    if debug:
        ax.grid(color="gray", linestyle="dotted")
    else:
        ax.axis("off")

    leaf_df = gdf.copy()

    if hatching:
        for value, hatch in hatch_dict.items():
            gdf[gdf["Value"] == value].plot(
                ax=ax,
                markersize=map_marker_size,
                facecolor=gdf[gdf["Value"] == value]["color"],
                linewidth=map_marker_lw,
                zorder=99,
                hatch=hatch,
            )
        gdf[pd.isnull(gdf["Value"])].plot(
            ax=ax,
            markersize=map_marker_size,
            facecolor=gdf[pd.isnull(gdf["Value"])]["color"],
            linewidth=map_marker_lw,
            edgecolor="black",
            zorder=88,
        )
    else:
        gdf.plot(
            ax=ax,
            markersize=map_marker_size,
            facecolor=gdf["color"],
            linewidth=map_marker_lw,
            edgecolor="black",
            zorder=99,
        )

    leaf_positions = {}
    i = 0
    for x in reversed(tree.get_terminals()):
        leaf_positions[x] = i
        i += leaf_spacing

    def get_clade_middle(clade):
        values = [leaf_positions[child] for child in clade.get_terminals()]
        return (max(values) + min(values)) / 2

    tree_baseline = visible_map[0] - tree_map_padding
    sideline = bounds[-1] - leaf_spacing * 0.5

    node_leafs = {}

    def draw_clade(clade, color, lw):
        lvl_line_start = get_clade_middle(clade.clades[0])
        lvl_line_end = get_clade_middle(clade.clades[-1])
        clade_depth = get_max_depth(clade)

        log.debug(
            f"""clade: {clade}
    tree_baseline: {tree_baseline}
    tree depth: {tree_depth}
    clade depth: {clade_depth}
    line on: {tree_baseline-clade_depth}
    side: {sideline}
    start: {lvl_line_start}
    end: {lvl_line_end}
    """
        )
        ax.vlines(
            tree_baseline - clade_depth,
            sideline - lvl_line_start,
            sideline - lvl_line_end,
            color=color,
            lw=lw,
        )
        if clade.clades:
            for child in clade.clades:
                child_depth = get_max_depth(child)
                log.debug(
                    f"""child: {child}
    depth: {child_depth}
    line at: {sideline-get_clade_middle(child)}
    from: {tree_baseline-clade_depth}
    to: {tree_baseline+tree_depth-child_depth}
    """
                )
                if color_tree:
                    node_entries = lg_df[lg_df[id_col] == child.name]
                    if len(node_entries) > 0:
                        color = node_entries.iloc[0]["color"]
                    else:
                        color = "black"
                else:
                    color = "black"
                ax.hlines(
                    sideline - get_clade_middle(child),
                    tree_baseline - clade_depth,
                    tree_baseline - child_depth,
                    color=color,
                    lw=lw,
                )
                if child.is_terminal():
                    leaf_coords = (
                        tree_baseline - child_depth,
                        sideline - get_clade_middle(child),
                    )
                    node_leafs[child.name] = leaf_coords
                    node_alpha = 1
                    for point in gdf[gdf[id_col] == child.name].to_dict("records"):
                        map_node = (point["geometry"].x, point["geometry"].y)
                        if print_labels:
                            label_text = gdf[gdf[id_col] == child.name].iloc[0][
                                label_column
                            ]
                        else:
                            label_text = ""
                        ax.annotate(
                            xytext=(
                                leaf_coords[0] + text_x_offset,
                                leaf_coords[1] - text_y_offset,
                            ),
                            text=label_text,
                            # .upper(),
                            xy=map_node,
                            alpha=node_alpha,
                            size=font_size,
                            fontname="Linux Libertine",
                            arrowprops={
                                "arrowstyle": "-",
                                "color": point["color"],
                                "shrinkA": 0,
                                "shrinkB": 3.5,
                                "linewidth": connection_lw,
                                "linestyle": "dotted",
                            },
                        )
                        if node_alpha == 1:
                            node_alpha = 0
                else:
                    if nonterminal_nodes and child.name in color_dic:
                        circle = plt.Circle(
                            (
                                tree_baseline - child_depth,
                                sideline - get_clade_middle(child),
                            ),
                            leaf_marker_size,
                            facecolor=color_dic[child.name],
                            edgecolor="black",
                            zorder=99,
                            lw=leaf_lw,
                        )
                        ax.add_patch(circle)

                    draw_clade(child, color, lw)

    if feature_df is not None:
        # https://www.python-graph-gallery.com/how-to-use-rectangles-in-matplotlib-legends
        if hatching:
            handles = [
                matplotlib.patches.Circle(
                    (0.5, 0.5),
                    1,
                    label=label,
                    facecolor=value_color_dic.get(label, default_color),
                    linewidth=3,
                    hatch=value_hatch_dic.get(label, None),
                )
                for label, color in value_color_dic.items()
            ]
        else:
            handles = [
                Patch(facecolor=color, label=label)
                for label, color in value_color_dic.items()
            ]

        bbox_coords = (
            visible_map[0],
            visible_map[1],
            visible_map[2] - visible_map[0],
            visible_map[3] - visible_map[1],
        )

        legend = ax.legend(
            handles=handles,
            loc=legend_position,
            bbox_to_anchor=bbox_coords,
            bbox_transform=ax.transData,
            prop={"size": legend_size, "family": "Linux Libertine"},
        ).get_frame()

        legend.set_edgecolor("black")
        legend.set_facecolor("white")

    # add text labels
    if text_df is not None:
        for text in text_df.to_dict("records"):
            ax.text(
                text["Longitude"],
                text["Latitude"],
                s=text["Label"],
                size=font_size * 0.85,
                ha="center",
                color="gray",
                va="center",
            )

    outer_rect.plot(ax=ax, edgecolor="black", facecolor="none", zorder=10, lw=1)
    mask.plot(ax=ax, color="white", alpha=1, edgecolor="black", lw=0.5)
    tree_lw = tree_lw or plt.rcParams["lines.linewidth"]

    tree_color = color_dic.get(tree.root.name, "black")
    draw_clade(tree.root, tree_color, tree_lw)

    leaf_df["geometry"] = leaf_df.apply(
        lambda x: shapely.geometry.Point(node_leafs[x[id_col]]), axis=1
    )

    if hatching:
        for value, hatch in hatch_dict.items():
            leaf_df[leaf_df["Value"] == value].plot(
                ax=ax,
                markersize=leaf_marker_size,
                facecolor=leaf_df[leaf_df["Value"] == value]["color"],
                linewidth=leaf_lw,
                zorder=99,
                hatch=hatch,
            )
        leaf_df[pd.isnull(leaf_df["Value"])].plot(
            ax=ax,
            markersize=leaf_marker_size,
            facecolor=leaf_df[pd.isnull(leaf_df["Value"])]["color"],
            linewidth=leaf_lw,
            edgecolor="black",
            zorder=99,
        )
    else:
        leaf_df.plot(
            ax=ax,
            markersize=leaf_marker_size,
            facecolor=leaf_df["color"],
            linewidth=leaf_lw,
            edgecolor="black",
            zorder=99,
        )

    def get_attribution_position(position):
        if position == "bottomleft":
            return (
                visible_map[0] + (visible_map[2] - visible_map[0]) * 0.005,
                visible_map[1] + (visible_map[3] - visible_map[1]) * 0.005,
                "left",
                "bottom",
            )
        if position == "bottomright":
            return (
                visible_map[2] - (visible_map[2] - visible_map[0]) * 0.005,
                visible_map[1] + (visible_map[3] - visible_map[1]) * 0.005,
                "right",
                "bottom",
            )
        if position == "topleft":
            return (
                visible_map[0] + (visible_map[2] - visible_map[0]) * 0.005,
                visible_map[3] - (visible_map[3] - visible_map[1]) * 0.005,
                "left",
                "top",
            )
        if position == "topright":
            return (
                visible_map[2] - (visible_map[2] - visible_map[0]) * 0.005,
                visible_map[3] - (visible_map[3] - visible_map[1]) * 0.005,
                "right",
                "top",
            )
        log.error(
            "Please specify a valid attrib position: bottomleft,\
         bottomright, topleft, or topright."
        )
        sys.exit(1)

    if background == "osm":
        cx_provider = cx.providers.OpenStreetMap.Mapnik

    if cx_provider:
        cx.add_basemap(ax, crs="epsg:4326", source=cx_provider, attribution="")
        pos_x, pos_y, halign, valign = get_attribution_position(attribution_position)
        # copied from
        # https://github.com/geopandas/contextily/blob/72c85a1097dfad6f03d2b0b17cd92dfd8171b0ee/contextily/plotting.py#L249
        # (needed to set custom xy values)

        # Original work: Copyright (c) 2016, Dani Arribas-Bel
        # Modified work: Copyright 2022 Florian Matter
        # All rights reserved.

        # Redistribution and use in source and binary forms, with or without
        # modification, are permitted provided that the following conditions are met:

        # * Redistributions of source code must retain the above copyright notice, this
        #   list of conditions and the following disclaimer.

        # * Redistributions in binary form must reproduce the above copyright
        #   notice, this list of conditions and the following disclaimer in the
        #   documentation and/or other materials provided with the distribution.

        # * Neither the name of Dani Arribas-Bel nor the names of other contributors
        #   may be used to endorse or promote products derived from this software
        #   without specific prior written permission.

        # THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
        # CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
        # INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
        # MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
        # DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
        # CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
        # SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
        # LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
        # USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
        # ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
        # LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
        # ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
        # POSSIBILITY OF SUCH DAMAGE.

        ax.text(
            x=pos_x,
            y=pos_y,
            s=cx.providers.OpenStreetMap.Mapnik.attribution,
            ha=halign,
            va=valign,
            transform=ax.transData,
            size=font_size,
            path_effects=[patheffects.withStroke(linewidth=2, foreground="w")],
            wrap=True,
        )

    if debug:
        ax.vlines(x=tree_baseline, ymin=-90, ymax=90, color="blue", linewidth=1)
        ax.vlines(
            x=tree_baseline - tree_depth, ymin=-90, ymax=90, color="c", linewidth=1
        )
        ax.hlines(y=sideline, xmin=-90, xmax=90, color="red", linewidth=1)
        gpd.GeoSeries(data_rect).plot(ax=ax, facecolor="none", edgecolor="g")
        gpd.GeoSeries(visible_map_rect).plot(ax=ax, facecolor="none", edgecolor="m")
        log.info(
            f"""
tree_map_padding = {tree_map_padding}
internal_map_padding = {internal_map_padding}
text_x_offset = {text_x_offset}
text_y_offset = {text_y_offset}
tree_depth = {tree_depth}
tree_lw = {tree_lw}
base_padding = {base_padding}
leaf_marker_size = {leaf_marker_size}"""
        )

    if filename:
        if "." in str(filename):
            filename, file_format = filename.split(".")
        log.info(f"Saving file {filename}.{file_format}")
        if "tif" in file_format:
            plt.savefig(
                f"{filename}.{file_format}", bbox_inches="tight", pad_inches=0, dpi=2000
            )
        else:
            out_path = f"{filename}.{file_format}"
            plt.savefig(out_path, bbox_inches="tight", pad_inches=0)

    return ax
