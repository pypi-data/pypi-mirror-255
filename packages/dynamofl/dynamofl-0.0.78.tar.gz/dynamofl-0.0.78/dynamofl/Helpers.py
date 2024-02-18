"""
Utility methods
"""
# pylint: disable=invalid-name
import os
from itertools import product
from typing import Any, Dict, List, Union


class TrainArgs:
    """Utitlity class for training arguments"""

    def __init__(
        self,
        datasource_key=None,
        federated_model_path=None,
        new_model_path=None,
        project=None,
        project_info=None,
        hyper_param_values=None,
    ):
        self.datasource_key = datasource_key
        self.federated_model_path = federated_model_path
        self.new_model_path = new_model_path
        self.project = project
        self.project_info = project_info
        self.hyper_param_values = hyper_param_values


class TestArgs:
    """Utitlity class for testing arguments"""

    def __init__(self, datasource_key=None, federated_model_path=None, project_info=None):
        self.datasource_key = datasource_key
        self.federated_model_path = federated_model_path
        self.project_info = project_info


class FileUtils:
    @staticmethod
    def validate_file_extension(
        file_path: str, allowed_extensions: List[str], error_message_prefix: str = "File extension"
    ):
        _, file_extension = os.path.splitext(file_path)
        if file_extension not in allowed_extensions:
            raise ValueError(
                f"{error_message_prefix} {file_extension} not allowed. "
                f"Allowed extensions are {allowed_extensions}"
            )


class Helpers:
    """Utility class for helper methods"""

    @staticmethod
    def save_state_dict_tensorflow(model):
        state_dict = {}
        for index, layer in enumerate(model.layers):
            layer_class = model.layers[index].__class__.__name__
            raw_weights = model.layers[index].weights
            layer_weights = []
            for weight_tensors in raw_weights:
                layer_weights.append(weight_tensors.numpy())
            state_dict[layer.name] = [layer_class, layer_weights]
        return state_dict

    @staticmethod
    def load_state_dict_tensorflow(model, state_dict):
        for index, layer in enumerate(model.layers):
            raw_weights = model.layers[index].weights
            for index, weight_tensors in enumerate(raw_weights):
                weight_tensors.assign(state_dict[layer.name][1][index])

    @staticmethod
    def expand_grid_search(
        grid: List[Dict[str, List[Union[str, float, int]]]]
    ) -> List[Dict[str, Union[str, float, int]]]:
        hyper_parameters_combinations = []
        for grid_item in grid:
            # Generate all combinations of values from the grid
            value_combinations = list(product(*grid_item.values()))
            # Create a list of dictionaries representing each combination
            dict_combinations = [
                dict(zip(grid_item.keys(), values)) for values in value_combinations
            ]
            hyper_parameters_combinations.extend(dict_combinations)
        return hyper_parameters_combinations

    @staticmethod
    def construct_dict_filtering_none_values(**kwargs) -> Dict[str, Any]:
        payload = {key: value for key, value in kwargs.items() if value is not None}
        return payload


class URLUtils:
    """Utility class for URL related methods"""

    @staticmethod
    def get_ui_host_from_api_host(api_host):
        return api_host.replace("api.", "")

    @staticmethod
    def get_model_ui_url(api_host: str, model_id: str) -> str:
        ui_host = URLUtils.get_ui_host_from_api_host(api_host)
        return f"{ui_host}/model/{model_id}"

    @staticmethod
    def get_test_report_ui_url(api_host: str, test_id: str) -> str:
        ui_host = URLUtils.get_ui_host_from_api_host(api_host)
        return f"{ui_host}/report/{test_id}"
