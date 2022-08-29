"""Console script for lingtreemaps."""
import logging
import sys
from pathlib import Path
import click
import matplotlib.pyplot as plt
import pandas as pd
import yaml
from Bio import Phylo
import lingtreemaps


log = logging.getLogger(__name__)


def load_conf(conf_file="lingtreemaps.yaml"):
    confpath = Path(conf_file)
    if confpath.is_file():
        with open(confpath, "r", encoding="utf-8") as f:
            data = yaml.load(f, yaml.SafeLoader)
            if data is not None:
                return data
            log.warning(f"Empty config file: {confpath.resolve()}")
            return {}
    log.error(f"Config file {confpath.resolve()} not found.")
    return {}


@click.group()
def main():
    pass  # pragma: no cover


@main.command()
@click.argument("languages")
@click.argument("tree")
@click.option(
    "-f",
    "--feature",
    default=None,
    help="Path to a CSV with columns ``Clade`` and ``Value``.",
)
@click.option("-c", "--conf", default=None, help="Path to a YAML configuration file.")
@click.option(
    "-o", "--output", "filename", default=None, help="Name of the created map."
)
@click.option(
    "-d",
    "--debug",
    is_flag=True,
    default=False,
    help="Show calculated values and orientation lines on the map.",
)
def plot(
    languages, tree, feature, conf, filename, debug
):  # pylint: disable=too-many-arguments
    """LANGUAGES: A CSV file with languages.
    Minimally required columns: ``ID``, ``Latitude``, ``Longitude``.

    TREE: A newick tree file."""
    df = pd.read_csv(languages)
    if not filename:
        filename = Path(languages).stem
    tree = Phylo.read(tree, "newick")
    kwargs = dict(filename=filename, file_format="pdf", debug=debug)
    if conf:
        kwargs.update(**load_conf(conf))
    else:
        log.info("Provide a conf file to style your map.")
    if feature:
        feature_df = pd.read_csv(feature)
        lingtreemaps.plot(df, tree, feature_df, **kwargs)
    else:
        lingtreemaps.plot(df, tree, **kwargs)
    plt.show()


@main.command()
@click.argument("glottocode")
@click.option(
    "-l",
    "--languages",
    default=None,
    help="Path to a your language CSV file. Useful if there is a mismatch between "
    "your points on the map and the leafs of the glottolog tree.",
)
@click.option(
    "-p",
    "--plot",
    show_default=True,
    is_flag=True,
    default=False,
    help="Plot a quick map (without data).",
)
@click.option(
    "-g",
    "--get-languages",
    show_default=True,
    is_flag=True,
    default=False,
    help="Get a language table from the glottolog catalog as well.",
)
@click.option(
    "-o",
    "--output",
    "output_dir",
    default=".",
    show_default=True,
    help="Where to store the downloaded data.",
)
def download_tree(glottocode, languages, output_dir, get_languages, plot):
    """GLOTTOCODE: The glottocode of the root of the tree you want to download."""
    if get_languages:
        df = lingtreemaps.get_glottolog_csv(glottocode)
        df.to_csv(Path(output_dir) / f"{glottocode}.csv", index=False)
    elif languages:
        df = pd.read_csv(languages)
    else:
        log.warning(
            "If you do not provide CSV file with the language list, dialects without "
            "coordinates will show up in the tree."
        )
        df = None
    tree = lingtreemaps.download_glottolog_tree(root=glottocode, df=df)
    Phylo.draw_ascii(tree)
    Phylo.write(tree, Path(output_dir) / f"{glottocode}.nwk", "newick")
    kwargs = dict(filename=glottocode, file_format="svg")
    if plot:
        lingtreemaps.plot(df, tree, **kwargs)


@main.command()
@click.argument("glottocode")
@click.option(
    "-o",
    "--output",
    "output_dir",
    default=".",
    help="Where to store the downloaded data.",
)
def get_language_data(glottocode, output_dir):
    """Note: for this to work, you need to install cldfbench and download
    the glottolog catalog.

GLOTTOCODE: The glottocode of the root of the tree you want to download the language
list for."""
    df = lingtreemaps.get_glottolog_csv(glottocode)
    df.to_csv(Path(output_dir) / f"{glottocode}.csv", index=False)
    return df


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
