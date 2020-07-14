ENV = "development"

DEBUG = True

SECRET_KEY = "dev"

SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://localhost:5432/gltg_bmp"
SQLALCHEMY_TRACK_MODIFICATIONS = False

INIT_DB = {
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
