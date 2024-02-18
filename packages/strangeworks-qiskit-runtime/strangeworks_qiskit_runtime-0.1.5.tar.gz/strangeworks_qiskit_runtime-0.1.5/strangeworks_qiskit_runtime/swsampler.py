# This code is part of Qiskit.
#
# (C) Copyright IBM 2022.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""Sampler primitive."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Sequence, Union

from qiskit.circuit import QuantumCircuit
from qiskit_ibm_runtime import Sampler
from qiskit_ibm_runtime.constants import DEFAULT_DECODERS
from qiskit_ibm_runtime.ibm_backend import IBMBackend

# TODO import _circuit_key from terra once 0.23 released
from qiskit_ibm_runtime.options import Options
from qiskit_ibm_runtime.runtime_job import RuntimeJob

# pylint: disable=unused-import,cyclic-import
from qiskit_ibm_runtime.session import Session

logger = logging.getLogger(__name__)


class StrangeworksSampler(Sampler):
    """Class for interacting with Qiskit Runtime Sampler primitive service.

    Qiskit Runtime Sampler primitive service calculates probabilities or
    quasi-probabilities
    of bitstrings from quantum circuits.

    The :meth:`run` method can be used to submit circuits and parameters to the Sampler
    primitive.

    You are encouraged to use :class:`~qiskit_ibm_runtime.Session` to open a session,
    during which you can invoke one or more primitive programs. Jobs submitted within a
    session
    are prioritized by the scheduler, and data is cached for efficiency.

    Example::

        from qiskit.test.reference_circuits import ReferenceCircuits
        from qiskit_ibm_runtime import QiskitRuntimeService, Session, Sampler

        service = QiskitRuntimeService(channel="ibm_cloud")
        bell = ReferenceCircuits.bell()

        with Session(service, backend="ibmq_qasm_simulator") as session:
            sampler = Sampler(session=session)

            job = sampler.run(bell, shots=1024)
            print(f"Job ID: {job.job_id()}")
            print(f"Job result: {job.result()}")
            # Close the session only if all jobs are finished
            # and you don't need to run more in the session.
            session.close()
    """

    _PROGRAM_ID = "sampler"

    def __init__(
        self,
        session: Optional[Union[Session, str, IBMBackend]] = None,
        options: Optional[Union[Dict, Options]] = None,
    ):
        """Initializes the StrangeworksSampler primitive."""

        super().__init__(session=session, options=options)

    def _run(  # pylint: disable=arguments-differ
        self,
        circuits: Sequence[QuantumCircuit],
        parameter_values: Sequence[Sequence[float]],
        **kwargs: Any,
    ) -> RuntimeJob:
        """Submit a request to the sampler primitive program.

        Args:
            circuits: A (parameterized) :class:`~qiskit.circuit.QuantumCircuit` or
                a list of (parameterized) :class:`~qiskit.circuit.QuantumCircuit`.
            parameter_values: An optional list of concrete parameters to be bound.
            **kwargs: Individual options to overwrite the default primitive options.
                These include the runtime options in
                :class:`qiskit_ibm_runtime.RuntimeOptions`.

        Returns:
            Submitted job.
        """
        inputs = {
            "circuits": circuits,
            "parameters": [circ.parameters for circ in circuits],
            "circuit_indices": list(range(len(circuits))),
            "parameter_values": parameter_values,
        }
        combined = Options._merge_options(self._options, kwargs.get("_user_kwargs", {}))

        if self._session.backend():
            inputs_new, options = self._session.service.backend_options(
                self._session.backend(),
                combined=combined,
            )
            inputs.update(inputs_new)
        else:
            combined["optimization_level"] = Options._DEFAULT_OPTIMIZATION_LEVEL
            combined["resilience_level"] = Options._DEFAULT_RESILIENCE_LEVEL
            options = None

        return self._session.run(
            program_id=self._PROGRAM_ID,
            inputs=inputs,
            options=options,
            callback=combined.get("environment", {}).get("callback", None),
            result_decoder=DEFAULT_DECODERS.get(self._PROGRAM_ID),
        )
