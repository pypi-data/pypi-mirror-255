"""Strangeworks Qiskit Runtime Service."""

import logging
from typing import Any, Callable, Dict, List, Optional, Sequence, Type, Union

import strangeworks
from qiskit.providers.backend import BackendV1 as Backend
from qiskit_ibm_provider.utils.backend_decoder import configuration_from_server_data
from qiskit_ibm_runtime import ibm_backend
from qiskit_ibm_runtime.accounts import ChannelType
from qiskit_ibm_runtime.api.exceptions import RequestsApiError
from qiskit_ibm_runtime.exceptions import IBMRuntimeError, RuntimeProgramNotFound
from qiskit_ibm_runtime.ibm_backend import IBMBackend
from qiskit_ibm_runtime.program.result_decoder import ResultDecoder
from qiskit_ibm_runtime.runtime_options import RuntimeOptions
from qiskit_ibm_runtime.runtime_program import ParameterNamespace
from strangeworks.core.errors.error import StrangeworksError

from .runtime_client import StrangeworksRuntimeClient
from .sw_runtime_job import StrangeworksRuntimeJob

logger = logging.getLogger(__name__)

SERVICE_NAME = "sw_runtime"


class StrangeworksQiskitRuntimeService:
    """Class for interacting with the Qiskit Runtime service.

    Qiskit Runtime is a new architecture offered by IBM Quantum that
    streamlines computations requiring many iterations. These experiments will
    execute significantly faster within its improved hybrid quantum/classical
    process.

    A sample workflow of using the runtime service::

        import strangeworks
        from qiskit_ibm_runtime import Session, Options
        from strangeworks_qiskit_runtime import (
            StrangeworksQiskitRuntimeService,
            StrangeworksSampler,
            StrangeworksEstimator,
        )

        from qiskit.test.reference_circuits import ReferenceCircuits
        from qiskit.circuit.library import RealAmplitudes
        from qiskit.quantum_info import SparsePauliOp

        # Initialize account.
        strangeworks.authenticate(api_key="your-api-key-here")
        service = StrangeworksQiskitRuntimeService(channel="ibm-quantum")
        # service = StrangeworksQiskitRuntimeService(channel="ibm-cloud")

        # Set options, which can be overwritten at job level.
        options = Options(optimization_level=1)

        # Prepare inputs.
        bell = ReferenceCircuits.bell()
        psi = RealAmplitudes(num_qubits=2, reps=2)
        H1 = SparsePauliOp.from_list([("II", 1), ("IZ", 2), ("XI", 3)])
        theta = [0, 1, 1, 2, 3, 5]

        with Session(service=service, backend="ibmq_qasm_simulator") as session:
            # Submit a request to the Sampler primitive within the session.
            sampler = StrangeworksSampler(session=session, options=options)
            job = sampler.run(circuits=bell)
            print(f"Sampler results: {job.result()}")

            # Submit a request to the Estimator primitive within the session.
            estimator = StrangeworksEstimator(session=session, options=options)
            job = estimator.run(
                circuits=[psi], observables=[H1], parameter_values=[theta]
            )
            print(f"Estimator results: {job.result()}")
            # Close the session only if all jobs are finished
            # and you don't need to run more in the session.
            session.close()

    The example above uses the dedicated :class:`~qiskit_ibm_runtime.Sampler`
    and :class:`~qiskit_ibm_runtime.Estimator` classes. You can also
    use the :meth:`run` method directly to invoke a Qiskit Runtime program.

    If the program has any interim results, you can use the ``callback``
    parameter of the :meth:`run` method to stream the interim results.
    Alternatively, you can use the :meth:`RuntimeJob.stream_results` method to stream
    the results at a later time, but before the job finishes.

    The :meth:`run` method returns a
    :class:`RuntimeJob` object. You can use its
    methods to perform tasks like checking job status, getting job result, and
    canceling job.
    """

    def __init__(
        self,
        resource_slug: Optional[str] = None,
        channel: Optional[ChannelType] = None,
    ) -> None:
        """StrangeworksQiskitRuntimeService constructor

        Args:
            channel: Channel type. ``ibm_cloud`` or ``ibm_quantum``.
        Returns:
            An instance of StrangeworksQiskitRuntimeService.

        Raises:
            IBMInputValueError: If an input is invalid.
        """
        if resource_slug is not None:
            self.rsc = strangeworks.resources(slug=resource_slug)[0]
            if self.rsc:
                if self.rsc.product.slug == "ibm-quantum":
                    channel = "ibm_quantum"
                elif self.rsc.product.slug == "ibm-qiskit-runtime":
                    channel = "ibm_cloud"
            else:
                raise StrangeworksError(f"Invalid resource slug '{resource_slug}'.")
        elif channel is not None:
            if channel == "ibm_quantum":
                product_slug = "ibm-quantum"
            elif channel == "ibm_cloud":
                product_slug = "ibm-qiskit-runtime"
            else:
                raise StrangeworksError(
                    f"Invalid channel type '{channel}'. "
                    f"Valid channel types are 'ibm_quantum' and 'ibm_cloud'."
                )
            rsc_list = strangeworks.resources()
            for rr in range(len(rsc_list)):
                if rsc_list[rr].product.slug == product_slug:
                    self.rsc = rsc_list[rr]
                    break
        else:
            raise StrangeworksError("Must specify either a channel or reource slug.")
        self._api_client = StrangeworksRuntimeClient(channel=channel, rsc=self.rsc)
        self.channel = channel
        self._channel = channel

    def backend_options(
        self,
        name: Optional[str] = None,
        combined: Dict[str, Any] = None,
        min_num_qubits: Optional[int] = None,
        instance: Optional[str] = None,
        filters: Optional[Callable[[List["ibm_backend.IBMBackend"]], bool]] = None,
        **kwargs: Any,
    ) -> List["ibm_backend.IBMBackend"]:
        """Return all backends accessible via this account, subject to optional
        filtering.
        """

        payload = {
            "runtime": True,
            "channel": self.channel,
            "name": name,
            "combined": combined,
            "min_num_qubits": min_num_qubits,
            "instance": instance,
            "filters": filters,
            "kwargs": kwargs,
        }
        response = strangeworks.execute(self.rsc, payload, "runtime_backends")

        return response.get("inputs"), response.get("outputs")

    def backends(
        self,
    ) -> Backend:
        """Return a list of available backends."""
        if self._channel == "ibm_quantum":
            slug = "ibm-quantum"
        elif self._channel == "ibm_cloud":
            slug = "ibm-cloud"
        return strangeworks.backends(backend_type_slugs=[slug])

    def backend(
        self,
        name: str = None,
        instance: Optional[str] = None,
    ) -> Backend:
        """Return a single backend matching the specified filtering."""
        backends = self.backends()
        for b in backends:
            if b.name == name:
                backend = b

        # To-Do: Need to get backend configuration from service side
        payload = {
            "runtime": True,
            "channel": self.channel,
            "name": name,
        }
        raw_config = strangeworks.execute(self.rsc, payload, "runtime_backend_config")
        config = configuration_from_server_data(
            raw_config=raw_config, instance=instance
        )
        backend = IBMBackend(
            configuration=config,
            service=self,
            api_client=self._api_client,
            instance=instance,
        )
        return backend

    def run(
        self,
        program_id: str,
        inputs: Union[Dict, ParameterNamespace],
        options: Optional[Union[RuntimeOptions, Dict]] = None,
        callback: Optional[Callable] = None,
        result_decoder: Optional[
            Union[Type[ResultDecoder], Sequence[Type[ResultDecoder]]]
        ] = None,
        session_id: Optional[str] = None,
        start_session: Optional[bool] = False,
    ) -> StrangeworksRuntimeJob:
        """Execute the runtime program.

        Args:
            program_id: Program ID.
            inputs: Program input parameters. These input values are passed
                to the runtime program.
            options: Runtime options that control the execution environment.
                See :class:`RuntimeOptions` for all available options.

            callback: Callback function to be invoked for any interim results and final
            result.
                The callback function will receive 2 positional parameters:

                    1. Job ID
                    2. Job result.

            result_decoder: A :class:`ResultDecoder` subclass used to decode job
            results.
                If more than one decoder is specified, the first is used for interim
                results and
                the second final results. If not specified, a program-specific decoder
                or the default
                ``ResultDecoder`` is used.
            session_id: Job ID of the first job in a runtime session.
            start_session: Set to True to explicitly start a runtime session. Defaults
            to False.

        Returns:
            A ``StrangeworksJob`` instance representing the execution.

        Raises:
            IBMInputValueError: If input is invalid.
            RuntimeProgramNotFound: If the program cannot be found.
            IBMRuntimeError: An error occurred running the program.
        """

        qrt_options: RuntimeOptions = options
        if options is None:
            qrt_options = RuntimeOptions()
        elif isinstance(options, Dict):
            qrt_options = RuntimeOptions(**options)

        # If using params object, extract as dictionary
        if isinstance(inputs, ParameterNamespace):
            inputs.validate()
            inputs = vars(inputs)

        qrt_options.validate(channel=self.channel)

        try:
            response = self._api_client.program_run(
                program_id=program_id,
                backend_name=qrt_options.backend,
                params=inputs,
                image=qrt_options.image,
                log_level=qrt_options.log_level,
                session_id=session_id,
                job_tags=qrt_options.job_tags,
                max_execution_time=qrt_options.max_execution_time,
                start_session=start_session,
                session_time=qrt_options.session_time,
            )
        except RequestsApiError as ex:
            if ex.status_code == 404:
                raise RuntimeProgramNotFound(
                    f"Program not found: {ex.message}"
                ) from None
            raise IBMRuntimeError(f"Failed to run program: {ex}") from None

        # j = response.json()
        sw_job = StrangeworksRuntimeJob(
            job_slug=response["slug"],
            backend=response["jobData"]["backend"],
            service=self,
        )

        return sw_job

    def job(self, job_id: str) -> StrangeworksRuntimeJob:
        """Retrieve a runtime job.

        Args:
            job_id: Job ID.

        Returns:
            Runtime job retrieved.

        Raises:
            RuntimeJobNotFound: If the job doesn't exist.
            IBMRuntimeError: If the request failed.
        """
        response = self._api_client.job_get(job_id)
        return response

    def jobs(
        self,
    ) -> List[StrangeworksRuntimeJob]:
        """Retrieve all runtime jobs, subject to optional filtering for the product"""
        response = self._api_client.jobs_get()
        return response
