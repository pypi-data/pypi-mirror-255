"""backends.py"""
import json
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from strangeworks.core.client.platform import API, Operation
from strangeworks_core.types.backend import Backend


get_backends_query = Operation(
    query="""
    query backends(
        $product_slugs: [String!]
        $backend_type_slugs: [String!]
        $statuses: [BackendStatus!]
        $backend_tags: [String!]
    ) {
        backends(
            productSlugs: $product_slugs
            backendTypeSlugs: $backend_type_slugs
            backendStatuses: $statuses
            backendTags: $backend_tags
        ) {
            name
            slug
            remoteBackendId
            status
            backendRegistrations {
                data
                backendType {
                    slug
                    displayName
                }
            }
            product {
                slug
                productType
            }
        }
    }
"""
)


class Registration(BaseModel):
    """Backend Registration object.

    Includes the configuration data and type slug.
    """

    backendType: dict
    data: Optional[dict] = {}

    def __init__(self, *args, **kwargs):
        """Initialize object."""
        data_val = kwargs.pop("data")
        if data_val and isinstance(data_val, str):
            kwargs["data"] = json.loads(data_val)
        super().__init__(*args, **kwargs)

    @property
    def type_slug(self) -> Optional[str]:
        """Backend Type Slug."""
        return self.backendType.get("slug")

    def is_qiskit(self) -> bool:
        """Check if backend is of type qiskit."""
        return self.type_slug == "sw-qiskit"


class QiskitBackend(Backend):
    """Backend Class representing a Qiskit Backend."""

    registrations: Optional[List[Registration]] = Field(
        default=[], alias="backendRegistrations"
    )

    def get_registration(self) -> Optional[Registration]:
        """Get Qiskit-related backend info."""
        return next(reg for reg in self.registrations if reg.is_qiskit())

    def get_config(self) -> Optional[dict]:
        """Get backend configuration."""
        registration: Registration = self.get_registration()
        return registration.data if registration.data else self.data


def get(
    api: API,
    statuses: Optional[List[str]] = None,
    product_slugs: Optional[List[str]] = None,
) -> Optional[List[QiskitBackend]]:
    """Get backends from Strangeworks."""
    raw_results = api.execute(
        get_backends_query,
        statuses=statuses,
        product_slugs=product_slugs,
        backend_type_slugs=["sw-qiskit"],
    ).get("backends")
    retval: List[QiskitBackend] = [QiskitBackend(**x) for x in raw_results]
    return retval


_get_status_query = Operation(
    query="""
    query backend_status($backend_slug: String!) {
        backend(slug: $backend_slug) {
            status
            remoteStatus
            name
        }
    }
"""
)


def get_status(api: API, backend_slug: str) -> Dict[str, Any]:
    """Get status for backend identified by its slug."""
    sw_status = api.execute(op=_get_status_query, backend_slug=backend_slug).get(
        "backend"
    )
    return {
        "backend_name": sw_status.get("name"),
        "backend_version": "0.0.0",
        "operational": True,
        "pending_jobs": 0,
        "status_msg": sw_status.get("remoteStatus"),
    }
