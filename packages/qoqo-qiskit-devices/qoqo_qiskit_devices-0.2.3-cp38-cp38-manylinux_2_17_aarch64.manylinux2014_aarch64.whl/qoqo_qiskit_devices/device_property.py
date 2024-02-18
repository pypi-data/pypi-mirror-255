"""Device information-gathering routines."""
# Copyright © 2023 HQS Quantum Simulations GmbH. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License
# is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied. See the License for the specific language governing permissions and limitations under
# the License.

from qoqo import noise_models
from struqture_py import spins

from qiskit_ibm_provider import IBMProvider

from .mocked_properties import MockedProperties

import types
import warnings


def _qiskit_gate_equivalent(gate: str) -> str:
    """Outputs qiskit equivalent of a Qoqo gate name.

    Args:
        gate (str): The name of the qoqo gate.

    Returns:
        str: The name of the equivalent Qiskit.
    """
    if gate == "PauliX":
        return "x"
    elif gate == "RotateZ":
        return "rz"
    elif gate == "SqrtPauliX":
        return "sx"
    elif gate == "CNOT":
        return "cx"
    elif gate == "Identity":
        return "id"


def set_qiskit_noise_information(
    device: types.ModuleType, get_mocked_information: bool = False
) -> types.ModuleType:
    """Sets a qoqo_qiskit_devices.ibm_devices instance noise info.

    Obtains the device info from qiskit's IBMProvider and performs the following updates:
        - adds damping
        - adds dephasing
        - sets single qubit gate times
        - sets two qubit gate times

    Args:
        device (ibm_devices): The qoqo_qiskit_devices instance to update.
        get_mocked_information (bool): Whether the returned information is mocked or not.

    Returns:
        ibm_devices: The input instance updated with qiskit's physical device info.
    """
    name = device.name()
    warn = False
    if get_mocked_information:
        properties = MockedProperties()
    else:
        properties = IBMProvider().get_backend(name).properties()

    for qubit in range(device.number_qubits()):
        damping = 1 / properties.t1(qubit=qubit)
        dephasing = 1 / properties.t2(qubit=qubit) - 1 / (
            2 * properties.t1(qubit=qubit)
        )
        if dephasing < 0:
            warn = True
        device.add_damping(qubit=qubit, damping=damping)
        device.add_dephasing(qubit=qubit, dephasing=dephasing)
        for gate in device.single_qubit_gate_names():
            qiskit_gate = _qiskit_gate_equivalent(gate)
            device.set_single_qubit_gate_time(
                gate=gate,
                qubit=qubit,
                gate_time=properties.gate_property(
                    gate=qiskit_gate, qubits=qubit, name="gate_length"
                )[0],
            )

    for edge in device.two_qubit_edges():
        for gate in device.two_qubit_gate_names():
            qiskit_gate = _qiskit_gate_equivalent(gate)
            device.set_two_qubit_gate_time(
                gate=gate,
                control=edge[0],
                target=edge[1],
                gate_time=properties.gate_property(
                    gate=qiskit_gate, qubits=[edge[0], edge[1]], name="gate_length"
                )[0],
            )
            device.set_two_qubit_gate_time(
                gate=gate,
                control=edge[1],
                target=edge[0],
                gate_time=properties.gate_property(
                    gate=qiskit_gate, qubits=[edge[1], edge[0]], name="gate_length"
                )[0],
            )

    if warn:
        warnings.warn(
            "IBM's calibration data resulted in negative dephasing value(s).",
            stacklevel=2,
        )

    return device


def get_decoherence_on_gate_model(
    device: types.ModuleType, get_mocked_information: bool = False
) -> noise_models.DecoherenceOnGateModel:
    """Gets the DecoherenceOnGateModel qoqo noise model of an IBM device.

    The paper that relates the gate fidelity to single-qubit damping + dephasing noise
    is https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.129.150504.
    The relevant equation is (12). As discussed below it, a heating noise (\\sigma^+)
    would contribute similarly as damping noise (\\sigma^-). By combining all three channels
    (damping, heating, dephasing), with proper front factors, one can also obtain a relation
    between depolarising noise and gate fidelity.

    Args:
        device (ibm_devices): The qoqo_qiskit_devices referencing the IBM device.
        get_mocked_information (bool): Whether the returned information is mocked or not.

    Returns:
        noise_models.DecoherenceOnGateModel: The qoqo noise model.
    """
    number_qubits = device.number_qubits()
    noise_model = noise_models.DecoherenceOnGateModel()
    if get_mocked_information:
        properties = MockedProperties()
    else:
        properties = IBMProvider().get_backend(device.name()).properties()
    warn = False
    operators = ["+", "-", "Z"]
    rate_factors = [0.5, 0.5, 0.25]

    for ii in range(number_qubits):
        for gate in ["SqrtPauliX", "PauliX"]:
            qiskit_gate = _qiskit_gate_equivalent(gate)
            gate_error = properties.gate_error(qiskit_gate, ii)
            gate_time = properties.gate_property(
                gate=qiskit_gate, qubits=ii, name="gate_length"
            )[0]
            depol_rate = gate_error / gate_time
            depol_rates = [factor * depol_rate for factor in rate_factors]

            lindblad_noise = spins.PlusMinusLindbladNoiseOperator()
            for op, rate in zip(operators, depol_rates):
                dp = spins.PlusMinusProduct().from_string(f"{ii}{op}")
                lindblad_noise.add_operator_product((dp, dp), rate)

            noise_model = noise_model.set_single_qubit_gate_error(
                gate, ii, lindblad_noise
            )

    for gate in device.two_qubit_gate_names():
        qiskit_gate = _qiskit_gate_equivalent(gate)
        for edge in device.two_qubit_edges():
            for ii, jj in [edge, tuple(reversed(edge))]:
                gate_error = properties.gate_error(qiskit_gate, (ii, jj))
                gate_time = properties.gate_property(
                    gate=qiskit_gate, qubits=[ii, jj], name="gate_length"
                )[0]
                depol_rate = (5 / 6) * gate_error / gate_time
                depol_rates = [factor * depol_rate for factor in rate_factors]

                lindblad_noise = spins.PlusMinusLindbladNoiseOperator()
                for kk in [ii, jj]:
                    for op, rate in zip(operators, depol_rates):
                        dp = spins.PlusMinusProduct().from_string(f"{kk}{op}")
                        lindblad_noise.add_operator_product((dp, dp), rate)

                noise_model = noise_model.set_two_qubit_gate_error(
                    gate, ii, jj, lindblad_noise
                )

    for ii in range(number_qubits):
        damping = 1 / properties.t1(qubit=ii)
        dephasing = 1 / properties.t2(qubit=ii) - 1 / (2 * properties.t1(qubit=ii))
        if dephasing < 0:
            warn = True

        lindblad_noise = spins.PlusMinusLindbladNoiseOperator()
        dp = spins.PlusMinusProduct().from_string(f"{ii}Z")
        lindblad_noise.add_operator_product((dp, dp), dephasing)
        noise_model = noise_model.set_single_qubit_gate_error(
            "Identity", ii, lindblad_noise
        )

        lindblad_noise = spins.PlusMinusLindbladNoiseOperator()
        dp = spins.PlusMinusProduct().from_string(f"{ii}+")
        lindblad_noise.add_operator_product((dp, dp), damping)
        noise_model = noise_model.set_single_qubit_gate_error(
            "Identity", ii, lindblad_noise
        )

    if warn:
        warnings.warn(
            "IBM's calibration data resulted in negative dephasing value(s).",
            stacklevel=2,
        )

    return noise_model
