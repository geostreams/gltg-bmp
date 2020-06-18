import click

from flask import current_app
from flask.cli import with_appcontext

import pandas as pd
import geopandas as gpd

from geoalchemy2 import Geometry, WKTElement
from sqlalchemy import create_engine


def clean_column_names(df):
    return df.columns.str.strip().str.lower().str.replace(" ", "_").str.replace("[()]", "")


@click.command("import-data")
@with_appcontext
def import_data():
    config = current_app.config["IMPORT_PARAMS"]

    engine = create_engine(current_app.config["SQLALCHEMY_DATABASE_URI"])

    practices = pd.read_excel(parse_dates=False, **config["extra_input_args"])
    practices.index += 1
    practices.columns = clean_column_names(practices)

    practices.to_sql("practices", con=engine, index_label="id", **config["extra_output_args"])

    huc_8_column = config["huc_8_column_name"]
    huc8 = gpd.read_file("./data/WBD_National_GDB/WBD_National_GDB.gdb", layer="WBDHU8")
    huc8.to_crs("EPSG:4326", inplace=True)
    huc8.columns = clean_column_names(huc8)
    huc8.rename(columns={"huc8": huc_8_column}, inplace=True)
    huc8[huc_8_column] = huc8[huc_8_column].astype(str)
    huc8.sort_values(by=[huc_8_column], inplace=True)
    huc8 = huc8[huc8[huc_8_column].isin(practices[huc_8_column])][[huc_8_column, "name", "areaacres", "states", "geometry"]]
    huc8["geometry"] = huc8["geometry"].apply(lambda geom: WKTElement(geom.wkt, srid=4326))
    huc8.set_index(huc_8_column, inplace=True)

    huc8.to_sql("huc8", con=engine, if_exists="replace", dtype={"geometry": Geometry("MultiPolygon", srid=4326)})
