import datetime
from dotenv import dotenv_values
import enum
import luigi
from os import path
import psycopg


def get_conn():
    config = dotenv_values("../.env")
    connection = psycopg.connect(
        conninfo="postgresql://{0}:{1}@localhost:{2}/{3}".format(
            config.get("PGUSER"),
            config.get("PGPASSWORD"),
            config.get("PGPORT"),
            config.get("PGDATABASE"),
        )
    )
    return connection


class LangTag(enum.Enum):
    En = "en"
    Es = "es"
    De = "de"
    Fr = "fr"
    Zh = "zh"


def from_output_params(
    output_dir: str,
    extract_datetime: datetime.datetime,
    params: dict[str, str],
    ext: str,
):
    accumulate_filename = extract_datetime.strftime("%Y-%m-%dT%H%M%S%z")
    params_items = params.items()
    if len(params_items) > 0:
        joined_key_values = ["_".join([key, str(value)]) for key, value in params_items]
        joined_params = "__".join(joined_key_values)
        accumulate_filename = "__".join([accumulate_filename, joined_params])
    accumulate_filename = path.extsep.join([accumulate_filename, ext])
    output_path = path.join(output_dir, accumulate_filename)
    return luigi.LocalTarget(path=output_path)
