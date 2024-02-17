""" Configuration Singleton to live throughout the project's execution """

#  pylint:disable=attribute-defined-outside-init, import-error

import os
from copy import deepcopy
from pathlib import Path
from typing import List, Union

from omegaconf import DictConfig, ListConfig, OmegaConf


class ConfigurationParser:
    """.yaml configuration parser"""

    _PPCONF_KEY_PATTERN = "ppconf"
    _instance = None

    def __new__(cls, *args, **kwargs):
        """Ensure only one instance"""
        if not cls._instance:
            cls._instance = super(ConfigurationParser, cls).__new__(cls, *args, **kwargs)
            cls._instance._config = None
        return cls._instance

    def get_ppconfig(self):
        """Returns pplog's configuration parse from .yaml files"""
        if self._config is None:
            raise ValueError("Configuration not loaded. Call load_ppconfig() first.")
        return deepcopy(self._config)

    def load_parsed_config(self, parsed_config: dict) -> None:
        """Loads readily parsed config for ppconf to use - it will look for 'ppconf' key"""
        if parsed_config.get(self._PPCONF_KEY_PATTERN) is None:
            raise ValueError(
                'The provided readily parsed config does not have the "ppconf" key:'
                + f"\nExisting Keys: {parsed_config.keys()}"
            )

        if not parsed_config.get(self._PPCONF_KEY_PATTERN):
            raise ValueError('The provided parsed config\'s "ppconf" key has an empty value')

        #  pylint: disable-next=access-member-before-definition
        self._config = deepcopy(parsed_config.get(self._PPCONF_KEY_PATTERN))

    def load_ppconfig(self, config_folder: Path) -> None:
        """Loads pplog configuration from a specified folder pathlib.PosixPath object

        Args:
            config_folder (PosixPath): pplog .yml, .yaml, .json config files location

        Raises:
            FileNotFoundError: No configuration files found or incorrect path provided

        Returns:
            Union[ListConfig, DictConfig]: OmegaConf object - loaded configuration
        """
        # Search for the configuration file in the specified folder
        conf_files: List[Path] = []
        try:
            #  Get all file paths at location
            for root, _, files in os.walk(config_folder):
                conf_files.extend(Path(root).joinpath(file).resolve() for file in files)

            #  Omega load config
            loaded_conf_files: List[Union[DictConfig, ListConfig]] = [
                OmegaConf.load(file)
                for file in conf_files
                if file.suffix in [".yml", ".yaml", ".json"]
                and self._PPCONF_KEY_PATTERN in file.name
            ]

            if not loaded_conf_files:
                raise FileNotFoundError(f"No conf files found at {str(config_folder)}")

        except FileNotFoundError as exp:
            raise FileNotFoundError(
                f"Configuration path {str(config_folder)} provided is not correct.",
            ) from exp

        #  pylint: disable-next=access-member-before-definition
        self._config = OmegaConf.merge(*loaded_conf_files)


#  Set singleton instance and pre-bound methods
_ppconfig_instance = ConfigurationParser()
load_ppconfig = _ppconfig_instance.load_ppconfig
load_parsed_config = _ppconfig_instance.load_parsed_config
get_ppconfig = _ppconfig_instance.get_ppconfig
