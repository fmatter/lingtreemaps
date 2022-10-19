import importlib
import logging
from pathlib import Path
import pandas as pd


log = logging.getLogger(__name__)


def read_data_file(filename, **kwargs):
    filename = Path(filename)
    if filename.suffix == ".csv":
        return pd.read_csv(filename, **kwargs)
    if filename.suffix == ".xlsx":
        try:
            importlib.import_module("openpyxl")
        except ImportError as exc:
            raise ImportError(
                "To work with excel files, please install openpyxl (via pip or conda)."
            ) from exc
        return pd.read_excel(filename, **kwargs)

    raise ValueError("Tabular data must be in .csv or .xlsx format")
