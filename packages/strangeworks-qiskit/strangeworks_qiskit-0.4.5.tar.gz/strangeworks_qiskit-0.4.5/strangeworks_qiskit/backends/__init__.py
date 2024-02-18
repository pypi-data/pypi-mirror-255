"""__init__.py."""
from typing import Any, Dict

from strangeworks_qiskit.backends._utils import get_provider_and_account
from strangeworks_qiskit.backends.aws import AwsSimulator, GeneralAWSBackend
from strangeworks_qiskit.backends.honeywell import HoneywellBackend
from strangeworks_qiskit.backends.ibm import IBMQBackend, IBMQSimulator
from strangeworks_qiskit.backends.ionq import IonqBackend
from strangeworks_qiskit.backends.rigetti import RigettiBackend
from strangeworks_qiskit.backends.strangeworks import StrangeworksBackend


def product_resolution(product_slug: str, cfg: Dict[str, Any]):
    """Return Backend class corresponding to the product."""
    # TODO: Only works for ibm-quantum right now. Need to expand to
    # other products.
    simulator = cfg.get("simulator", False)
    if product_slug == "ibm-quantum":
        return IBMQSimulator if simulator else IBMQBackend

    return None
