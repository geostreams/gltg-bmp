import json
import os
from functools import reduce

import geopandas as gpd
import pandas as pd
import sqlalchemy
from dotenv import load_dotenv
from geoalchemy2 import Geometry
from geoalchemy2 import WKTElement

load_dotenv()

CONFIG = {
    "database_uri": os.getenv("DATABASE_URI"),
    "boundaries": {"source": "./data/boundaries.xlsx"},
    "assumptions": {"source": "./data/assumptions.xlsx"},
    "practices": {
        "extra_input_args": {
            "io": "./resources/1_EQIP_CSP_319 Practices 2008_2017_2.3.1.xlsm",
            "sheet_name": "Practices Applied",
            "header": 1,
            "usecols": "A:M",
            "dtype": {
                "HUC 8": "str",
                "HUC 12": "str",
                "County Code": "str",
                "NRCS Practice Code": "str",
                "Applied Date": "Int64",
            },
        },
        "extra_output_args": {"if_exists": "replace"},
    },
    "huc8": {"source": "./resources/WBD_National_GDB/WBD_National_GDB.gdb"},
}


def clean_column_names(df: pd.DataFrame):
    return (
        df.columns.str.strip().str.lower().str.replace(" ", "_").str.replace("[()]", "")
    )


def get_states():
    print("Getting States...")
    source_file = CONFIG["boundaries"]["source"]
    states = pd.read_excel(
        source_file,
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

    return states.set_index(states["state"]).sort_index().drop("state", axis=1)


def get_huc8_meta():
    print("Getting HUC8 metadata...")
    source_file = CONFIG["boundaries"]["source"]
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
    return huc8_meta.set_index(huc8_meta["code"]).sort_index().drop("code", axis=1)


def get_assumptions():
    print("Getting assumptions...")
    source_file = CONFIG["assumptions"]["source"]
    assumptions = pd.read_excel(source_file, sheet_name="Practices", dtype="str")
    assumptions["wq"] = pd.to_numeric(assumptions["wq"]).astype("Int64")
    assumptions = (
        assumptions.set_index(assumptions["code"]).sort_index().drop("code", axis=1)
    )

    def join_json_columns(main: pd.DataFrame, sheet_info: (str, str)):
        (sheet_name, column_name) = sheet_info

        sheet = pd.read_excel(source_file, sheet_name=sheet_name, dtype="str")
        sheet = (
            sheet.set_index(sheet["code"]).sort_index().drop("code", axis=1).fillna("")
        )
        sheet[column_name] = sheet.apply(lambda row: row.to_dict(), axis=1)

        return main.join(sheet[column_name], on="code")

    return reduce(
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
    )


def get_practices():
    print("Getting practices...")
    practices = pd.read_excel(
        parse_dates=False, **CONFIG["practices"]["extra_input_args"]
    )
    practices.index += 1
    practices.columns = clean_column_names(practices)

    return practices


def update_practices(
    assumptions: pd.DataFrame,
    states: pd.DataFrame,
    huc8_meta: pd.DataFrame,
    practices: pd.DataFrame,
):
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

    for _, row in practices.iterrows():
        if row.nrcs_practice_code != "0":
            practice_assumptions = assumptions.loc[row.nrcs_practice_code]

            # Sunset
            practice_life_span = practice_assumptions["life_span"]
            if not pd.isna(practice_life_span):
                sunset.append(row.applied_date + int(practice_life_span[row.state]) - 1)
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
                            lambda benefit: practice_ancillary_benefits[benefit] == "1",
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

    with open("./logs/missing_huc8.json", "w") as f:
        f.write(json.dumps(list(missing_huc8), indent=2))

    return calculated_columns


def get_huc8_boundaries(practices: pd.DataFrame):
    print("Getting HUC8 boundaries...")
    huc8 = gpd.read_file(CONFIG["huc8"]["source"], layer="WBDHU8")
    huc8.to_crs("EPSG:4326", inplace=True)
    huc8.columns = clean_column_names(huc8)
    huc8.huc8 = huc8.huc8.astype(str)
    huc8.sort_values(by=["huc8"], inplace=True)
    huc8 = huc8[huc8["huc8"].isin(practices["huc_8"])][
        ["huc8", "name", "areaacres", "states", "geometry"]
    ]
    huc8["states"] = huc8["states"].apply(lambda x: x.split(","))
    huc8["geometry"] = huc8["geometry"].apply(
        lambda geom: WKTElement(geom.wkt, srid=4326)
    )
    huc8.set_index("huc8", inplace=True)

    return huc8


def import_data():
    print("Importing data...")
    states = get_states()
    huc8_meta = get_huc8_meta()
    assumptions = get_assumptions()
    practices = get_practices()
    practices = practices.merge(
        update_practices(assumptions, states, huc8_meta, practices),
        left_index=True,
        right_index=True,
    )
    huc8_boundaries = get_huc8_boundaries(practices)

    engine = sqlalchemy.create_engine(CONFIG["database_uri"])

    print("Importing states...")
    states.to_sql("states", con=engine, index_label="id", if_exists="replace")

    print("Importing assumptions...")
    assumptions.to_sql(
        "assumptions",
        con=engine,
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

    print("Importing practices...")
    practices.to_sql(
        "practices",
        con=engine,
        index_label="id",
        dtype={"ancillary_benefits": sqlalchemy.types.JSON},
        **CONFIG["practices"]["extra_output_args"]
    )

    print("Importing HUC8 boundaries...")
    huc8_boundaries.to_sql(
        "huc8",
        con=engine,
        if_exists="replace",
        dtype={
            "states": sqlalchemy.types.JSON,
            "geometry": Geometry("MultiPolygon", srid=4326),
        },
    )


if __name__ == "__main__":
    import_data()
