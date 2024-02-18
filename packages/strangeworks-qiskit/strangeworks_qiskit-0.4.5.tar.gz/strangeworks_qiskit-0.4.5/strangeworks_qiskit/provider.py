"""provider.py."""
import logging
from typing import List, Optional

import strangeworks
from qiskit import Aer
from qiskit.providers import ProviderV1 as Provider
from qiskit.providers.models import BackendConfiguration
from qiskit.providers.providerutils import filter_backends
from strangeworks.sw_client import SWClient as SDKClient

from strangeworks_qiskit._runtime_client import RuntimeClient
from strangeworks_qiskit.backends import product_resolution
from strangeworks_qiskit.backends.ibm import IBMQSimulator
from strangeworks_qiskit.platform import backends as workspace_backends
from strangeworks_qiskit.platform.backends import Registration
from strangeworks_qiskit.runtimes import StrangeworksRuntimeService


class StrangeworksProvider(Provider):
    """The Strangeworks Provider allows access to Strangeworks backends and runtime
    wrappers for the Qiskit IBMQ Runtime services"""

    def __init__(
        self,
        client: Optional[SDKClient] = None,
    ):
        """Initialize StrangeworksProvider instance."""

        sdk_client = client or strangeworks.client
        self.sdk_client: SDKClient = sdk_client

        self._runtime = StrangeworksRuntimeService(
            provider=self, runtime_client=RuntimeClient(sdk_client)
        )
        self._backends = None

    def backends(self, name=None, filters=None, **kwargs):
        resources = self.sdk_client.resources()
        product_slugs = list(set(map(lambda x: x.product.slug, resources)))
        if not self._backends:
            self._backends = self._discover_backends(product_slugs=product_slugs)

        backends = self._backends
        if name:
            backends = [b for b in backends if b.name() == name]

        return filter_backends(backends, filters, **kwargs)

    def _discover_backends(
        self,
        product_slugs: Optional[List[str]] = None,
    ):
        backends = []
        platform_backends = workspace_backends.get(
            self.sdk_client.get_sdk_api(),
            statuses=["ONLINE"],
            product_slugs=product_slugs,
        )
        for qiskit_backend in platform_backends:
            backend_registration: Registration = qiskit_backend.get_registration()
            if not backend_registration or not backend_registration.data:
                logging.debug(
                    f"skipping {qiskit_backend.name} due to missing configuration."
                )
                continue

            cls = product_resolution(
                qiskit_backend.product.slug,
                qiskit_backend.get_config(),
            )
            if not cls:
                logging.debug(
                    f"unable to determine class type for {qiskit_backend.name}"
                )
                continue

            try:
                conf = BackendConfiguration.from_dict(qiskit_backend.get_config())
                b = cls(
                    conf,
                    self,
                    qiskit_backend.name,
                    self.sdk_client,
                    True,
                    None,
                    sw_product_info=qiskit_backend.product,
                    slug=qiskit_backend.slug,
                )

                backends.append(b)
            except (TypeError, AttributeError, KeyError) as e:
                logging.debug(
                    (
                        f"error retrieving configuration info for backend "
                        f"{qiskit_backend.name}: {e}"
                    )
                )
        # we also support all of the aer backends!
        for b in Aer.backends():
            backends.append(
                IBMQSimulator(
                    b.configuration(), self, b.name(), self.sdk_client, False, {}, b
                )
            )

        return backends

    @property
    def runtime(self) -> StrangeworksRuntimeService:
        """Return the runtime service.
        Returns:
            The runtime service instance.
        Raises:
            IBMQNotAuthorizedError: If the account is not authorized to use the service.
        """
        if self._runtime:
            return self._runtime
        else:
            raise Exception("You are not authorized to use the runtime service.")


def get_backend(name=None, **kwargs):
    sw = StrangeworksProvider()
    return sw.get_backend(name, **kwargs)
