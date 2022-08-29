from lingtreemaps import plot
import pandas as pd
from Bio import Phylo


def test_pdf(data, tmp_path):
    df = pd.read_csv(data / "cariban.csv")
    df.rename(columns={"lat": "Latitude", "long": "Longitude"}, inplace=True)

    tree = Phylo.read(data / "cariban.newick", "newick")
    ax = plot(
        df,
        tree,
        tree_depth=6,
        leaf_marker_size=0.17,
        tree_map_padding=2.7,
        label_column="Name",
        map_marker_size=25,
        font_size=6.5,
        text_x_offset=0.3,
        text_y_offset=0.135,
        file_format="svg",
        leaf_lw=0.5,
        filename=tmp_path / "output",
    )
    assert (tmp_path / "output.svg").is_file()
