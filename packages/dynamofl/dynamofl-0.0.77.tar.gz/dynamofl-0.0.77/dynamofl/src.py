"""
User facing methods on the dfl object of core sdk
"""

import logging
from typing import Dict, List, Union

from .attacks import pii_extraction
from .datasets.dataset import Dataset
from .datasets.hf_dataset import HFDataset
from .entities.dataset import HFDatasetEntity
from .entities.model import LocalModelEntity, RemoteModelEntity
from .entities.test import TestEntity
from .Helpers import Helpers, URLUtils
from .logging import set_logger
from .MessageHandler import _MessageHandler
from .models import local_model, remote_model
from .State import _State
from .tests.gpu_config import GPUSpecification
from .tests.test import Test
from .vector_db import ChromaDB, LlamaIndexDB, LlamaIndexWithChromaDB

try:
    from typing import Optional
except ImportError:
    from typing_extensions import Optional


RETRY_AFTER = 5  # seconds


class DynamoFL:
    """Creates a client instance that communicates with the API through REST and websockets.

    Args:
        token - Your auth token. Required.

        host - API server url. Defaults to DynamoFL prod API.

        metadata - Sets a default metadata object for attach_datasource calls; can be overriden.

        log_level - Set the log_level for the client.
            Accepts all of logging._Level. Defaults to logging.INFO.
    """

    def __init__(
        self,
        token: str,
        host: str = "https://api.dynamofl.com",
        metadata: object = None,
        log_level=logging.INFO,
        bi_directional_client=True,
    ):
        self._state = _State(token, host, metadata=metadata)
        if bi_directional_client:
            self._messagehandler = _MessageHandler(self._state)
            self._messagehandler.connect_to_ws()

        set_logger(log_level=log_level)

    def attach_datasource(self, key, train=None, test=None, name=None, metadata=None):
        return self._state.attach_datasource(
            key, train=train, test=test, name=name, metadata=metadata
        )

    def delete_datasource(self, key):
        return self._state.delete_datasource(key)

    def get_datasources(self):
        return self._state.get_datasources()

    def delete_project(self, key):
        return self._state.delete_project(key)

    def get_user(self):
        return self._state.get_user()

    def create_project(
        self,
        base_model_path,
        params,
        dynamic_trainer_key=None,
        dynamic_trainer_path=None,
    ):
        return self._state.create_project(
            base_model_path,
            params,
            dynamic_trainer_key=dynamic_trainer_key,
            dynamic_trainer_path=dynamic_trainer_path,
        )

    def get_project(self, project_key):
        return self._state.get_project(project_key)

    def get_projects(self):
        return self._state.get_projects()

    def is_datasource_labeled(self, project_key=None, datasource_key=None):
        """
        Accepts a valid datasource_key and project_key
        Returns True if the datasource is labeled for the project; False otherwise

        """
        return self._state.is_datasource_labeled(
            project_key=project_key, datasource_key=datasource_key
        )

    def upload_dynamic_trainer(self, dynamic_trainer_key, dynamic_trainer_path):
        return self._state.upload_dynamic_trainer(dynamic_trainer_key, dynamic_trainer_path)

    def download_dynamic_trainer(self, dynamic_trainer_key):
        return self._state.download_dynamic_trainer(dynamic_trainer_key)

    def delete_dynamic_trainer(self, dynamic_trainer_key):
        return self._state.delete_dynamic_trainer(dynamic_trainer_key)

    def get_dynamic_trainer_keys(self):
        return self._state.get_dynamic_trainer_keys()

    def create_attack(self):
        return pii_extraction.PIIExtraction(self._state.request)

    def create_test(
        self,
        name: str,
        model_key: str,
        dataset_id: str,
        test_type: str,
        gpu: GPUSpecification,
        config: list,
        api_key=None,
    ) -> TestEntity:
        return Test.create_test(
            request=self._state.request,
            name=name,
            model_key=model_key,
            dataset_id=dataset_id,
            test_type=test_type,
            gpu=gpu,
            config=config,
            api_key=api_key,
        )

    def create_performance_test(  # pylint: disable=dangerous-default-value
        self,
        name: str,
        model_key: str,
        dataset_id: str,
        gpu: GPUSpecification,
        performance_metrics: List[str],
        input_column: str,
        topic_list: Optional[List[str]] = None,
        prompts_column: Optional[str] = None,
        reference_column: Optional[str] = None,
        hf_token: Optional[str] = None,
        api_key: Optional[str] = None,
        grid: List[Dict[str, List[Union[str, float, int]]]] = [{}],
    ) -> TestEntity:
        """Creates a performance test on a model with a dataset

        Args:
            name (str): Name of the test
            model_key (str): Key of the model to be tested
            dataset_id (str): Id of the dataset to be used
            gpu (GPUSpecification): GPU specification
            performance_metrics (List[str]): Performance evaluation metrics used.
                E.g rouge, bertscore
            hf_token (Optional[str]): Huggingface token to use for the attack
            api_key (Optional[str]): API Key to use in case of remote models. Ignore this, if
                model was created using create_openai_model or create_azure_openai_model and
                you already supplied the api_key in the model creation
            input_column (str): Input column in the dataset to use for performance evaluation
            topic_list (Optional[List[str]]): List of topics to cluster the result
            prompts_column (Optional[str]): Column to specify the prompts for the input
            reference_column (Optional[str]): Column to specify the reference for the input
            grid (List[Dict[str, List[str |  float  |  int]]]): Grid of hyper parameters

        Returns:
            TestEntity: TestEntity object
        """
        common_attack_config = {
            "attack": Helpers.construct_dict_filtering_none_values(
                performance_metrics=performance_metrics,
                hf_token=hf_token,
            ),
            "dataset": Helpers.construct_dict_filtering_none_values(
                topic_list=topic_list,
                prompts_column_name=prompts_column,
                mia_input_text_column_name=input_column,
                mia_target_text_column_name=reference_column,
            ),
            "model": Helpers.construct_dict_filtering_none_values(
                api_key=api_key,
            ),
        }

        return Test.create_test_with_grid(
            common_attack_config=common_attack_config,
            grid=grid,
            request=self._state.request,
            name=name,
            model_key=model_key,
            dataset_id=dataset_id,
            test_type="perf-test",
            gpu=gpu,
        )

    def create_membership_inference_test(  # pylint: disable=dangerous-default-value
        self,
        name: str,
        model_key: str,
        dataset_id: str,
        gpu: GPUSpecification,
        input_column: str,
        hf_token: Optional[str] = None,
        api_key: Optional[str] = None,
        prompts_column: Optional[str] = None,
        reference_column: Optional[str] = None,
        base_model: Optional[str] = None,
        pii_classes: Optional[List[str]] = None,
        regex_expressions: Optional[Dict[str, str]] = None,
        grid: List[Dict[str, List[Union[str, float, int]]]] = [{}],
    ) -> TestEntity:
        """Create a membership inference test on a model with a dataset

        Args:
            name (str): Name of the test
            model_key (str): Key of the model to be tested
            dataset_id (str): Id of the dataset to be used
            gpu (GPUSpecification): GPU specification
            hf_token (Optional[str]): Huggingface token to use for the attack
            api_key (Optional[str]): API Key to use in case of remote models. Ignore this, if
                model was created using create_openai_model or create_azure_openai_model and
                you already su
            input_column (str): Input column in the dataset to use for performance evaluation
            prompts_column (Optional[str]): Column to specify the prompts for the input
            reference_column (Optional[str]): Column to specify the reference for the input
            base_model (Optional[str]): Base model to use for the attack
            pii_classes (Optional[List[str]]): PII classes to attack. E.g PERSON
            regex_expressions (Optional[Dict[str, str]]): list of regex expressions to use
                for extraction
            grid (List[Dict[str, List[str |  float  |  int]]]): Grid of hyper parameters

        Returns:
            TestEntity: TestEntity object
        """
        common_attack_config = {
            "attack": Helpers.construct_dict_filtering_none_values(
                hf_token=hf_token,
                pii_classes=pii_classes,
                regex_expressions=regex_expressions,
            ),
            "model": Helpers.construct_dict_filtering_none_values(
                base_model=base_model,
                api_key=api_key,
            ),
            "dataset": Helpers.construct_dict_filtering_none_values(
                prompts_column_name=prompts_column,
                mia_input_text_column_name=input_column,
                mia_target_text_column_name=reference_column,
            ),
        }

        return Test.create_test_with_grid(
            common_attack_config=common_attack_config,
            grid=grid,
            request=self._state.request,
            name=name,
            model_key=model_key,
            dataset_id=dataset_id,
            test_type="membership_inference",
            gpu=gpu,
        )

    def create_hallucination_test(  # pylint: disable=dangerous-default-value
        self,
        name: str,
        model_key: str,
        dataset_id: str,
        gpu: GPUSpecification,
        hallucination_metrics: List[str],
        input_column: str,
        topic_list: Optional[List[str]] = None,
        hf_token: Optional[str] = None,
        api_key: Optional[str] = None,
        prompts_column: Optional[str] = None,
        reference_column: Optional[str] = None,
        grid: List[Dict[str, List[Union[str, float, int]]]] = [{}],
    ) -> TestEntity:
        """Create a hallucination test on a model with a dataset

        Args:
            name (str): Name of the test
            model_key (str): Key of the model to be tested
            dataset_id (str): Id of the dataset to be used
            gpu (GPUSpecification): GPU specification
            hallucation_metrics (List[str]): Hallucation metrics used. E.g
                nli-consistency, unieval-factuality
            topic_list (Optional[List[str]]): List of topics to cluster the result
            hf_token (Optional[str]): Huggingface token to use for the attack
            api_key (Optional[str]): API Key to use in case of remote models. Ignore this, if
                model was created using create_openai_model or create_azure_openai_model and
                you already su
            input_column (str): Input column in the dataset to use for performance evaluation
            prompts_column (Optional[str]): Column to specify the prompts for the input
            reference_column (Optional[str]): Column to specify the reference for the input
            grid (List[Dict[str, List[str |  float  |  int]]]): Grid of hyper parameters

        Returns:
            TestEntity: TestEntity object
        """
        common_attack_config = {
            "attack": Helpers.construct_dict_filtering_none_values(
                hallucination_metrics=hallucination_metrics,
                hf_token=hf_token,
            ),
            "dataset": Helpers.construct_dict_filtering_none_values(
                topic_list=topic_list,
                prompts_column_name=prompts_column,
                mia_input_text_column_name=input_column,
                mia_target_text_column_name=reference_column,
            ),
            "model": Helpers.construct_dict_filtering_none_values(
                api_key=api_key,
            ),
        }

        return Test.create_test_with_grid(
            common_attack_config=common_attack_config,
            grid=grid,
            request=self._state.request,
            name=name,
            model_key=model_key,
            dataset_id=dataset_id,
            test_type="hallucination-test",
            gpu=gpu,
        )

    def create_pii_extraction_test(  # pylint: disable=dangerous-default-value
        self,
        name: str,
        model_key: str,
        dataset_id: str,
        gpu: GPUSpecification,
        pii_ref_column: str,
        hf_token: Optional[str] = None,
        api_key: Optional[str] = None,
        pii_classes: Optional[List[str]] = None,
        extraction_prompt: Optional[str] = None,
        sampling_rate: Optional[float] = None,
        regex_expressions: Optional[Dict[str, str]] = None,
        prompts_column: Optional[str] = None,
        grid: List[Dict[str, List[Union[str, float, int]]]] = [{}],
    ) -> TestEntity:
        """Create a pii extraction test on a model with a dataset

        Args:
            name (str): Name of the test
            model_key (str): Key of the model to be tested
            dataset_id (str): Id of the dataset to be used
            gpu (GPUSpecification): GPU specification
            hf_token (Optional[str]): Huggingface token to use for the attack
            api_key (Optional[str]): API Key to use in case of remote models. Ignore this, if
                model was created using create_openai_model or create_azure_openai_model and
                you already su
            pii_classes (Optional[List[str]]): PII classes to attack. E.g PERSON
            extraction_prompt (Optional[str]): Prompt or for PII extraction.
            sampling_rate (Optional[float]): Number of times to attempt generating candidates.
            regex_expressions (Optional[Dict[str, str]]): list of regex expressions to use
                for extraction
            pii_ref_column (str): Column in the dataset to sample prompts from
            prompts_column (Optional[str]): Column to specify the prompts for the input
            grid (List[Dict[str, List[str |  float  |  int]]]): Grid of hyper parameters

        Returns:
            TestEntity: TestEntity object
        """

        common_attack_config = {
            "attack": Helpers.construct_dict_filtering_none_values(
                hf_token=hf_token,
                pii_classes=pii_classes,
                extraction_prompt=extraction_prompt,
                sampling_rate=sampling_rate,
                regex_expressions=regex_expressions,
            ),
            "dataset": Helpers.construct_dict_filtering_none_values(
                column_name=pii_ref_column, prompts_column_name=prompts_column
            ),
            "model": Helpers.construct_dict_filtering_none_values(
                api_key=api_key,
            ),
        }

        return Test.create_test_with_grid(
            common_attack_config=common_attack_config,
            grid=grid,
            request=self._state.request,
            name=name,
            model_key=model_key,
            dataset_id=dataset_id,
            test_type="pii_extraction",
            gpu=gpu,
        )

    def create_pii_inference_test(  # pylint: disable=dangerous-default-value
        self,
        name: str,
        model_key: str,
        dataset_id: str,
        gpu: GPUSpecification,
        pii_ref_column: str,
        hf_token: Optional[str] = None,
        api_key: Optional[str] = None,
        pii_classes: Optional[List[str]] = None,
        num_targets: Optional[int] = None,
        candidate_size: Optional[int] = None,
        regex_expressions: Optional[Dict[str, str]] = None,
        prompts_column: Optional[str] = None,
        sample_and_shuffle: Optional[int] = None,
        grid: List[Dict[str, List[Union[str, float, int]]]] = [{}],
    ) -> TestEntity:
        """Create a pii inference test on a model with a dataset

        Args:
            name (str): Name of the test
            model_key (str): Key of the model to be tested
            dataset_id (str): Id of the dataset to be used
            gpu (GPUSpecification): GPU specification
            hf_token (Optional[str]): Huggingface token to use for the attack
            api_key (Optional[str]): API Key to use in case of remote models. Ignore this, if
                model was created using create_openai_model or create_azure_openai_model and
                you already su
            pii_classes (Optional[List[str]]): PII classes to attack. E.g PERSON
            num_targets (int): Number of target sequence to sample to attack
            candidate_size (int): Number of PII candidates to sample randomly for the attack.
            regex_expressions (Optional[Dict[str, str]]): list of regex expressions to use
                for extraction
            pii_ref_column (str): Column in the dataset to sample prompts from
            prompts_column (Optional[str]): Column to specify the prompts for the input
            sample_and_shuffle (int): number of times to sample and shuffle candidates
            grid (List[Dict[str, List[str |  float  |  int]]]): Grid of hyper parameters

        Returns:
            TestEntity: TestEntity object
        """
        common_attack_config = {
            "attack": Helpers.construct_dict_filtering_none_values(
                hf_token=hf_token,
                pii_classes=pii_classes,
                num_targets=num_targets,
                candidate_size=candidate_size,
                regex_expressions=regex_expressions,
                sample_and_shuffle=sample_and_shuffle,
            ),
            "dataset": Helpers.construct_dict_filtering_none_values(
                column_name=pii_ref_column, prompts_column_name=prompts_column
            ),
            "model": Helpers.construct_dict_filtering_none_values(
                api_key=api_key,
            ),
        }

        return Test.create_test_with_grid(
            common_attack_config=common_attack_config,
            grid=grid,
            request=self._state.request,
            name=name,
            model_key=model_key,
            dataset_id=dataset_id,
            test_type="pii_inference",
            gpu=gpu,
        )

    def create_pii_reconstruction_test(  # pylint: disable=dangerous-default-value
        self,
        name: str,
        model_key: str,
        dataset_id: str,
        gpu: GPUSpecification,
        pii_ref_column: str,
        hf_token: Optional[str] = None,
        api_key: Optional[str] = None,
        pii_classes: Optional[List[str]] = None,
        num_targets: Optional[int] = None,
        candidate_size: Optional[int] = None,
        sampling_rate: Optional[float] = None,
        regex_expressions: Optional[Dict[str, str]] = None,
        prompts_column: Optional[str] = None,
        grid: List[Dict[str, List[Union[str, float, int]]]] = [{}],
    ) -> TestEntity:
        """Create a pii reconstruction test on a model with a dataset

        Args:
            name (str): Name of the test
            model_key (str): Key of the model to be tested
            dataset_id (str): Id of the dataset to be used
            gpu (GPUSpecification): GPU specification
            hf_token (Optional[str]): Huggingface token to use for the attack
            api_key (Optional[str]): API Key to use in case of remote models. Ignore this, if
                model was created using create_openai_model or create_azure_openai_model and
                you already su
            pii_classes (Optional[List[str]]): PII classes to attack. E.g PERSON
            num_targets (int): Number of target sequence to sample to attack
            candidate_size (int): Number of PII candidates to sample randomly for the attack.
            sampling_rate (Optional[float]): Number of times to attempt generating candidates.
            regex_expressions (Optional[Dict[str, str]]): list of regex expressions to use
                for extraction
            pii_ref_column (str): Column in the dataset to sample prompts from
            prompts_column (Optional[str]): Column to specify the prompts for the input
            grid (List[Dict[str, List[str |  float  |  int]]]): Grid of hyper parameters

        Returns:
            TestEntity: TestEntity object
        """
        common_attack_config = {
            "attack": Helpers.construct_dict_filtering_none_values(
                hf_token=hf_token,
                pii_classes=pii_classes,
                num_targets=num_targets,
                candidate_size=candidate_size,
                sampling_rate=sampling_rate,
                regex_expressions=regex_expressions,
            ),
            "dataset": Helpers.construct_dict_filtering_none_values(
                column_name=pii_ref_column, prompts_column_name=prompts_column
            ),
            "model": Helpers.construct_dict_filtering_none_values(
                api_key=api_key,
            ),
        }

        return Test.create_test_with_grid(
            common_attack_config=common_attack_config,
            grid=grid,
            request=self._state.request,
            name=name,
            model_key=model_key,
            dataset_id=dataset_id,
            test_type="pii_reconstruction",
            gpu=gpu,
        )

    def create_rag_hallucination_test(  # pylint: disable=dangerous-default-value
        self,
        name: str,
        model_key: str,
        dataset_id: str,
        gpu: GPUSpecification,
        rag_hallucination_metrics: List[str],
        input_column: str,
        example_column: Optional[str] = None,
        topic_list: Optional[List[str]] = None,
        hf_token: Optional[str] = None,
        api_key: Optional[str] = None,
        prompts_column: Optional[str] = None,
        prompt_template: Optional[str] = None,
        vector_db: Optional[Union[ChromaDB, LlamaIndexDB, LlamaIndexWithChromaDB]] = None,
        grid: List[Dict[str, List[Union[str, float, int]]]] = [{}],
    ) -> TestEntity:
        """Create a rag hallucination test on a model with a dataset

        Args:
            name (str): Name of the test
            model_key (str): Key of the model to be tested
            dataset_id (str): Id of the dataset to be used
            gpu (GPUSpecification): GPU specification
            rag_hallucation_metrics (List[str]): Rag hallucination metrics used. E.g
                nli-consistency, unieval-factuality
            topic_list (Optional[List[str]]): List of topics to cluster the result
            hf_token (Optional[str]): Huggingface token to use for the attack
            api_key (Optional[str]): API Key to use in case of remote models. Ignore this, if
                model was created using create_openai_model or create_azure_openai_model and
                you already su
            input_column (str): Input column in the dataset to use for rag hallucination evaluation
            example_column (Optional[str]): Example column used for few shot examples
            prompts_column (Optional[str]): Column to specify the prompts for the input
            prompt_template (Optional[str]): Prompt template to use for the attack
            vector_db (Optional[Union[ChromaDB, LlamaIndexDB, LlamaIndexWithChromaDB]]):
                Vector db to use for the attack

        Returns:
            TestEntity: TestEntity object
        """
        common_attack_config = {
            "attack": Helpers.construct_dict_filtering_none_values(
                hf_token=hf_token,
                rag_hallucination_metrics=rag_hallucination_metrics,
            ),
            "dataset": Helpers.construct_dict_filtering_none_values(
                topic_list=topic_list,
                prompt_template=prompt_template,
                prompts_column_name=prompts_column,
                mia_input_text_column_name=input_column,
                example_text_column_name=example_column,
                vector_db=vector_db.__dict__,
            ),
            "model": Helpers.construct_dict_filtering_none_values(
                api_key=api_key,
            ),
        }

        return Test.create_test_with_grid(
            common_attack_config=common_attack_config,
            grid=grid,
            request=self._state.request,
            name=name,
            model_key=model_key,
            dataset_id=dataset_id,
            test_type="rag-hallucination-test",
            gpu=gpu,
        )

    def create_sequence_extraction_test(  # pylint: disable=dangerous-default-value
        self,
        name: str,
        model_key: str,
        dataset_id: str,
        gpu: GPUSpecification,
        memorization_granularity: str,
        sampling_rate: int,
        is_finetuned: bool,
        title: Optional[str] = None,
        title_column: Optional[str] = None,
        text_column: Optional[str] = None,
        source: Optional[str] = None,
        api_key: Optional[str] = None,
        hf_token: Optional[str] = None,
        grid: List[Dict[str, List[Union[str, float, int]]]] = [{}],
    ) -> TestEntity:
        """Create a sequence extraction test on a model with a dataset

        Args:
            name (str): Name of the test
            model_key (str): Key of the model to be tested
            dataset_id (str): Id of the dataset to be used
            gpu (GPUSpecification): GPU specification
            memorization_granularity (str): Granularity of memorization. E.g paragraph, sentence
            sampling_rate (int): Number of times to attempt generating candidates.
            is_finetuned (bool): Whether the model is finetuned or not; determines
                whether to generate the fine-tuned or the base model report
            title (Optional[str]): Title to use for the attack
            title_column (Optional[str]): Title column to use for the attack
            text_column (Optional[str]): Text column to use for the attack
            source (Optional[str]): Source of the dataset, e.g. NYT
            api_key (Optional[str]): API Key to use in case of remote models. Ignore this, if
                model was created using create_openai_model or create_azure_openai_model
            hf_token (Optional[str]): Huggingface token to use for the attack

        Returns:
            TestEntity: TestEntity object
        """
        common_attack_config = {
            "attack": Helpers.construct_dict_filtering_none_values(
                hf_token=hf_token,
                memorization_granularity=memorization_granularity,
                sampling_rate=sampling_rate,
                source=source,
                is_finetuned=is_finetuned,
            ),
            "dataset": Helpers.construct_dict_filtering_none_values(
                title=title,
                title_column=title_column,
                text_column=text_column,
            ),
            "model": Helpers.construct_dict_filtering_none_values(
                api_key=api_key,
            ),
        }

        return Test.create_test_with_grid(
            common_attack_config=common_attack_config,
            grid=grid,
            request=self._state.request,
            name=name,
            model_key=model_key,
            dataset_id=dataset_id,
            test_type="sequence_extraction",
            gpu=gpu,
        )

    def create_mitre_test(  # pylint: disable=dangerous-default-value
        self,
        name: str,
        model_key: str,
        dataset_id: str,
        gpu: GPUSpecification,
        grid: List[Dict[str, List[Union[str, float, int]]]] = [{}],
    ) -> TestEntity:
        """Create a sequence extraction test on a model with a dataset

        Args:
            name (str): Name of the test
            model_key (str): Key of the model to be tested
            dataset_id (str): Id of the dataset to be used
            gpu (GPUSpecification): GPU specification
            api_key (Optional[str]): API Key to use in case of remote models. Ignore this, if
                model was created using create_openai_model or create_azure_openai_model

        Returns:
            TestEntity: TestEntity object
        """
        common_attack_config = {
            "attack": Helpers.construct_dict_filtering_none_values(),
            "dataset": Helpers.construct_dict_filtering_none_values(),
            "model": Helpers.construct_dict_filtering_none_values(),
        }

        return Test.create_test_with_grid(
            common_attack_config=common_attack_config,
            grid=grid,
            request=self._state.request,
            name=name,
            model_key=model_key,
            dataset_id=dataset_id,
            test_type="mitre",
            gpu=gpu,
        )

    def create_rag_test(
        self,
        name: str,
        model_key: str,
        dataset_id: str,
        gpu: GPUSpecification,
        prompt_template: str,
        config: list,
        vector_db: Union[ChromaDB, LlamaIndexDB, LlamaIndexWithChromaDB],
        retrieve_top_k: int,
        rag_hallucination_metrics: list[str],
        api_key=None,
    ) -> TestEntity:
        for c in config:
            for wrapper in ["attack", "dataset", "hyper_parameters"]:
                if wrapper not in c:
                    c[wrapper] = {}
            c["dataset"]["prompt_template"] = prompt_template
            c["attack"]["rag_hallucination_metrics"] = rag_hallucination_metrics
            c["hyper_parameters"]["retrieve_top_k"] = retrieve_top_k
            c["dataset"]["vector_db"] = vector_db.__dict__

        return self.create_test(
            name, model_key, dataset_id, "rag-hallucination-test", gpu, config, api_key
        )

    def get_use_cases(self):
        self._state.get_use_cases()

    def get_test_info(self, test_id: str):
        return self._state.get_test_info(test_id)

    def get_test_report_url(self, test_id: str):
        return URLUtils.get_test_report_ui_url(self._state.host, test_id)

    def get_attack_info(self, attack_id: str):
        return self._state.get_attack_info(attack_id)

    def get_datasets(self):
        self._state.get_datasets()

    def create_centralized_project(
        self,
        name,
        datasource_key,
        rounds=None,
        use_case_key=None,
        use_case_path=None,
    ):
        self._state.create_centralized_project(
            name,
            datasource_key,
            rounds=rounds,
            use_case_key=use_case_key,
            use_case_path=use_case_path,
        )

    def create_model(
        self,
        name: str,
        config: object,
        model_file_path: Optional[str] = None,
        model_file_paths: Optional[List[str]] = None,
        checkpoint_json_file_path: Optional[str] = None,
        architecture: Optional[str] = None,
        key: Optional[str] = None,
        peft_config_path: Optional[str] = None,
    ):
        return local_model.LocalModel.create_and_upload(
            request=self._state.request,
            name=name,
            key=key,
            model_file_path=model_file_path,
            model_file_paths=model_file_paths,
            checkpoint_json_file_path=checkpoint_json_file_path,
            architecture=architecture,
            config=config,
            peft_config_path=peft_config_path,
        )

    def create_remote_model(
        self,
        name: str,
        api_provider: str,
        api_instance: str,
        key: str,
        endpoint: Optional[str] = None,
    ):
        return remote_model.RemoteModel.create_and_upload(
            request=self._state.request,
            name=name,
            key=key,
            api_provider=api_provider,
            api_instance=api_instance,
            endpoint=endpoint,
        )

    def create_azure_openai_model(
        self,
        name: str,
        api_instance: str,
        api_key: str,
        api_version: str,
        model_endpoint: str,
        key: str,
    ) -> RemoteModelEntity:
        """Creates azure openai model

        Args:
            name (str): Name of the model to be created
            api_instance (str): Azure openai api instance
            api_key (str): Azure openai api key
            api_version (str): Azure openai api version
            model_endpoint (str): Azure openai model endpoint to use
            key (str): Unique key for the model

        Returns:
            RemoteModelEntity: RemoteModelEntity object
        """
        return remote_model.RemoteModel.create_azure_openai_model(
            request=self._state.request,
            name=name,
            api_instance=api_instance,
            api_key=api_key,
            api_version=api_version,
            model_endpoint=model_endpoint,
            key=key,
        )

    def create_openai_model(
        self,
        name: str,
        api_instance: str,
        api_key: str,
        key: str,
    ) -> RemoteModelEntity:
        """Creates openai model

        Args:
            name (str): Name of the model to be created
            api_instance (str): OpenAI api instance
            api_key (str): OpenAI api key
            key (str): Unique key for the model

        Returns:
            RemoteModelEntity: RemoteModelEntity object
        """
        return remote_model.RemoteModel.create_openai_model(
            request=self._state.request,
            name=name,
            api_instance=api_instance,
            api_key=api_key,
            key=key,
        )

    def create_databricks_model(
        self,
        name: str,
        api_key: str,
        model_endpoint: str,
        key: str,
    ) -> RemoteModelEntity:
        """Creates azure openai model

        Args:
            name (str): Name of the model to be created
            api_key (str): Databricks api token
            model_endpoint (str): Databricks model endpoint to use
            key (str): Unique key for the model

        Returns:
            RemoteModelEntity: RemoteModelEntity object
        """
        return remote_model.RemoteModel.create_databricks_model(
            request=self._state.request,
            name=name,
            api_key=api_key,
            model_endpoint=model_endpoint,
            key=key,
        )

    def create_hf_model(
        self,
        name: str,
        hf_hub_id: str,
        hf_token: str,
        key: Optional[str],
        architecture_hf_hub_id: Optional[str],
        is_peft: bool = False,
    ) -> LocalModelEntity:
        """Creates hugging face model

        Args:
            name (str): Name of the model to be created
            hf_hub_id: Id of the hugging face model to use
            hf_token: hugging face token to use to access the model
            key (Optional[str]): Unique key for the model
            if_peft: Optional[bool]: Whether it's a peft model or not
            architecture_hf_hub_id: Optional[str]: Hugging face id of the base model. This
                is required only in case of peft models.

        Returns:
            LocalModelEntity: LocalModelEntity object
        """
        return local_model.LocalModel.create_hf_model(
            request=self._state.request,
            name=name,
            hf_hub_id=hf_hub_id,
            hf_token=hf_token,
            architecture_hf_hub_id=architecture_hf_hub_id,
            is_peft=is_peft,
            key=key,
        )

    def get_model(self, key: str) -> Union[LocalModelEntity, RemoteModelEntity, None]:
        return self._state.get_model(key)

    def create_dataset(
        self,
        file_path,
        key: Optional[str] = None,
        name: Optional[str] = None,
        test_file_path: Optional[str] = None,
    ):
        return Dataset(
            request=self._state.request,
            name=name,
            key=key,
            file_path=file_path,
            test_file_path=test_file_path,
        )

    def create_hf_dataset(
        self,
        name: str,
        hf_id: str,
        hf_token: str,
        key: Optional[str],
    ) -> HFDatasetEntity:
        """_summary_

        Args:
            name (str): Name of the dataset
            hf_id (str): Dataset id from huggingface
            hf_token (str): Dataset token from huggingface. Please provide the token
                that has access to the dataset
            key (Optional[str]): Unique key for the dataset

        Returns:
            HFDatasetEntity: HFDatasetEntity object
        """
        return HFDataset.create_dataset(
            request=self._state.request, name=name, hf_id=hf_id, hf_token=hf_token, key=key
        )
