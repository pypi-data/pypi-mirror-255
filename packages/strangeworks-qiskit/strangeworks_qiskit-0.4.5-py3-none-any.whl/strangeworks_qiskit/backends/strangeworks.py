"""strangeworks.py."""
import copy
import warnings
from typing import Any, Dict, Optional

from qiskit import assemble
from qiskit.providers import BackendV1 as Backend
from qiskit.providers.models.backendproperties import BackendProperties
from qiskit.providers.models.backendstatus import BackendStatus
from qiskit.qobj import PulseQobj, QasmQobj
from strangeworks.sw_client import SWClient as SDKClient
from strangeworks_core.errors.error import StrangeworksError

from strangeworks_qiskit.jobs.job import StrangeworksJob
from strangeworks_qiskit.platform.backends import get_status


class StrangeworksBackend(Backend):
    """Strangeworks Backend class."""

    def __init__(
        self,
        configuration,
        provider,
        name: str,
        client: SDKClient,
        remote: bool,
        slug: Optional[str] = None,
        sw_product_info=None,
        sw_properties=None,
        account_details=None,
        **fields,
    ):
        """Initialize StrangeworksBackend object."""
        if remote and not slug:
            raise StrangeworksError(message="all remote backends must have a slug.")

        super().__init__(configuration, provider=provider, **fields)
        self._name = name
        self.slug = slug
        self._client: SDKClient = client
        self._remote = remote
        self.sw_product_info = sw_product_info
        self.sw_properties = sw_properties
        self.account_details = account_details

    def run(self, circuits, **kwargs):
        """Run circuit request on backend."""
        # these types require assembly before being able to send to the cloud
        if not isinstance(circuits, (QasmQobj, PulseQobj)):
            circuits = assemble(circuits, self, **self.__get_run_config(**kwargs))

        job = StrangeworksJob(
            backend=self,
            circuit=circuits,
            remote=self._remote,
            sdk_client=self._client,
        )
        job.submit()
        return job

    def __get_run_config(self, **kwargs: Any) -> Dict:
        """Return the consolidated runtime configuration."""
        run_config_dict = copy.copy(self.options.__dict__)
        for key, val in kwargs.items():
            if val:
                run_config_dict[key] = val
                if (
                    key not in self.options.__dict__
                    and not self.configuration().simulator
                ):
                    warnings.warn(
                        (
                            f"{key} is not available in backend options and may be "
                            "ignored by this backend"
                        ),
                        stacklevel=4,
                    )
        return run_config_dict

    def name(self):
        """Get backend name."""
        return self._name

    def __repr__(self):
        return self.name()

    def __str__(self):
        return self.name()

    def status(self):
        """Retrieve backend status."""
        status: Dict[str, Any] = get_status(
            self._client.get_sdk_api(),
            self.slug,
        )
        return BackendStatus.from_dict(status)

    def properties(self):
        """Return properties of backend."""
        return (
            BackendProperties.from_dict(self.sw_properties)
            if self.sw_properties
            else None
        )

    def is_remote(self):
        return self._remote

    def product_slug(self):
        return self.sw_product_info.slug if self.sw_product_info else None
