use ctr256::ctr;
use ige256::{ige_encrypt, ige_decrypt};
use pyo3::{prelude::*, types::PyBytes};
mod aes256;
mod ige256;
mod ctr256;

#[pyfunction]
fn ige256_encrypt<'a>(py: Python<'a>, data: &[u8], key: &[u8], iv: &[u8]) -> PyResult<&'a PyBytes> {
    let result = ige_encrypt(data, data.len(), key, iv);
    Ok(PyBytes::new(py, &result))
}

#[pyfunction]
fn ige256_decrypt<'a>(py: Python<'a>, data: &[u8], key: &[u8], iv: &[u8]) -> PyResult<&'a PyBytes> {
    let result = ige_decrypt(data, data.len(), key, iv);
    Ok(PyBytes::new(py, &result))
}

#[pyfunction]
fn ctr256_encrypt<'a>(py: Python<'a>, data: &[u8], key: &[u8], iv: &[u8], state: &[u8]) -> PyResult<&'a PyBytes>{
    let result = ctr(data, data.len(), key, iv, state);
    Ok(PyBytes::new(py, &result))
}

#[pyfunction]
fn ctr256_decrypt<'a>(py: Python<'a>, data: &[u8], key: &[u8], iv: &[u8], state: &[u8]) -> PyResult<&'a PyBytes>{
    let result = ctr(data, data.len(), key, iv, state);
    Ok(PyBytes::new(py, &result))
}

/// A Python module implemented in Rust.
#[pymodule]
fn hydrocrypto(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(ige256_encrypt, m)?)?;
    m.add_function(wrap_pyfunction!(ige256_decrypt, m)?)?;
    m.add_function(wrap_pyfunction!(ctr256_encrypt, m)?)?;
    m.add_function(wrap_pyfunction!(ctr256_decrypt, m)?)?;
    Ok(())
}
