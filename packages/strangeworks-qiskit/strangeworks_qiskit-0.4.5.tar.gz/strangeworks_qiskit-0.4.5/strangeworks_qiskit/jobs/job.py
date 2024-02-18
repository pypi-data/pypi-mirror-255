"""job.py."""
from typing import Optional

import strangeworks
from qiskit.providers import JobStatus
from qiskit.providers import JobV1 as Job
from qiskit.providers.jobstatus import JOB_FINAL_STATES
from qiskit.result import Result
from strangeworks.sw_client import SWClient as SDKClient


class StrangeworksJob(Job):
    """Strangeworks implementation of a Qiskit Job."""

    def __init__(
        self, backend, circuit, remote, sdk_client: Optional[SDKClient] = None, **kwargs
    ):
        super().__init__(
            backend=backend,
            job_id=None,
            **kwargs,
        )
        self._remote: bool = remote
        self._circuit = circuit

        self._sdk_client = sdk_client or strangeworks.client

        if not self._remote:
            self._run_config = kwargs
        # we only need a resource, etc if the job is remote.
        if self._remote:
            # pick the first resource that matches backend product slug
            self._product_slug = backend.product_slug()
        self._result = None
        self._status: JobStatus = None

    def status(self):
        """Return job status.

        Jobs run on local simulators will have a status in terminal state once they
        return from submit.

        Jobs running remotely will make a remote call to retrieve job status until it
        reaches a terminal state.
        """
        if self._remote and self._status not in JOB_FINAL_STATES:
            sw_job = self._sdk_client.execute_post(
                product_slug=self._product_slug,
                payload={"slug": self._job_slug},
                endpoint="get_job_status",
            )
            remote_job_status = sw_job.get("remote_status") or sw_job.get(
                "remote_job_status"
            )
            self._status = JobStatus[remote_job_status]

        return self._status

    def result(self):
        """Obtain job result.

        Jobs run on local simulators will already have a terminal status and a result
        if they terminated with a status of DONE.

        If a job is running remotely, this method will block until it reaches a
        terminal state. If the job finishes with a status of DONE, its results will
        be retrieved.

        Job results stored as a part of the object once they are available.
        """
        if not self._result and self._remote:
            self.wait_for_final_state()
            if self._status == JobStatus.DONE:
                sw_job = self._sdk_client.execute_post(
                    product_slug=self._product_slug,
                    payload={"slug": self._job_slug},
                    endpoint="get_job_results",
                )
                files = sw_job.get("files")
                if files:
                    result_file = [
                        f.get("file").get("url")
                        for f in files
                        if f.get("file").get("file_name") == "job_results.json"
                    ]
                    results_json = self._sdk_client.download_job_files(result_file)
                    self._result = Result.from_dict(results_json[0])

        return self._result

    def submit(self, **kwargs):
        """Submit a job.

        The method will wait for a result for jobs running on local simulators. For jobs
        running remotely, the method will return once the job request has been accepted
        successfully.
        """
        if self._remote:
            return self._submit_remote(**kwargs)
        return self._submit_local(**kwargs)

    def cancel(self):
        """Cancel job.

        Only jobs that are running remotely can be cancelled.
        """
        # make sure we have _status set to something other than None to ensure job has
        # been submitted prior to this call.
        if self._remote and self._status:
            self._sdk_client.execute_post(
                product_slug=self._product_slug,
                payload={"slug": self._job_slug},
                endpoint="cancel_job",
            )

    def _submit_local(self, **kwargs):
        backend = self.backend()
        simulator = getattr(backend, "simulator", **self._run_config)
        if not simulator:
            self._status = JobStatus.ERROR
            return

        job = simulator.run(self._circuit, **self._run_config)
        self._result = job.result()
        self._status = JobStatus.ERROR
        if self._result:
            self._status = JobStatus.DONE
            self._job_id = job.job_id()

    def _submit_remote(self, **kwargs):
        circuit_type = type(self._circuit).__name__
        payload = {
            "qobj_dict": self._circuit.to_dict(),
            "circuit_type": circuit_type,
            "backend_name": self.backend().name(),
        }
        payload.update(kwargs)
        sw_job = self._sdk_client.execute_post(
            product_slug=self._product_slug,
            payload=payload,
            endpoint="create_job",
        )
        self._job_slug = sw_job.get("slug")
        self._job_id = sw_job.get("external_identifier")
        remote_job_status = sw_job.get("remote_status") or sw_job.get(
            "remote_job_status"
        )
        self._status = JobStatus[remote_job_status]
