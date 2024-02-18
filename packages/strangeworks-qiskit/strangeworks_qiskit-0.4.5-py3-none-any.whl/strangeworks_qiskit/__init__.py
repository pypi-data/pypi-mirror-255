"""Strangeworks Qiskit SDK"""
import importlib.metadata
from typing import List, Optional

# TODO: is there a better way of initializing the SW Client?
import strangeworks

# TODO: is there a better way of defining these shortcuts?
from .jobs.job import StrangeworksJob
from .provider import StrangeworksProvider, get_backend


__version__ = importlib.metadata.version("strangeworks-qiskit")
