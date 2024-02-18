from typing import Dict, Type

from komodo_cli.backends.aws_backend import AWSBackend
from komodo_cli.backends.backend import Backend
from komodo_cli.backends.kubernetes_backend import KubernetesBackend
from komodo_cli.backends.local_backend import LocalBackend
from komodo_cli.types import Backend as BackendSchema
from komodo_cli.utils import APIClient


class BackendFactory:
    backend_types: Dict[str, Type[Backend]] = {
        "local": LocalBackend,
        "kubernetes": KubernetesBackend,
        "aws": AWSBackend,
    }

    @classmethod
    def get_backend(
        cls, backend_schema: BackendSchema, api_client: APIClient
    ) -> Backend:
        resources_dict = {r.name: r.config for r in backend_schema.resources}
        backend = cls.backend_types[backend_schema.type](
            backend_schema.name,
            api_client,
            backend_schema.config,
            resources_dict,
        )
        return backend
