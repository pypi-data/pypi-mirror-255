import copy
import json
import logging
import pathlib
from typing import Literal

import pydantic

from camera_management.dataclasses.camera_dataclasses import CameraDescription, PreprocessingSettings


def check_preprocessing(settings: dict, old_settings: PreprocessingSettings) -> tuple[str, PreprocessingSettings]:
    """
    Checks a given PreprocessingSettings object in respect to another PreprocessingSettings object. Returns the new
    object if all type checks are successful, else returns the old object with no changes.

    :param settings: New PreprocessingSettings object to check.
    :param old_settings: Old PreprocessingSettings object to check against.
    :returns: The new PreprocessingSettings object if all type checks succeed, else the unchanged old
        PreprocessingSettings object.
    """
    new_settings = copy.deepcopy(old_settings)

    for key, value in settings.items():
        if key not in list(old_settings.model_fields.keys()):
            logging.warning(f"Tried to set the setting {key}. Allowed settings are {list(old_settings.model_fields.keys())}.")
            return f"Tried to set the setting {key}. Allowed settings are {list(old_settings.model_fields.keys())}.", old_settings

        if isinstance(value, dict):
            for k, v in value.items():
                if k not in list(getattr(old_settings, key).model_fields.keys()):
                    logging.warning(f"Tried to set the setting {k}. Allowed settings are {list(getattr(old_settings, key).model_fields.keys())}.")
                    return f"Tried to set the setting {k}. Allowed settings are {list(getattr(old_settings, key).model_fields.keys())}.", old_settings
                setattr(getattr(new_settings, key), k, v)
        else:
            setattr(new_settings, key, value)
    try:
        new_settings = PreprocessingSettings.model_validate(new_settings)
    except pydantic.ValidationError as e:
        logging.error(f"Camera Settings {new_settings} could not be validated and raised pydantic.ValidationError: {e}")
        return f"Camera Settings {new_settings} could not be validated and raised pydantic.ValidationError: {e}", old_settings

    return "SUCCESS", new_settings


def check_config(config: dict, mode: Literal["type", "individual"], config_path: str) -> pydantic.BaseModel | None:
    """
    Function, to check if a given config corresponds to the specifications.

    :param config: A configuration, can e.g. be created by json.load(<path_to_config>)
    :param mode: Flag to set if either a type or an individual calibration shall be used. Can be 'type' or 'individual'
    :param config_path: Path to the config file, only used for logging.
    :return: True if the config is valid, false if not
    """

    if mode == "type":
        try:
            config = CameraDescription.model_validate(config)
        except pydantic.ValidationError as e:
            logging.error(f"Config for {config_path} could not be validated and raised pydantic.ValidationError: {e}")
            return None

        if config.calibration.available and config.calibration.values is None:
            logging.warning(
                f'Key "calibration -> available" for {config_path} is set to true, but no calibration'
                f' data was found while looking for the key "values". Config will be ignored.'
            )
            return None
        return config

    if mode == "individual":
        try:
            config = CameraDescription.model_validate(config)
        except pydantic.ValidationError as e:
            logging.error(f"Config for {config_path} could not be validated and raised pydantic.ValidationError: {e}")
            return None

        if config.calibration.available and config.calibration.values is None:
            logging.warning(
                f'Key "calibration -> available" for {config_path} is set to true, but no calibration'
                f' data was found while looking for the key "values". Config will be ignored.'
            )
            return None
        if not config.calibration.available:
            logging.warning(
                f'Key "calibration -> available" is set to False for {config_path}. An individual calibration file must have calibration values.'
            )
        return config


def __rotate_file_bkup(filename: pathlib.Path, max_bkup=5):
    bkup_filename = filename.parent / f"{filename.name}.{max_bkup}"
    if bkup_filename.exists():
        # Delete latest bkup, which is "shifted out"
        bkup_filename.unlink()

    for i in range(max_bkup, 0, -1):
        if i > 1:
            bkup_filename = filename.parent / f"{filename.name}.{i-1}"
        else:
            bkup_filename = filename

        target_filename = filename.parent / f"{filename.name}.{i}"
        if bkup_filename.exists():
            bkup_filename.rename(target_filename)
            # print(f"Renaming {bkup_filename.name} -> {target_filename.name}")


def write_configuration_file(filename: str, content: dict, cam_config_path: pathlib.Path, max_bkup=4):
    """
    Write a configuration file to a given filepath while keeping the last files.

    :param filename: The filename of the file you want to save.
    :param content: The content you want to save.
    :param cam_config_path: The path to the "temp" folder.
    :param max_bkup: The maximum number of last config files you want to keep.
    """
    __rotate_file_bkup(cam_config_path / "configs" / filename, max_bkup)

    with open(cam_config_path / "configs" / filename, "w") as config_file:
        config_file.write(json.dumps(content, indent=4))
