import json
import os
from enum import Enum
from pathlib import Path
from typing import Dict


class RunMode(Enum):
    SIMULATION = "simulation",
    ANALYSIS = "analysis"


class FCRType(Enum):
    BIOMETRICS = 1,
    ASSAF = 2


class Config:
    """
    This class is used to access configuration.
    """

    def __init__(self,
                 run_type: RunMode = RunMode.SIMULATION,
                 fcr_type: FCRType = FCRType.BIOMETRICS,
                 n_members_in_cluster: int = 2,
                 n_competing_risks: int = 2,
                 n_clusters: int = 500,
                 uniform: bool = True,
                 n_bootstrap: int = 3,
                 thresholds_cumulative_hazards: list = [0.1, 0.15, 0.20, 0.25],
                 calculate_event_types: bool = False,
                 n_simulations: int = 3,
                 beta_coefficients: list = [0.5, 2.5],
                 frailty_mean: list = [0, 0],
                 frailty_covariance: list = [[1, 0.5], [0.5, 1.5]],
                 has_censoring: bool = True,
                 n_covariates: int = None,
                 data_path: Path = None):
        self.run_type = run_type
        self.fcr_type = fcr_type
        self.n_members_in_cluster = n_members_in_cluster
        self.n_competing_risks = n_competing_risks
        self.n_clusters = n_clusters
        self.uniform = uniform
        self.bootstrap = n_bootstrap
        self.thresholds_cumulative_hazards = thresholds_cumulative_hazards
        self.calculate_event_types = calculate_event_types

        if self.run_type == RunMode.SIMULATION:
            self.n_simulations = n_simulations
            self.beta_coefficients = beta_coefficients
            self.frailty_mean = frailty_mean
            self.frailty_covariance = frailty_covariance
            self.has_censoring = has_censoring

        elif self.run_type == RunMode.ANALYSIS.value[0]:
            self.n_covariates = n_covariates
            self.data_path = data_path

    @staticmethod
    def _get_config_dict_from_json(config_folder_path: Path, run_type: str) -> Dict[str, object]:
        config_file_path = config_folder_path / f"config.{run_type}.json"
        with config_file_path.open() as config_file:
            values = json.load(config_file)
        return values

    @staticmethod
    def _validate_mode_name(run_type: str) -> None:
        if run_type not in ['simulation', 'analysis']:
            raise Exception('env_name must be simulation or analysis')

    @staticmethod
    def print_configs(configs: Dict[str, object]) -> None:
        for config, value in configs.items():
            print(config, ": ", value)
