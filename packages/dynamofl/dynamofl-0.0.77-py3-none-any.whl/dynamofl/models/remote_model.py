"""DynamoFL Remote Model"""
from ..entities.model import RemoteModelEntity
from ..models.model import Model
from ..Request import _Request

try:
    from typing import Optional
except ImportError:
    from typing_extensions import Optional


class RemoteModel(Model):
    """RemoteModel"""

    def __init__(
        self,
        request,
        name: str,
        key: str,
        model_id: str,
        config,
    ) -> None:
        self.request = request
        super().__init__(
            request=request,
            name=name,
            key=key,
            config=config,
            model_type="REMOTE",
            model_id=model_id,
        )

    @staticmethod
    def create_and_upload(
        request: _Request,
        name: str,
        key: str,
        api_provider: str,
        api_instance: str,
        endpoint: Optional[str],
    ):
        config = {
            "remoteModelApiProvider": api_provider,
            "remoteModelApiInstance": api_instance,
            "remoteModelEndpoint": endpoint,
        }

        model_id = Model.create_ml_model_and_get_id(
            request=request, name=name, key=key, model_type="REMOTE", config=config, size=None
        )

        return RemoteModel(
            request=request,
            name=name,
            key=key,
            config=config,
            model_id=model_id,
        )

    @staticmethod
    def create(
        request: _Request,
        name: str,
        key: str,
        config: object,
    ) -> RemoteModelEntity:
        model_id = Model.create_ml_model_and_get_id(
            request=request, name=name, key=key, model_type="REMOTE", config=config, size=None
        )
        return RemoteModelEntity(
            id=model_id,
            name=name,
            key=key,
            config=config,
            api_host=request.host,
        )

    @staticmethod
    def create_azure_openai_model(
        request: _Request,
        name: str,
        api_instance: str,
        api_key: str,
        api_version: str,
        model_endpoint: str,
        key: str,
    ) -> RemoteModelEntity:
        config = {
            "remoteModelApiProvider": "azure",
            "remoteModelApiInstance": api_instance,
            "remoteModelEndpoint": model_endpoint,
            "apiVersion": api_version,
            "apiKey": api_key,
        }
        return RemoteModel.create(request=request, name=name, key=key, config=config)

    @staticmethod
    def create_openai_model(
        request: _Request,
        name: str,
        api_instance: str,
        api_key: str,
        key: str,
    ) -> RemoteModelEntity:
        config = {
            "remoteModelApiProvider": "openai",
            "remoteModelApiInstance": api_instance,
            "apiKey": api_key,
        }
        return RemoteModel.create(request=request, name=name, key=key, config=config)

    @staticmethod
    def create_databricks_model(
        request: _Request,
        name: str,
        api_key: str,
        model_endpoint: str,
        key: str,
    ) -> RemoteModelEntity:
        config = {
            "remoteModelApiProvider": "databricks",
            "remoteModelEndpoint": model_endpoint,
            "apiKey": api_key,
        }
        return RemoteModel.create(request=request, name=name, key=key, config=config)
