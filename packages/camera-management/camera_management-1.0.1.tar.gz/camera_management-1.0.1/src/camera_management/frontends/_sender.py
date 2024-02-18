import dataclasses
import json

import requests

from . import types


def set_meas_config(url: str, config: types.MeasConfig):
    """
    INSERT USEFUL DESCRIPTION WHEN SEEING THIS
    """
    json_data = dataclasses.asdict(config)
    json_data = json.dumps(json_data)
    response = requests.post(url, data=json_data)
    print(response.text)


if __name__ == "__main__":
    test = types.MeasConfig()
    test.measure_flm = True

    set_meas_config("http://localhost:8090/config/meas", test)
