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
from qiskit.opflow import PauliSumOp
from qiskit.quantum_info.operators.base_operator import BaseOperator
from qiskit_ibm_runtime import Estimator
from qiskit_ibm_runtime.constants import DEFAULT_DECODERS
from qiskit_ibm_runtime.ibm_backend import IBMBackend

# TODO import _circuit_key from terra once 0.23 released
from qiskit_ibm_runtime.options import Options
from qiskit_ibm_runtime.runtime_job import RuntimeJob

# pylint: disable=unused-import,cyclic-import
from qiskit_ibm_runtime.session import Session

logger = logging.getLogger(__name__)


class StrangeworksEstimator(Estimator):
    """Class for interacting with Qiskit Runtime Estimator primitive service.

    Qiskit Runtime Estimator primitive service estimates expectation values
    of quantum circuits and
    observables.

    The :meth:`run` can be used to submit circuits, observables, and parameters
    to the Estimator primitive.

    You are encouraged to use :class:`~qiskit_ibm_runtime.Session` to open a session,
    during which you can invoke one or more primitive programs.
    Jobs submitted within a session
    are prioritized by the scheduler, and data is cached for efficiency.

    Example::

        from qiskit.circuit.library import RealAmplitudes
        from qiskit.quantum_info import SparsePauliOp

        from qiskit_ibm_runtime import QiskitRuntimeService, Estimator

        service = QiskitRuntimeService(channel="ibm_cloud")

        psi1 = RealAmplitudes(num_qubits=2, reps=2)

        H1 = SparsePauliOp.from_list([("II", 1), ("IZ", 2), ("XI", 3)])
        H2 = SparsePauliOp.from_list([("IZ", 1)])
        H3 = SparsePauliOp.from_list([("ZI", 1), ("ZZ", 1)])

        with Session(service=service, backend="ibmq_qasm_simulator") as session:
            estimator = Estimator(session=session)

            theta1 = [0, 1, 1, 2, 3, 5]

            # calculate [ <psi1(theta1)|H1|psi1(theta1)> ]
            psi1_H1 = estimator.run(circuits=[psi1], observables=[H1],
            parameter_values=[theta1])
            print(psi1_H1.result())

            # calculate [ <psi1(theta1)|H2|psi1(theta1)>,
            <psi1(theta1)|H3|psi1(theta1)> ]
            psi1_H23 = estimator.run(
                circuits=[psi1, psi1],
                observables=[H2, H3],
                parameter_values=[theta1]*2
            )
            print(psi1_H23.result())
            # Close the session only if all jobs are finished
            # and you don't need to run more in the session
            session.close()
    """

    _PROGRAM_ID = "estimator"

    def __init__(
        self,
        session: Optional[Union[Session, str, IBMBackend]] = None,
        options: Optional[Union[Dict, Options]] = None,
    ):
        """Initializes the Strangeworksestimator primitive."""

        super().__init__(session=session, options=options)

    def _run(  # pylint: disable=arguments-differ
        self,
        circuits: Sequence[QuantumCircuit],
        observables: Sequence[BaseOperator | PauliSumOp],
        parameter_values: Sequence[Sequence[float]],
        **kwargs: Any,
    ) -> RuntimeJob:
        """Submit a request to the estimator primitive program.

        Args:
            circuits: a (parameterized) :class:`~qiskit.circuit.QuantumCircuit` or
                a list of (parameterized) :class:`~qiskit.circuit.QuantumCircuit`.

            observables: A list of observable objects.

            parameter_values: An optional list of concrete parameters to be bound.

            **kwargs: Individual options to overwrite the default primitive options.
                These include the runtime options in
                :class:`~qiskit_ibm_runtime.RuntimeOptions`.

        Returns:
            Submitted job
        """
        inputs = {
            "circuits": circuits,
            "circuit_indices": list(range(len(circuits))),
            "observables": observables,
            "observable_indices": list(range(len(observables))),
            "parameters": [circ.parameters for circ in circuits],
            "parameter_values": parameter_values,
        }
        combined = Options._merge_options(self._options, kwargs.get("_user_kwargs", {}))

        if self._session.backend():
            inputs_new, options = self._session.service.backend_options(
                self._session.backend(),
                combined=combined,
            )
        else:
            combined["optimization_level"] = Options._DEFAULT_OPTIMIZATION_LEVEL
            combined["resilience_level"] = Options._DEFAULT_RESILIENCE_LEVEL

        inputs.update(inputs_new)

        return self._session.run(
            program_id=self._PROGRAM_ID,
            inputs=inputs,
            options=options,
            callback=combined.get("environment", {}).get("callback", None),
            result_decoder=DEFAULT_DECODERS.get(self._PROGRAM_ID),
        )
