"""Strangeworks runtime job."""

import logging
import time
from typing import Any, Dict, List, Optional, Sequence, Type

import strangeworks
from qiskit.providers.jobstatus import JOB_FINAL_STATES, JobStatus
from qiskit_ibm_runtime.constants import DEFAULT_DECODERS
from qiskit_ibm_runtime.program.result_decoder import ResultDecoder

logger = logging.getLogger(__name__)


class Backend:
    """Backend Object"""

    def __init__(self, name):
        self.name = name


class StrangeworksRuntimeJob:
    """Strangeworks runtime program execution."""

    def __init__(
        self,
        job_slug: str,
        service: Optional[Any] = None,
        backend: Optional[str] = None,
        params: Optional[Dict] = None,
        session_id: Optional[str] = None,
        tags: Optional[List] = None,
    ) -> None:
        """RuntimeJob constructor.

        Args:
            job_slug: Job slug.
            backend: The backend instance used to run this job.
            params: Job parameters.
            session_id: Job ID of the first job in a runtime session.
            tags: Tags assigned to the job.
        """

        self._job_slug = job_slug
        self.service = service
        self.rsc = service.rsc

        sw_job = strangeworks.jobs(slug=job_slug)[0]
        files = sw_job.files
        results_file = None
        for f in files:
            if f.file_name == "input_data.json":
                input_file = strangeworks.download_job_files([f.url])[0]
            if f.file_name == "results.json":
                results_file = strangeworks.download_job_files([f.url])[0]

        self._job_id = sw_job.external_identifier
        self.channel = input_file["channel"]
        self._backend = Backend(name=backend or input_file["backend"])
        self._program_id = input_file["program_id"]
        self._results: Optional[Any] = results_file
        self._interim_results: Optional[Any] = None
        self._params = params or {}
        self._status = sw_job.status
        self._reason: Optional[str] = None
        self._error_message: Optional[str] = None
        self._final_interim_results = False
        self._session_id = session_id or input_file["ibm_data"]["session_id"]
        self._tags = tags

        decoder = DEFAULT_DECODERS.get(self._program_id, None) or ResultDecoder
        if isinstance(decoder, Sequence):
            self._interim_result_decoder, self._final_result_decoder = decoder
        else:
            self._interim_result_decoder = self._final_result_decoder = decoder

    def interim_results(self, decoder: Optional[Type[ResultDecoder]] = None) -> Any:
        """Return the interim results of the job.

        Args:
            decoder: A :class:`ResultDecoder` subclass used to decode interim results.

        Returns:
            Runtime job interim results.

        Raises:
            RuntimeJobFailureError: If the job failed.
        """
        if not self._final_interim_results:
            _decoder = decoder or self._interim_result_decoder
            interim_results_raw = self._api_client.job_interim_results(
                job_id=self.job_id()
            )
            self._interim_results = _decoder.decode(interim_results_raw)
            if self.status() in JOB_FINAL_STATES:
                self._final_interim_results = True
        return self._interim_results

    def result(  # pylint: disable=arguments-differ
        self,
        timeout: Optional[float] = None,
        decoder: Optional[Type[ResultDecoder]] = None,
    ) -> Any:
        """Return the results of the job.

        Args:
            timeout: Number of seconds to wait for job.
            decoder: A :class:`ResultDecoder` subclass used to decode job results.

        Returns:
            Runtime job result.

        Raises:
            RuntimeJobFailureError: If the job failed.
            RuntimeJobMaxTimeoutError: If the job does not complete within given
            timeout.
        """
        if self._results is None:

            while self.status() not in {
                "COMPLETED",
                "FAILED",
                "CANCELLED",
            }:
                time.sleep(2.5)

            sw_job = strangeworks.jobs(slug=self.job_slug)[0]
            files = sw_job.files
            raw_results = None
            for f in files:
                if f.file_name == "job_results.json":
                    raw_results = strangeworks.download_job_files([f.url])[0]

            self._results = self._final_result_decoder.decode(raw_results)

        return self._results

    def cancel(self) -> None:
        """Cancel the job.

        Raises:
            RuntimeInvalidStateError: If the job is in a state that cannot be cancelled.
            IBMRuntimeError: If unable to cancel job.
        """
        if self._status != "COMPLETED":
            payload = {
                "runtime": True,
                "channel": self.channel,
                "job_slug": self._job_slug,
            }
            response = strangeworks.execute(self.rsc, payload, "runtime_cancel")
            status = response.get("status", None)
            if status is None:
                return response
            self._status = status
        return self._status

    def status(self) -> JobStatus:
        """Return the status of the job.

        Returns:
            Status of this job.
        """
        if self._status != "COMPLETED":
            payload = {
                "runtime": True,
                "channel": self.channel,
                "job_slug": self._job_slug,
            }
            response = strangeworks.execute(self.rsc, payload, "runtime_status")
            self._status = response["status"]
        return self._status

    def error_message(self) -> Optional[str]:
        """Returns the reason if the job failed.

        Returns:
            Error message string or ``None``.
        """
        self._set_status_and_error_message()
        return self._error_message

    @property
    def job_slug(self) -> str:
        """job_slug.

        Returns:
            Job slug of strangeworks job.
        """
        return self._job_slug

    def job_id(self) -> str:
        """Return a unique id identifying the job."""
        return self._job_id

    def backend(self) -> str:
        """backend.

        Returns:
            Backend where job was run job.
        """
        return self._backend

    @property
    def session_id(self) -> str:
        """Session ID.

        Returns:
            Job ID of the first job in a runtime session.
        """
        return self._session_id

    @property
    def tags(self) -> List:
        """Job tags.

        Returns:
            Tags assigned to the job that can be used for filtering.
        """
        return self._tags
