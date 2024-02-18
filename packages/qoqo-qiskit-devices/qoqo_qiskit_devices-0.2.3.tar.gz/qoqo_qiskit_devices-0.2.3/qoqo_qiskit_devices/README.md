<img src="../qoqo_Logo_vertical_color.png" alt="qoqo logo" width="300" />

# qoqo_qiskit_devices

Qiskit devices interface for the qoqo quantum toolkit by [HQS Quantum Simulations](https://quantumsimulations.de).

In order to make the update a device instance with Qiskit's information possible, the user has to run the following code before using this package:
```python
from qiskit_ibm_provider import IBMProvider

IBMProvider.save_account(token=MY_API_TOKEN)
```
Where `MY_API_TOKEN` is the API key that can be found in the account settings of the IBM Quantum website after registration.

### Installation

We provide pre-built binaries for linux, macos and windows on x86_64 hardware and macos on arm64. Simply install the pre-built wheels with

```shell
pip install qoqo-qiskit-devices
```

## General

Qiskit is under the Apache-2.0 license ( see https://github.com/Qiskit/qiskit/blob/master/LICENSE.txt ).

qoqo_qiskit_devices itself is also provided under the Apache-2.0 license.

## Testing

This software is still in the beta stage. Functions and documentation are not yet complete and breaking changes can occur.

If you find unexpected behaviour please open a github issue. You can also run the pytests in qoqo_qiskit_devices/python_tests/ locally.