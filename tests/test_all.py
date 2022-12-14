import shutil
import pandas as pd
from Bio import Phylo
from click.testing import CliRunner
from lingtreemaps import download_glottolog_tree
from lingtreemaps import plot
from lingtreemaps.cli import download_tree, get_language_data
from lingtreemaps.cli import plot as cli_plot


def test_cli_download(data, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    runner.invoke(download_tree, args=["cari1283"])
    assert (tmp_path / "cari1283.nwk").is_file()


def test_cli_plot(data, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        cli_plot,
        args=[
            (data / "cariban.csv").as_posix(),
            (data / "cariban.newick").as_posix(),
            "--conf",
            (data / "cariban.yaml").as_posix(),
            "--output",
            "test.svg",
        ],
        catch_exceptions=False,
    )
    assert (tmp_path / "test.svg").is_file()

    result = runner.invoke(
        cli_plot,
        args=[
            (data / "cariban.csv").as_posix(),
            (data / "cariban.newick").as_posix(),
            "--conf",
            (data / "cariban.yaml").as_posix(),
        ],
        catch_exceptions=False,
    )
    assert (tmp_path / "cariban.pdf").is_file()


def get_features(df):
    dic = {1: "A", 2: "B", 3: "C"}
    df.sort_values(by="ID", inplace=True)
    data = []
    i = 1
    for lg in df.to_dict("records"):
        data.append({"Clade": lg["ID"], "Value": dic[i]})
        if i == 3:
            i = 1
        else:
            i += 1
    return pd.DataFrame.from_dict(data)


def test_plot0(data, tmp_path, monkeypatch):
    df = pd.read_csv(data / "cariban.csv")
    tree = Phylo.read(data / "cariban.newick", "newick")
    plot(
        df,
        tree,
        feature_df=get_features(df),
        filename=tmp_path / "test",
        file_format="svg",
    )
    assert (tmp_path / "test.svg").is_file()


def test_plot1(data, tmp_path, monkeypatch):
    df = pd.read_csv(data / "cariban.csv")
    tree = Phylo.read(data / "cariban.newick", "newick")
    plot(
        df,
        tree,
        feature_df=get_features(df),
        filename=tmp_path / "test",
        file_format="svg",
    )
    assert (tmp_path / "test.svg").is_file()


def test_plot2(data, tmp_path, monkeypatch):
    df = pd.read_csv(data / "cariban.csv")
    tree = Phylo.read(data / "cariban.newick", "newick")
    plot(
        df,
        tree,
        feature_df=get_features(df),
        tree_sort_mode="max",
        color_dict={"A": "red", "B": "green", "C": "yellow"},
        filename=tmp_path / "test",
        file_format="svg",
        debug=True,
    )
    assert (tmp_path / "test.svg").is_file()
