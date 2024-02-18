// Copyright © 2023 HQS Quantum Simulations GmbH. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
// in compliance with the License. You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software distributed under the
// License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
// express or implied. See the License for the specific language governing permissions and
// limitations under the License.

#[allow(deprecated)]
mod ibm_belem;
pub use ibm_belem::*;

#[allow(deprecated)]
mod ibm_jakarta;
pub use ibm_jakarta::*;

mod ibm_lagos;
pub use ibm_lagos::*;
#[allow(deprecated)]
mod ibm_lima;
pub use ibm_lima::*;
#[allow(deprecated)]
mod ibm_manila;
pub use ibm_manila::*;

mod ibm_nairobi;
pub use ibm_nairobi::*;

mod ibm_perth;
pub use ibm_perth::*;
#[allow(deprecated)]
mod ibm_quito;
pub use ibm_quito::*;

use pyo3::{exceptions::PyValueError, prelude::*};

/// Instantiate a new IBMDevice instance based on the given IBM identifier.
///
/// Currently available identifiers:
///     - ibm_lagos
///     - ibm_nairobi
///     - ibm_perth
///     - ibmq_belem
///     - ibmq_jakarta
///     - ibmq_lima
///     - ibmq_manila
///     - ibmq_quito
///
/// Args:
///     identifier (str): The IBM identifier of the device.
///
/// Returns:
///     qoqo_qiskit_devices.devices: The new device instance.
#[pyfunction]
pub fn qoqo_qiskit_device_from_ibmq_identifier(identifier: &str) -> PyResult<Py<PyAny>> {
    Python::with_gil(|py| -> PyResult<Py<PyAny>> {
        match identifier {
            "ibm_lagos" => Ok(py
                .get_type::<IBMLagosDeviceWrapper>()
                .call0()
                .unwrap()
                .into()),
            "ibm_nairobi" => Ok(py
                .get_type::<IBMNairobiDeviceWrapper>()
                .call0()
                .unwrap()
                .into()),
            "ibm_perth" => Ok(py
                .get_type::<IBMPerthDeviceWrapper>()
                .call0()
                .unwrap()
                .into()),
            "ibmq_belem" => Ok(py
                .get_type::<IBMBelemDeviceWrapper>()
                .call0()
                .unwrap()
                .into()),
            "ibmq_jakarta" => Ok(py
                .get_type::<IBMJakartaDeviceWrapper>()
                .call0()
                .unwrap()
                .into()),
            "ibmq_lima" => Ok(py
                .get_type::<IBMLimaDeviceWrapper>()
                .call0()
                .unwrap()
                .into()),
            "ibmq_manila" => Ok(py
                .get_type::<IBMManilaDeviceWrapper>()
                .call0()
                .unwrap()
                .into()),
            "ibmq_quito" => Ok(py
                .get_type::<IBMQuitoDeviceWrapper>()
                .call0()
                .unwrap()
                .into()),
            _ => Err(PyValueError::new_err(
                "No device is related to the given identifier.".to_string(),
            )),
        }
    })
}

/// IBM Devices
#[pymodule]
pub fn ibm_devices(_py: Python, m: &PyModule) -> PyResult<()> {
    let _ = m.add_function(wrap_pyfunction!(
        qoqo_qiskit_device_from_ibmq_identifier,
        m
    )?);

    m.add_class::<IBMBelemDeviceWrapper>()?;
    m.add_class::<IBMJakartaDeviceWrapper>()?;
    m.add_class::<IBMLagosDeviceWrapper>()?;
    m.add_class::<IBMLimaDeviceWrapper>()?;
    m.add_class::<IBMManilaDeviceWrapper>()?;
    m.add_class::<IBMNairobiDeviceWrapper>()?;
    m.add_class::<IBMPerthDeviceWrapper>()?;
    m.add_class::<IBMQuitoDeviceWrapper>()?;
    Ok(())
}
