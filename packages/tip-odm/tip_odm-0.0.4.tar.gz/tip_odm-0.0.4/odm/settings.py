import dataclasses
import json
import os
import pathlib


@dataclasses.dataclass
class Settings:
    host: str
    port: int
    logLevel: str


settings: Settings | None = None


def get_settings():
    """
    Liest die Einstellungen aus der settings.json und gibt diese zurück
    :return: Einstellungen
    """

    global settings

    if settings is None:
        settings_file = "settings.json"
        if not os.path.exists(settings_file) or not os.path.isfile(settings_file):
            settings = Settings(host="0.0.0.0", port=8075, logLevel="INFO")

        if settings is None:
            with open(settings_file, "r") as file:
                json_data = json.load(file)

            settings = Settings(**json_data)

    return settings
