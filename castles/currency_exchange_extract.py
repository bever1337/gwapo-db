import csv
import datetime
import enum
import jsonschema
import json
import luigi
import os
import requests

from tasks import config


class Atob(enum.Enum):
    Coins = "coins"
    Gems = "gems"


class ExtractCurrencyExchange(luigi.Task):
    atob = luigi.EnumParameter(enum=Atob)
    url = "https://api.guildwars2.com/v2/commerce/exchange/"
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "currency_exchange"

    def output(self):
        gwapo_config = config.gconfig()
        return luigi.LocalTarget(
            path=os.path.join(
                str(gwapo_config.output_dir),
                self.get_task_family(),
                os.path.extsep.join([self.task_id, "csv"]),
            )
        )

    def run(self):
        self_atob: Atob = self.atob  # type: ignore
        self_task_datetime: datetime.datetime = self.task_datetime  # type: ignore
        if self_atob == Atob.Coins:
            gold = [500, 250, 100, 50, 10]
            copper = [quantity * 10000 for quantity in gold]
            quantities = copper
        elif self_atob == Atob.Gems:
            gems = [1600, 800, 400, 100, 25]
            quantities = gems
        else:
            raise RuntimeError("Invalid atob inputs")

        with open(
            str("./schema/gw2/v2/commerce/exchange/" + self_atob.value + ".json")
        ) as json_schema_file:
            json_schema = json.load(fp=json_schema_file)
        validator = jsonschema.Draft202012Validator(schema=json_schema)

        with self.output().open("w") as write_target:
            fieldnames = ["coin", "coins", "coins_per_gem", "gem", "gems", "recorded"]
            csv_writer = csv.DictWriter(
                f=write_target, dialect="unix", fieldnames=fieldnames
            )
            csv_writer.writeheader()

            for quantity in quantities:
                response = requests.get(
                    url=str(self.url + self_atob.value),
                    params=dict({"quantity": quantity}),
                )
                if response.status_code != 200:
                    raise RuntimeError("Expected status code 200")
                response_json = response.json()
                validator.validate(response_json)

                if self.atob == Atob.Coins:
                    entity = dict(
                        {
                            "coin": 1,
                            "coins": quantity,
                            "coins_per_gem": response_json["coins_per_gem"],
                            "gem": 4,
                            "gems": response_json["quantity"],
                            "recorded": self_task_datetime.isoformat(),
                        }
                    )
                elif self.atob == Atob.Gems:
                    entity = dict(
                        {
                            "coin": 1,
                            "coins": response_json["quantity"],
                            "coins_per_gem": response_json["coins_per_gem"],
                            "gem": 4,
                            "gems": quantity,
                            "recorded": self_task_datetime.isoformat(),
                        }
                    )
                csv_writer.writerow(entity)
