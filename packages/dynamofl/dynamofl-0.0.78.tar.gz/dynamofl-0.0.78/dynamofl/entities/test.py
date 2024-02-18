"""Test entity"""
import logging
from dataclasses import dataclass
from typing import Dict, List

from ..Helpers import URLUtils

logger = logging.getLogger(__name__)


@dataclass
class TestEntity:
    """Test entity"""

    id: str
    name: str
    model_key: str
    dataset_id: str
    test_type: str
    attacks: List[Dict]
    config: List[Dict]
    report_ui_url: str

    def __init__(  # pylint: disable=redefined-builtin
        self,
        id: str,
        name: str,
        model_key: str,
        dataset_id: str,
        test_type: str,
        attacks: List[Dict],
        config: List[Dict],
        api_host: str,
    ) -> None:
        self.id = id
        self.name = name
        self.model_key = model_key
        self.dataset_id = dataset_id
        self.test_type = test_type
        self.attacks = attacks
        self.config = config
        self.report_ui_url = URLUtils.get_test_report_ui_url(api_host, id)
        logger.info("Report UI URL: %s", self.report_ui_url)
