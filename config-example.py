ENV = "development"

DEBUG = True

SECRET_KEY = "dev"

SQLALCHEMY_DATABASE_URI = "localhost:5432/gltg_bmp"
SQLALCHEMY_TRACK_MODIFICATIONS = False

IMPORT_PARAMS = {
  "huc_8_column_name": "huc_8",
  "extra_input_args": {
    "io": "./data/1_EQIP_CSP_319 Practices 2008_2017_2.3.1.xlsm",
    "sheet_name": "Practices Applied",
    "header": 1,
    "usecols": "A:M",
    "dtype": {
      "HUC 8": "str",
      "HUC 12": "str"
    }
  },
  "extra_output_args": {
    "if_exists": "replace"
  }
}
