import json
import logging
import os
from functools import reduce
from typing import List

import geopandas as gpd
import pandas as pd
import sqlalchemy
from geoalchemy2 import Geometry, WKTElement
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

Base = declarative_base()


class Database:
    engine: Engine

    db_session: scoped_session

    def __init__(self, host: str, port: str, user: str, password: str, db_name: str):
        cred = []
        if user:
            cred.append(user)
            if password:
                cred.append(":")
                cred.append(password)
            cred.append("@")
        cred = "".join(cred)

        db_uri = f"postgresql+psycopg2://{cred}{host}:{port}/{db_name}"
        logging.info(db_uri)

        self.engine = create_engine(db_uri, convert_unicode=True)
        db_session = scoped_session(
            sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        )

        Base.query = db_session.query_property()

        self.db_session = db_session

    def get_session(self):
        return self.db_session

    def shutdown(self):
        if self.db_session:
            self.db_session.remove()
        if self.engine:
            self.engine.dispose()

    @staticmethod
    def clean_column_names(df: pd.DataFrame):
        return (
            df.columns.str.strip()
            .str.lower()
            .str.replace(" ", "_")
            .str.replace("[()]", "")
        )

    def prepare(self):
        print("Preparing database...")
        self.import_states()
        self.import_assumptions()
        self.import_huc8_meta()
        self.import_huc8()

    def import_states(self):
        print("Loading States...")
        states = pd.read_excel(
            "./data/boundaries.xlsx",
            sheet_name="States",
            dtype={
                "state": "str",
                "area_sq_mi": "float64",
                "size_ac": "float64",
                "total_p_load_lbs": "float64",
                "total_n_load_lbs": "float64",
                "rowcrop_p_yield_lbs_per_ac": "float64",
                "rowcrop_n_yield_lbs_per_ac": "float64",
                "fraction_p": "float64",
                "fraction_n": "float64",
                "overall_p_yield_lbs_per_ac": "float64",
                "overall_n_yield_lbs_per_ac": "float64",
            },
        )

        print("Importing States...")
        states.set_index(states["state"]).sort_index().drop("state", axis=1).to_sql(
            "states", con=self.engine, index_label="id", if_exists="replace"
        )

    def import_assumptions(self):
        print("Loading assumptions...")
        source_file = "./data/assumptions.xlsx"
        assumptions = pd.read_excel(source_file, sheet_name="Practices", dtype="str")
        assumptions["wq"] = pd.to_numeric(assumptions["wq"]).astype("Int64")
        assumptions = (
            assumptions.set_index(assumptions["code"]).sort_index().drop("code", axis=1)
        )

        def join_json_columns(main: pd.DataFrame, sheet_info: (str, str)):
            (sheet_name, column_name) = sheet_info

            sheet = pd.read_excel(source_file, sheet_name=sheet_name, dtype="str")
            sheet = (
                sheet.set_index(sheet["code"])
                .sort_index()
                .drop("code", axis=1)
                .fillna("")
            )
            sheet[column_name] = sheet.apply(lambda row: row.to_dict(), axis=1)

            return main.join(sheet[column_name], on="code")

        print("Importing assumptions...")
        reduce(
            join_json_columns,
            (
                ("Water Quality Benefits", "wq_benefits"),
                ("Life Span", "life_span"),
                ("N Red", "nitrogen"),
                ("P Red", "phosphorus"),
                ("Cost Share Fraction", "cost_share_fraction"),
                ("Category", "category"),
                ("Practice Conv", "conv"),
                ("Ancillary Benefits", "ancillary_benefits"),
            ),
            assumptions,
        ).to_sql(
            "assumptions",
            con=self.engine,
            index_label="id",
            if_exists="replace",
            dtype={
                "wq_benefits": sqlalchemy.types.JSON,
                "life_span": sqlalchemy.types.JSON,
                "nitrogen": sqlalchemy.types.JSON,
                "phosphorus": sqlalchemy.types.JSON,
                "cost_share_fraction": sqlalchemy.types.JSON,
                "category": sqlalchemy.types.JSON,
                "conv": sqlalchemy.types.JSON,
                "ancillary_benefits": sqlalchemy.types.JSON,
            },
        )

    def import_huc8_meta(self):
        print("Loading HUC8 metadata...")
        source_file = "./data/boundaries.xlsx"
        huc8_meta = pd.read_excel(
            source_file,
            sheet_name="HUC8",
            dtype={
                "code": "str",
                "area_ac": "float64",
                "rowcrop_p_yield_lbs_per_ac": "float64",
                "total_p_yield_lbs_per_ac": "float64",
                "total_p_sparrow_lbs": "float64",
                "total_p_sparrow_adjusted_usgs_lbs": "float64",
                "adjusted_rowcrop_p_yield_lbs_per_ac": "float64",
                "rowcrop_n_yield_lbs_per_ac": "float64",
                "total_n_yield_lbs_per_ac": "float64",
                "total_n_sparrow_lbs": "float64",
                "total_n_sparrow_adjusted_usgs_lbs": "float64",
                "adjusted_rowcrop_n_yield_lbs_per_ac": "float64",
            },
        )

        huc8_meta.columns = self.clean_column_names(huc8_meta)

        huc8_meta.set_index(huc8_meta["code"]).sort_index().drop("code", axis=1)

        huc8_meta.to_sql(
            "huc8_meta",
            con=self.engine,
            if_exists="replace",
            dtype={
                "states": sqlalchemy.types.JSON,
                "geometry": Geometry("MultiPolygon", srid=4326),
            },
        )

    def import_huc8(self):
        print("Loading HUC8s...")
        huc8 = gpd.read_file(
            "./data/WBD_National_GDB/WBD_National_GDB.gdb", layer="WBDHU8"
        )
        huc8.to_crs("EPSG:4326", inplace=True)
        huc8.columns = self.clean_column_names(huc8)
        huc8.huc8 = huc8.huc8.astype(str)
        huc8.sort_values(by=["huc8"], inplace=True)
        huc8 = huc8[["huc8", "name", "areaacres", "states", "geometry"]]
        huc8["states"] = huc8["states"].apply(lambda x: x.split(","))
        huc8["geometry"] = huc8["geometry"].apply(
            lambda geom: WKTElement(geom.wkt, srid=4326)
        )
        huc8.set_index("huc8", inplace=True)

        print("Importing HUC8s...")
        huc8.to_sql(
            "huc8",
            con=self.engine,
            if_exists="replace",
            dtype={
                "states": sqlalchemy.types.JSON,
                "geometry": Geometry("MultiPolygon", srid=4326),
            },
        )

    def get_states(self):
        return pd.read_sql("SELECT * FROM states", con=self.engine, index_col="id")

    def get_assumptions(self):
        return pd.read_sql("SELECT * FROM assumptions", con=self.engine, index_col="id")

    def get_huc8_meta(self):
        huc8_meta = pd.read_sql(
            sql="SELECT * FROM huc8_meta", con=self.engine, index_col="index"
        )
        huc8_meta["code"] = huc8_meta["code"].astype("string")
        return huc8_meta

    def import_practices(self, practices_paths: List[str]):
        states = self.get_states()
        assumptions = self.get_assumptions()
        huc8_meta = self.get_huc8_meta()

        all_practices = []
        for practices_path in practices_paths:
            print("Getting practices...")
            practices = pd.read_excel(
                practices_path,
                header=1,
                usecols="A:M",
                dtype={
                    "HUC 8": "str",
                    "HUC 12": "str",
                    "County Code": "str",
                    "NRCS Practice Code": "str",
                    "Applied Date": "Int64",
                },
                parse_dates=False,
            )
            practices.columns = self.clean_column_names(practices)
            all_practices.append(practices)
        all_practices = pd.concat(all_practices)
        all_practices.columns = self.clean_column_names(all_practices)
        all_practices.index += 1

        print("Updating practices...")
        missing_huc8 = set()
        sunset = []
        active_year = []
        category = []
        wq_benefits = []
        area_treated = []
        ancillary_benefits = []
        p_reduction_fraction = []
        n_reduction_fraction = []
        p_reduction_percentage_statewide = []
        n_reduction_percentage_statewide = []
        p_reduction_gom_lbs = []
        n_reduction_gom_lbs = []

        with open("./data/baselines.json", "r") as f:
            baselines = json.loads(f.read())

        def get_nutrient_reduction(
            nutrient,
            huc8_rowcrop_nutrient_str,
            state_sum_total_nutrient_load_lbs,
            state_total_nutrient_load_lbs,
            nutrient_reduction_fraction,
            nutrient_reduction_percentage_statewide,
        ):
            practice_nutrient = practice_assumptions[nutrient]
            if not pd.isna(practice_nutrient):
                state_nutrient_yield = float(
                    practice_nutrient[row.state] if practice_nutrient[row.state] else 0
                )
                if state_nutrient_yield <= 0:
                    state_nutrient_yield = float(
                        practice_nutrient["STEPL 4.4"]
                        if practice_nutrient["STEPL 4.4"]
                        else 0
                    )

                try:
                    huc8_nutrient_yield = huc8_meta.loc[row.huc_8][
                        huc8_rowcrop_nutrient_str
                    ]
                except KeyError:
                    huc8_nutrient_yield = 0
                    missing_huc8.add(row.huc_8)

                nutrient_reduction_fraction.append(
                    state_nutrient_yield
                    * huc8_nutrient_yield
                    * area_treated[-1]
                    / state_sum_total_nutrient_load_lbs
                )
                nutrient_reduction_percentage_statewide.append(
                    state_nutrient_yield
                    * huc8_nutrient_yield
                    * area_treated[-1]
                    / state_total_nutrient_load_lbs
                )
            else:
                nutrient_reduction_fraction.append(0)
                nutrient_reduction_percentage_statewide.append(0)

        for _, row in all_practices.iterrows():
            if row.nrcs_practice_code != "0":
                practice_assumptions = assumptions.loc[row.nrcs_practice_code]

                # Sunset
                practice_life_span = practice_assumptions["life_span"]
                if not pd.isna(practice_life_span):
                    sunset.append(
                        row.applied_date + int(practice_life_span[row.state]) - 1
                    )
                else:
                    sunset.append(row.applied_date)

                # Active Year
                if (
                    not pd.isna(row.applied_date)
                    and not pd.isna(sunset[-1])
                    and row.applied_date == sunset[-1]
                ):
                    active_year.append(row.applied_date)
                else:
                    active_year.append(None)

                # Category
                practice_category = practice_assumptions["category"]
                if not pd.isna(practice_category):
                    category.append(practice_category[row.state])
                else:
                    category.append(None)

                # Water Quality Benefits
                practice_wq_benefit = practice_assumptions["wq_benefits"]
                if not pd.isna(practice_wq_benefit):
                    wq_benefits.append(practice_wq_benefit[row.state])
                else:
                    wq_benefits.append(None)

                # Area Treated
                if row.practice_units == "sq ft":
                    area_treated.append(row.applied_amount / 43560)
                else:
                    practice_conversion_factor = practice_assumptions["conv"]
                    if not pd.isna(practice_conversion_factor):
                        area_treated.append(
                            row.applied_amount
                            * float(practice_conversion_factor[row.state])
                        )
                    else:
                        area_treated.append(None)

                # Ancillary Benefits
                practice_ancillary_benefits = practice_assumptions["ancillary_benefits"]
                if not pd.isna(practice_ancillary_benefits):
                    ancillary_benefits.append(
                        list(
                            filter(
                                lambda benefit: practice_ancillary_benefits[benefit]
                                == "1",
                                practice_ancillary_benefits,
                            )
                        )
                    )
                else:
                    ancillary_benefits.append([])

                # Phosphorus and Nitrogen Reduction (fraction and statewide percentage)
                for nutrient_reduction_fraction_args in (
                    (
                        "phosphorus",
                        "rowcrop_p_yield_lbs_per_ac",
                        states.total_p_load_lbs.sum(),
                        states.loc[row.state].total_p_load_lbs,
                        p_reduction_fraction,
                        p_reduction_percentage_statewide,
                    ),
                    (
                        "nitrogen",
                        "rowcrop_n_yield_lbs_per_ac",
                        states.total_n_load_lbs.sum(),
                        states.loc[row.state].total_n_load_lbs,
                        n_reduction_fraction,
                        n_reduction_percentage_statewide,
                    ),
                ):
                    get_nutrient_reduction(*nutrient_reduction_fraction_args)

                # Phosphorus Reduction at GOM (lbs)
                p_reduction_gom_lbs.append(
                    p_reduction_fraction[-1] * baselines["usgs_baseline_p_lbs"]
                )

                # Nitrogen Reduction at GOM (lbs)
                n_reduction_gom_lbs.append(
                    n_reduction_fraction[-1] * baselines["usgs_baseline_n_lbs"]
                )

            else:
                sunset.append(None)
                active_year.append(None)
                category.append(None)
                wq_benefits.append(None)
                area_treated.append(None)
                ancillary_benefits.append(None)
                p_reduction_fraction.append(None)
                n_reduction_fraction.append(None)
                p_reduction_percentage_statewide.append(None)
                n_reduction_percentage_statewide.append(None)
                p_reduction_gom_lbs.append(None)
                n_reduction_gom_lbs.append(None)

        calculated_columns = pd.DataFrame(
            {
                "sunset": sunset,
                "active_year": active_year,
                "category": category,
                "wq_benefits": wq_benefits,
                "area_treated": area_treated,
                "ancillary_benefits": ancillary_benefits,
                "p_reduction_fraction": p_reduction_fraction,
                "n_reduction_fraction": n_reduction_fraction,
                "p_reduction_percentage_statewide": p_reduction_percentage_statewide,
                "n_reduction_percentage_statewide": n_reduction_percentage_statewide,
                "p_reduction_gom_lbs": p_reduction_gom_lbs,
                "n_reduction_gom_lbs": n_reduction_gom_lbs,
            }
        )
        calculated_columns.index += 1

        if not os.path.exists("./logs"):
            os.makedirs("./logs")
        with open("./logs/missing_huc8.json", "w+") as f:
            f.write(json.dumps(list(missing_huc8), indent=2))

        print("Importing practices...")
        self.engine.execute("DROP INDEX IF EXISTS ix_practices_temp_id")

        all_practices.merge(
            calculated_columns,
            left_index=True,
            right_index=True,
        ).to_sql(
            "practices_temp",
            con=self.engine,
            index_label="id",
            dtype={
                "ancillary_benefits": sqlalchemy.types.JSON,
                "active_year": sqlalchemy.BIGINT,
            },
            if_exists="append",
        )

        self.engine.execute("DROP TABLE IF EXISTS practices")
        self.engine.execute("ALTER TABLE practices_temp RENAME TO practices")
