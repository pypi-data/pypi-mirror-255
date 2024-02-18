"""status.py."""
from qiskit.providers import JobStatus


# _status_map = {
#     "initializing": Status.CREATED,
#     "creating": Status.CREATED,
#     "created": Status.CREATED,
#     "validating": Status.CREATED,
#     "validated": Status.CREATED,
#     "queued": Status.QUEUED,
#     "running": Status.RUNNING,
#     "completed": Status.COMPLETED,
#     "done": Status.COMPLETED,
#     "error": Status.FAILED,
#     "cancelled": Status.CANCELLED,
# }


def qiskit_status(status: str):
    _status = status.strip()
    try:
        return JobStatus(_status)
    except ValueError:
        _status = _status.lower()
        if _status in ["creating", "created"]:
            return JobStatus.INITIALIZING
        if _status in ["validated"]:
            return JobStatus.VALIDATING
        if _status in ["completed"]:
            return JobStatus.DONE

    return JobStatus.Error
